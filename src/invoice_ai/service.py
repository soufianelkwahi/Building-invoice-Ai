from __future__ import annotations

from typing import Any

from .models import InvoiceJob
from .parser import parse_invoice_text


KEY_FIELDS = ["invoice_number", "invoice_date", "vendor_name", "total", "currency"]


def estimate_confidence(parsed: dict[str, Any]) -> str:
    score = sum(1 for key in KEY_FIELDS if parsed.get(key) not in (None, ""))
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def process_invoice_text(text: str, source_type: str = "text") -> InvoiceJob:
    parsed = parse_invoice_text(text)
    confidence = estimate_confidence(parsed)
    return InvoiceJob(
        source_type=source_type,
        status="processed",
        raw_text=text,
        parsed_data=parsed,
        confidence=confidence,
    )
