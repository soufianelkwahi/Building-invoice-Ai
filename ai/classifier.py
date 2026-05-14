import json

from app.core.config import settings


class InvoiceClassifier:
    def __init__(self):
        self.client = None
        if settings.openrouter_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url=settings.openrouter_base_url,
                )
            except ImportError:
                pass

    def classify(self, vendor: str, total: float, text: str) -> dict:
        if self.client:
            return self._classify_with_llm(vendor, total, text)

        return self._classify_rule_based(vendor, total, text)

    def _classify_with_llm(self, vendor: str, total: float, text: str) -> dict:
        from ai.prompts import INVOICE_CLASSIFICATION_PROMPT

        response = self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {"role": "system", "content": "You are a classifier. Return ONLY valid JSON."},
                {
                    "role": "user",
                    "content": INVOICE_CLASSIFICATION_PROMPT.format(
                        vendor=vendor, total=total, text=text[:2000]
                    ),
                },
            ],
            temperature=0,
            extra_headers={
                "HTTP-Referer": "https://github.com/invoice-ai",
                "X-Title": "Invoice AI",
            },
        )
        content = response.choices[0].message.content.strip()
        content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(content)

    def _classify_rule_based(self, vendor: str, total: float, text: str) -> dict:
        text_lower = (vendor + " " + text).lower()

        if any(w in text_lower for w in ["electric", "gas", "water", "utility"]):
            return {"category": "utilities", "confidence": 0.7, "reasoning": "keyword match"}
        if any(w in text_lower for w in ["office", "staples", "paper", "supplies"]):
            return {"category": "office_supplies", "confidence": 0.7, "reasoning": "keyword match"}
        if any(w in text_lower for w in ["software", "license", "saas", "subscription"]):
            return {"category": "software", "confidence": 0.7, "reasoning": "keyword match"}
        if any(w in text_lower for w in ["consult", "advisory", "professional"]):
            return {"category": "consulting", "confidence": 0.6, "reasoning": "keyword match"}
        if any(w in text_lower for w in ["hotel", "flight", "travel", "uber", "lyft"]):
            return {"category": "travel", "confidence": 0.7, "reasoning": "keyword match"}
        if any(w in text_lower for w in ["restaurant", "cafe", "lunch", "dinner", "food"]):
            return {"category": "meals", "confidence": 0.7, "reasoning": "keyword match"}
        if any(w in text_lower for w in ["rent", "lease"]):
            return {"category": "rent", "confidence": 0.7, "reasoning": "keyword match"}

        return {"category": "other", "confidence": 0.3, "reasoning": "no keyword match"}
