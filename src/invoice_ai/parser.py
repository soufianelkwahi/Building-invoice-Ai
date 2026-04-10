from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
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
    r"(?:invoice\s*date|issue\s*date|date)\s*[:\-]?\s*([0-3]?\d[/.\-][01]?\d[/.\-]\d{2,4})",
    r"(?:invoice\s*date|issue\s*date|date)\s*[:\-]?\s*(\d{4}[/.\-][01]?\d[/.\-][0-3]?\d)",
]

DUE_DATE_PATTERNS = [
    r"(?:due\s*date|pay\s*by)\s*[:\-]?\s*([0-3]?\d[/.\-][01]?\d[/.\-]\d{2,4})",
    r"(?:due\s*date|pay\s*by)\s*[:\-]?\s*(\d{4}[/.\-][01]?\d[/.\-][0-3]?\d)",
]

PAYMENT_TERMS_PATTERNS = [
    r"(?:payment\s*terms?|terms?)\s*[:\-]?\s*net\s*(\d{1,3})",
    r"\bnet\s*(\d{1,3})\b",
]

MONEY_VALUE = r"((?:USD|EUR|GBP|SAR|AED)?\s*[$€£]?\s?[\d.,]+\s?(?:USD|EUR|GBP|SAR|AED)?)"
MONEY_FIELDS = {
    "subtotal": [rf"^\s*(?:subtotal|sub\s*total)\s*[:\-]?\s*{MONEY_VALUE}"],
    "tax": [rf"^\s*(?:tax|vat|tva)\s*[:\-]?\s*{MONEY_VALUE}"],
    "total": [
        rf"^\s*(?:total\s*due|grand\s*total)\s*[:\-]?\s*{MONEY_VALUE}",
        rf"^\s*total\s*[:\-]?\s*{MONEY_VALUE}",
    ],
}

VENDOR_PATTERNS = [
    r"(?:from|vendor|supplier)\s*[:\-]?\s*([^\n]+)",
]

CUSTOMER_PATTERNS = [
    r"(?:bill\s*to|customer|client)\s*[:\-]?\s*([^\n]+)",
]


CURRENCY_BY_SYMBOL = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
}

CURRENCY_CODES = {"USD", "EUR", "GBP", "SAR", "AED"}


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
    if not numeric:
        return None

    if "," in numeric and "." in numeric:
        # support 1.234,56 and 1,234.56
        if numeric.rfind(",") > numeric.rfind("."):
            numeric = numeric.replace(".", "").replace(",", ".")
        else:
            numeric = numeric.replace(",", "")
    elif numeric.count(",") == 1 and numeric.count(".") == 0:
        numeric = numeric.replace(",", ".")
    else:
        numeric = numeric.replace(",", "")

    try:
        return float(numeric)
    except ValueError:
        return None


def _extract_payment_terms_days(text: str) -> int | None:
    value = _extract_first(PAYMENT_TERMS_PATTERNS, text)
    if not value:
        return None
    try:
        days = int(value)
    except ValueError:
        return None
    return days if 0 < days <= 365 else None


def _infer_due_date(invoice_date_iso: str | None, terms_days: int | None) -> str | None:
    if not invoice_date_iso or terms_days is None:
        return None
    try:
        invoice_date = datetime.strptime(invoice_date_iso, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (invoice_date + timedelta(days=terms_days)).isoformat()


def _detect_currency(text: str, *values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        for symbol, code in CURRENCY_BY_SYMBOL.items():
            if symbol in value:
                return code
        upper_value = value.upper()
        for code in CURRENCY_CODES:
            if code in upper_value:
                return code

    upper_text = text.upper()
    for code in CURRENCY_CODES:
        if re.search(rf"\b{code}\b", upper_text):
            return code
    return None


def _coalesce_total(subtotal: float | None, tax: float | None, total: float | None) -> float | None:
    if total is not None:
        return total
    if subtotal is not None and tax is not None:
        return round(subtotal + tax, 2)
    return total


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

    invoice_date = _normalize_date(invoice_date_raw)
    due_date = _normalize_date(due_date_raw)

    subtotal = _to_float(subtotal_raw)
    tax = _to_float(tax_raw)
    total = _coalesce_total(subtotal, tax, _to_float(total_raw))

    if due_date is None:
        due_date = _infer_due_date(invoice_date, _extract_payment_terms_days(text))

    currency = _detect_currency(text, subtotal_raw, tax_raw, total_raw)

    data = InvoiceData(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        vendor_name=vendor_name,
        customer_name=customer_name,
        subtotal=subtotal,
        tax=tax,
        total=total,
        currency=currency,
    )

    return data.to_dict()
