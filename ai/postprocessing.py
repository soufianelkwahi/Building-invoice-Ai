import re
from datetime import datetime


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return value


def normalize_amount(value) -> float:
    if isinstance(value, str):
        cleaned = re.sub(r"[^0-9.\-]", "", value)
        return float(cleaned) if cleaned else 0.0
    return float(value or 0.0)


def clean_extracted_data(data: dict) -> dict:
    data["invoice_date"] = normalize_date(data.get("invoice_date"))
    data["due_date"] = normalize_date(data.get("due_date"))
    data["total_amount"] = normalize_amount(data.get("total_amount"))
    data["subtotal"] = normalize_amount(data.get("subtotal", data.get("total_amount", 0)))
    data["tax_amount"] = normalize_amount(data.get("tax_amount")) if data.get("tax_amount") else None
    data["currency"] = data.get("currency", "USD").upper()
    data["invoice_number"] = str(data.get("invoice_number", "")).strip()
    data["vendor_name"] = str(data.get("vendor_name", "")).strip()

    line_items = data.get("line_items", [])
    for item in line_items:
        item["quantity"] = float(item.get("quantity", 1))
        item["unit_price"] = normalize_amount(item.get("unit_price"))
        item["amount"] = normalize_amount(item.get("amount"))

    return data
