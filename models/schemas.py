from datetime import datetime

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    amount: float = 0.0


class InvoiceCreate(BaseModel):
    invoice_number: str = ""
    vendor_name: str = ""
    vendor_address: str | None = None
    customer_name: str = ""
    invoice_date: str | None = None
    due_date: str | None = None
    subtotal: float = 0.0
    tax_amount: float | None = None
    total_amount: float = 0.0
    currency: str = "USD"
    category: str = "other"
    status: str = "pending"
    confidence_score: float = 0.0
    raw_text: str = ""
    file_path: str = ""
    line_items: list[LineItem] = []


class InvoiceUpdate(BaseModel):
    vendor_name: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    currency: str | None = None
    category: str | None = None
    status: str | None = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    vendor_name: str
    vendor_address: str | None
    customer_name: str
    invoice_date: str | None
    due_date: str | None
    subtotal: float
    tax_amount: float | None
    total_amount: float
    currency: str
    category: str
    status: str
    confidence_score: float
    file_path: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProcessingResult(BaseModel):
    invoice: InvoiceResponse
    category: str
    confidence: float
    processing_time_ms: float
