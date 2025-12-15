"""
FastMCP server for client and invoice management.
"""

from datetime import datetime
from typing import Optional
from fastmcp import FastMCP
from pydantic import ValidationError

from src.database import (
    load_clients, save_clients, load_invoices, save_invoices,
    get_client_by_id, get_invoice_by_id
)
from src.models import Client, InvoiceItem, Invoice, DashboardStats

mcp = FastMCP(
    name="Client & Invoice Manager",
    instructions="A server for managing clients and invoices. Use these tools to add clients, search for clients, create invoices, view invoices, and see dashboard statistics."
)


@mcp.tool()
def add_client(
    name: str,
    email: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    company: Optional[str] = None
) -> dict:
    """
    Add a new client to the database.
    
    Args:
        name: Client's full name
        email: Client's email address
        phone: Client's phone number (optional)
        address: Client's address (optional)
        company: Client's company name (optional)
    
    Returns:
        The newly created client with ID
    """
    try:
        client = Client(
            name=name,
            email=email,
            phone=phone,
            address=address,
            company=company
        )
    except ValidationError as e:
        errors = []
        for err in e.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append(f"{field}: {err['msg']}")
        return {"success": False, "error": f"Validation failed: {'; '.join(errors)}"}
    
    data = load_clients()
    client_dict = client.model_dump()
    client_dict["id"] = data["next_id"]
    client_dict["created_at"] = datetime.now().isoformat()
    client_dict["updated_at"] = datetime.now().isoformat()
    
    data["clients"].append(client_dict)
    data["next_id"] += 1
    save_clients(data)
    
    return {"success": True, "client": client_dict}


@mcp.tool()
def search_clients(
    query: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None
) -> dict:
    """
    Search for clients by name, email, or company.
    
    Args:
        query: Search term to match against name (optional)
        email: Filter by email address (optional)
        company: Filter by company name (optional)
    
    Returns:
        List of matching clients
    """
    data = load_clients()
    clients = data["clients"]
    results = []
    
    for client in clients:
        match = True
        
        if query:
            if query.lower() not in client.get("name", "").lower():
                match = False
        
        if email:
            if email.lower() not in client.get("email", "").lower():
                match = False
        
        if company and client.get("company"):
            if company.lower() not in client["company"].lower():
                match = False
        elif company and not client.get("company"):
            match = False
        
        if match:
            results.append(client)
    
    return {"count": len(results), "clients": results}


@mcp.tool()
def get_client(client_id: int) -> dict:
    """
    Get a client by their ID.
    
    Args:
        client_id: The unique ID of the client
    
    Returns:
        The client details or an error message
    """
    client = get_client_by_id(client_id)
    if client:
        return {"success": True, "client": client}
    return {"success": False, "error": f"Client with ID {client_id} not found"}


@mcp.tool()
def list_all_clients() -> dict:
    """
    List all clients in the database.
    
    Returns:
        List of all clients with count
    """
    data = load_clients()
    return {"count": len(data["clients"]), "clients": data["clients"]}


