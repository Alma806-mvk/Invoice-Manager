# Client & Invoice Management MCP Server

## Overview
A Python MCP (Model Context Protocol) server built with FastMCP that manages clients and invoices. The server provides tools for:
- Adding and searching clients
- Creating and managing invoices
- Viewing dashboard statistics

## Server Configuration
- **Transport:** Streamable HTTP
- **Port:** 8000
- **Endpoint:** `/mcp`
- **Full URL:** `http://your-domain:8000/mcp`

## Project Structure
```
├── main.py              # Entry point for the MCP server
├── src/
│   ├── __init__.py      # Package initialization
│   ├── server.py        # FastMCP server with all tools
│   ├── database.py      # JSON file-based data persistence
│   └── models.py        # Pydantic data models
├── data/                # JSON data storage (auto-created)
│   ├── clients.json     # Client data
│   └── invoices.json    # Invoice data
└── pyproject.toml       # Python dependencies
```

## Available MCP Tools

### Client Management
- **add_client**: Add a new client with name, email, phone, address, company
- **search_clients**: Search clients by name, email, or company
- **get_client**: Get a specific client by ID
- **list_all_clients**: List all clients in the database

### Invoice Management
- **create_invoice**: Create an invoice for a client with line items
- **get_invoice**: Get a specific invoice by ID
- **list_invoices**: List invoices with optional filters (client_id, status)
- **update_invoice_status**: Update invoice status (draft, sent, paid, overdue)

### Dashboard
- **dashboard**: View statistics including total clients, invoices, revenue

## Running the Server
```bash
python main.py
```

The server runs on port 8000 with streamable-http transport.

## Data Storage
Data is stored in JSON files in the `data/` directory:
- `clients.json`: Client records with auto-incrementing IDs
- `invoices.json`: Invoice records with line items and totals

## Dependencies
- fastmcp: MCP server framework
- pydantic: Data validation
