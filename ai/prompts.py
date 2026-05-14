INVOICE_EXTRACTION_PROMPT = """You are an expert invoice data extractor.
Extract the following fields from the invoice text.
Return valid JSON with these keys:

- invoice_number: str
- vendor_name: str
- vendor_address: str | null
- customer_name: str
- invoice_date: str (YYYY-MM-DD)
- due_date: str (YYYY-MM-DD) | null
- subtotal: float
- tax_amount: float | null
- total_amount: float
- currency: str (default "USD")
- line_items: list[{"description": str, "quantity": float, "unit_price": float, "amount": float}]

Invoice text:
{text}
"""

INVOICE_CLASSIFICATION_PROMPT = """Classify the following invoice into a category.
Return JSON: {"category": str, "confidence": float, "reasoning": str}

Categories:
- utilities
- office_supplies
- software
- consulting
- travel
- meals
- rent
- maintenance
- shipping
- other

Invoice details:
Vendor: {vendor}
Total: {total}
Description: {text}
"""
