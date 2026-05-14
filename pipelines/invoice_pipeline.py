import logging

from ai.classifier import InvoiceClassifier
from ai.extractor import InvoiceExtractor
from ai.postprocessing import clean_extracted_data

logger = logging.getLogger(__name__)


class InvoicePipeline:
    def __init__(self):
        self.extractor = InvoiceExtractor()
        self.classifier = InvoiceClassifier()

    def run(self, filepath: str) -> dict:
        raw_text = self.extractor.extract_text_from_file(filepath)
        if not raw_text or raw_text.startswith("["):
            logger.warning("No text extracted from %s", filepath)
            return {
                "extracted_data": {"raw_text": raw_text},
                "classification": {"category": "other", "confidence": 0.0},
            }

        extracted = self.extractor.extract_fields(raw_text)
        extracted["raw_text"] = raw_text
        extracted = clean_extracted_data(extracted)

        vendor = extracted.get("vendor_name", "")
        total = extracted.get("total_amount", 0.0)
        classification = self.classifier.classify(vendor, total, raw_text)

        return {
            "extracted_data": extracted,
            "classification": classification,
        }
