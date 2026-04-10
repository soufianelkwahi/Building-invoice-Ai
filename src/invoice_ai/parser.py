from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any


@dataclass
class InvoiceData:
    invoice_number: str | None
    invoice_date: str | None
    due_date: str | None
    vendor_name: str | None
    customer_name: str | None
    subtotal: float | None
    tax: float | None
    total: float | None
    currency: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


INVOICE_NUMBER_PATTERNS = [
    r"(?:invoice\s*(?:number|#|no\.?))\s*[:\-]?\s*([A-Z0-9\-_/]+)",
    r"(?:facture\s*(?:number|#|no\.?))\s*[:\-]?\s*([A-Z0-9\-_/]+)",
]

DATE_PATTERNS = [
    r"(?:invoice\s*date|date)\s*[:\-]?\s*([0-3]?\d[/-][01]?\d[/-]\d{2,4})",
    r"(?:invoice\s*date|date)\s*[:\-]?\s*(\d{4}[/-][01]?\d[/-][0-3]?\d)",
]

DUE_DATE_PATTERNS = [
    r"(?:due\s*date|pay\s*by)\s*[:\-]?\s*([0-3]?\d[/-][01]?\d[/-]\d{2,4})",
    r"(?:due\s*date|pay\s*by)\s*[:\-]?\s*(\d{4}[/-][01]?\d[/-][0-3]?\d)",
]

MONEY_FIELDS = {
    "subtotal": [r"^\s*(?:subtotal|sub\s*total)\s*[:\-]?\s*([$€£]?\s?[\d,.]+)"],
    "tax": [r"^\s*(?:tax|vat|tva)\s*[:\-]?\s*([$€£]?\s?[\d,.]+)"],
    "total": [
        r"^\s*(?:total\s*due|grand\s*total)\s*[:\-]?\s*([$€£]?\s?[\d,.]+)",
        r"^\s*total\s*[:\-]?\s*([$€£]?\s?[\d,.]+)",
    ],
}

VENDOR_PATTERNS = [
    r"(?:from|vendor|supplier)\s*[:\-]?\s*([^\n]+)",
]

CUSTOMER_PATTERNS = [
    r"(?:bill\s*to|to|customer|client)\s*[:\-]?\s*([^\n]+)",
]


CURRENCY_BY_SYMBOL = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}


def _extract_first(patterns: list[str], text: str, flags: int = re.IGNORECASE | re.MULTILINE) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            value = match.group(1).strip()
            if value:
                return value
    return None


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None

    cleaned = value.replace(".", "/").replace("-", "/")
    formats = ["%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y"]
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def _to_float(money_text: str | None) -> float | None:
    if not money_text:
        return None
    numeric = re.sub(r"[^\d.,]", "", money_text)

    if "," in numeric and "." in numeric:
        numeric = numeric.replace(",", "")
    elif numeric.count(",") == 1 and numeric.count(".") == 0:
        numeric = numeric.replace(",", ".")
    else:
        numeric = numeric.replace(",", "")

    try:
        return float(numeric)
    except ValueError:
        return None


def _detect_currency(*values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        for symbol, code in CURRENCY_BY_SYMBOL.items():
            if symbol in value:
                return code
    return None


def parse_invoice_text(text: str) -> dict[str, Any]:
    """Parse invoice-like text and extract normalized structured fields."""
    invoice_number = _extract_first(INVOICE_NUMBER_PATTERNS, text)
    invoice_date_raw = _extract_first(DATE_PATTERNS, text)
    due_date_raw = _extract_first(DUE_DATE_PATTERNS, text)

    subtotal_raw = _extract_first(MONEY_FIELDS["subtotal"], text)
    tax_raw = _extract_first(MONEY_FIELDS["tax"], text)
    total_raw = _extract_first(MONEY_FIELDS["total"], text)

    vendor_name = _extract_first(VENDOR_PATTERNS, text)
    customer_name = _extract_first(CUSTOMER_PATTERNS, text)

    currency = _detect_currency(subtotal_raw, tax_raw, total_raw)

    data = InvoiceData(
        invoice_number=invoice_number,
        invoice_date=_normalize_date(invoice_date_raw),
        due_date=_normalize_date(due_date_raw),
        vendor_name=vendor_name,
        customer_name=customer_name,
        subtotal=_to_float(subtotal_raw),
        tax=_to_float(tax_raw),
        total=_to_float(total_raw),
        currency=currency,
    )

    return data.to_dict()