@mcp.tool()
def create_invoice(
    client_id: int,
    items: list[dict],
    notes: Optional[str] = None,
    due_date: Optional[str] = None,
    status: str = "draft"
) -> dict:
    """
    Create a new invoice for a client.
    
    Args:
        client_id: The ID of the client to invoice
        items: List of invoice items, each with description, quantity, and unit_price
        notes: Additional notes for the invoice (optional)
        due_date: Due date in ISO format YYYY-MM-DD (optional)
        status: Invoice status: draft, sent, paid, overdue (default: draft)
    
    Returns:
        The newly created invoice with ID and total
    """
    client = get_client_by_id(client_id)
    if not client:
        return {"success": False, "error": f"Client with ID {client_id} not found"}
    
    valid_statuses = ["draft", "sent", "paid", "overdue"]
    if status.lower() not in valid_statuses:
        return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
    
    if not items:
        return {"success": False, "error": "At least one invoice item is required"}
    
    invoice_items = []
    for i, item in enumerate(items):
        required_fields = ["description", "quantity", "unit_price"]
        missing_fields = [f for f in required_fields if f not in item]
        if missing_fields:
            return {
                "success": False,
                "error": f"Item {i + 1} is missing required fields: {', '.join(missing_fields)}"
            }
        
        try:
            invoice_item = InvoiceItem(
                description=item["description"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            invoice_items.append(invoice_item)
        except ValidationError as e:
            errors = []
            for err in e.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                errors.append(f"{field}: {err['msg']}")
            return {
                "success": False,
                "error": f"Item {i + 1} validation failed: {'; '.join(errors)}"
            }
    
    total = sum(item.quantity * item.unit_price for item in invoice_items)
    
    data = load_invoices()
    invoice_dict = {
        "id": data["next_id"],
        "client_id": client_id,
        "client_name": client["name"],
        "items": [item.model_dump() for item in invoice_items],
        "status": status.lower(),
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "due_date": due_date,
        "total": total
    }
    
    data["invoices"].append(invoice_dict)
    data["next_id"] += 1
    save_invoices(data)
    
    return {"success": True, "invoice": invoice_dict}


@mcp.tool()
def get_invoice(invoice_id: int) -> dict:
    """
    Get an invoice by its ID.
    
    Args:
        invoice_id: The unique ID of the invoice
    
    Returns:
        The invoice details or an error message
    """
    invoice = get_invoice_by_id(invoice_id)
    if invoice:
        client = get_client_by_id(invoice["client_id"])
        return {
            "success": True,
            "invoice": invoice,
            "client": client
        }
    return {"success": False, "error": f"Invoice with ID {invoice_id} not found"}


@mcp.tool()
def list_invoices(
    client_id: Optional[int] = None,
    status: Optional[str] = None
) -> dict:
    """
    List invoices with optional filtering.
    
    Args:
        client_id: Filter by client ID (optional)
        status: Filter by status: draft, sent, paid, overdue (optional)
    
    Returns:
        List of matching invoices
    """
    data = load_invoices()
    invoices = data["invoices"]
    results = []
    
    for invoice in invoices:
        match = True
        
        if client_id is not None:
            if invoice.get("client_id") != client_id:
                match = False
        
        if status:
            if invoice.get("status", "").lower() != status.lower():
                match = False
        
        if match:
            results.append(invoice)
    
    total_amount = sum(inv.get("total", 0) for inv in results)
    
    return {
        "count": len(results),
        "total_amount": total_amount,
        "invoices": results
    }


@mcp.tool()
def update_invoice_status(invoice_id: int, status: str) -> dict:
    """
    Update the status of an invoice.
    
    Args:
        invoice_id: The ID of the invoice to update
        status: New status: draft, sent, paid, overdue
    
    Returns:
        The updated invoice or an error message
    """
    valid_statuses = ["draft", "sent", "paid", "overdue"]
    if status.lower() not in valid_statuses:
        return {"success": False, "error": f"Invalid status. Must be one of: {valid_statuses}"}
    
    data = load_invoices()
    for invoice in data["invoices"]:
        if invoice["id"] == invoice_id:
            invoice["status"] = status.lower()
            save_invoices(data)
            return {"success": True, "invoice": invoice}
    
    return {"success": False, "error": f"Invoice with ID {invoice_id} not found"}


@mcp.tool()
def dashboard() -> dict:
    """
    Get dashboard statistics showing an overview of clients and invoices.
    
    Returns:
        Statistics including total clients, invoices, revenue, and invoice breakdowns
    """
    clients_data = load_clients()
    invoices_data = load_invoices()
    
    invoices = invoices_data["invoices"]
    
    total_revenue = sum(inv.get("total", 0) for inv in invoices if inv.get("status") == "paid")
    pending_invoices = len([inv for inv in invoices if inv.get("status") in ["sent", "overdue"]])
    paid_invoices = len([inv for inv in invoices if inv.get("status") == "paid"])
    draft_invoices = len([inv for inv in invoices if inv.get("status") == "draft"])
    
    stats = DashboardStats(
        total_clients=len(clients_data["clients"]),
        total_invoices=len(invoices),
        total_revenue=total_revenue,
        pending_invoices=pending_invoices,
        paid_invoices=paid_invoices,
        draft_invoices=draft_invoices
    )
    
    recent_invoices = sorted(invoices, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    recent_clients = sorted(clients_data["clients"], key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    
    return {
        "statistics": stats.model_dump(),
        "recent_invoices": recent_invoices,
        "recent_clients": recent_clients
    }


if __name__ == "__main__":
    mcp.run()
