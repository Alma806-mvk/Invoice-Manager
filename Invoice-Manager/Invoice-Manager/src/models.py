"""
Pydantic models for clients and invoices.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Client(BaseModel):
    """Client data model."""
    id: Optional[int] = None
    name: str = Field(..., min_length=1, description="Client's full name")
    email: EmailStr = Field(..., description="Client's email address")
    phone: Optional[str] = Field(None, description="Client's phone number")
    address: Optional[str] = Field(None, description="Client's address")
    company: Optional[str] = Field(None, description="Client's company name")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class InvoiceItem(BaseModel):
    """Invoice line item model."""
    description: str = Field(..., min_length=1, description="Item description")
    quantity: float = Field(..., gt=0, description="Quantity of items")
    unit_price: float = Field(..., ge=0, description="Price per unit")
    
    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


class Invoice(BaseModel):
    """Invoice data model."""
    id: Optional[int] = None
    client_id: int = Field(..., description="ID of the client")
    items: list[InvoiceItem] = Field(default_factory=list, description="Invoice line items")
    status: str = Field(default="draft", description="Invoice status: draft, sent, paid, overdue")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: Optional[str] = None
    due_date: Optional[str] = None
    
    @property
    def total(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)


class DashboardStats(BaseModel):
    """Dashboard statistics model."""
    total_clients: int
    total_invoices: int
    total_revenue: float
    pending_invoices: int
    paid_invoices: int
    draft_invoices: int
