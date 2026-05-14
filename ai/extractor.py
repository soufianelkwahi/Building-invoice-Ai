import json
import re

from app.core.config import settings


class InvoiceExtractor:
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
            except ImportError:
                pass

    def extract_text_from_file(self, filepath: str) -> str:
        ext = filepath.rsplit(".", 1)[-1].lower()

        if ext == "pdf":
            return self._extract_from_pdf(filepath)
        elif ext in ("png", "jpg", "jpeg", "tiff"):
            return self._extract_from_image(filepath)
        elif ext == "txt":
            with open(filepath) as f:
                return f.read()
        return ""

    def _extract_from_pdf(self, filepath: str) -> str:
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except ImportError:
            return "[pdfplumber not installed]"

    def _extract_from_image(self, filepath: str) -> str:
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(filepath))
        except ImportError:
            return "[pytesseract not installed]"

    def extract_fields(self, text: str) -> dict:
        if self.client:
            return self._extract_with_llm(text)
        return self._extract_with_regex(text)

    def _extract_with_llm(self, text: str) -> dict:
        from ai.prompts import INVOICE_EXTRACTION_PROMPT

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract invoice data as JSON."},
                {"role": "user", "content": INVOICE_EXTRACTION_PROMPT.format(text=text[:8000])},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        return json.loads(response.choices[0].message.content)

    def _extract_with_regex(self, text: str) -> dict:
        patterns = {
            "invoice_number": r"(?:invoice\s*(?:#|no|number)[:\s]*)(\S+)",
            "vendor_name": r"(?:vendor|from|seller|supplier)[:\s]*(.+)$",
            "total_amount": r"(?:total|amount\s*due|balance\s*due)[:\s]*\$?([\d,]+\.\d{2})",
            "invoice_date": r"(?:date|invoice\s*date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        }

        result = {}
        text_lower = text.lower()
        for key, pattern in patterns.items():
            match = re.search(pattern, text_lower, re.MULTILINE | re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()

        total = result.get("total_amount", "0")
        result["total_amount"] = float(total.replace(",", "")) if isinstance(total, str) else 0.0
        result["currency"] = "USD"
        result["line_items"] = []
        return result
