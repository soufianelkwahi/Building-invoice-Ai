from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .parser import parse_invoice_text


class ParseInvoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw invoice text content")


class ParseInvoiceResponse(BaseModel):
    invoice: dict


class HealthResponse(BaseModel):
    status: str


def create_app() -> FastAPI:
    app = FastAPI(title="Invoice AI API", version="0.2.0")

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/parse", response_model=ParseInvoiceResponse)
    def parse_invoice(payload: ParseInvoiceRequest) -> ParseInvoiceResponse:
        return ParseInvoiceResponse(invoice=parse_invoice_text(payload.text))

    return app


app = create_app()
