from ai.classifier import InvoiceClassifier
from ai.extractor import InvoiceExtractor
from ai.postprocessing import clean_extracted_data


class TestInvoiceExtractor:
    def test_regex_extraction(self):
        extractor = InvoiceExtractor()
        text = "Invoice #INV-2024-001\nVendor: Acme Corp\nTotal: $1,234.56\nDate: 2024-03-15"
        result = extractor._extract_with_regex(text)
        assert result["invoice_number"] == "INV-2024-001"
        assert result["total_amount"] == 1234.56

    def test_extract_from_text_file(self, tmp_path):
        f = tmp_path / "invoice.txt"
        f.write_text("Invoice #123\nTotal: $99.99")
        extractor = InvoiceExtractor()
        text = extractor.extract_text_from_file(str(f))
        assert "Invoice #123" in text


class TestInvoiceClassifier:
    def test_rule_based_utilities(self):
        classifier = InvoiceClassifier()
        result = classifier._classify_rule_based("Electric Co", 200.0, "electric bill")
        assert result["category"] == "utilities"

    def test_rule_based_office(self):
        classifier = InvoiceClassifier()
        result = classifier._classify_rule_based("Staples", 50.0, "office supplies")
        assert result["category"] == "office_supplies"

    def test_rule_based_other(self):
        classifier = InvoiceClassifier()
        result = classifier._classify_rule_based("Unknown", 100.0, "random stuff")
        assert result["category"] == "other"

    def test_rule_based_software(self):
        classifier = InvoiceClassifier()
        result = classifier._classify_rule_based("Microsoft", 299.0, "software license renewal")
        assert result["category"] == "software"


class TestPostprocessing:
    def test_clean_extracted_data(self):
        raw = {
            "invoice_number": " INV-001 ",
            "total_amount": "$1,234.56",
            "currency": "usd",
            "line_items": [{"quantity": "2", "unit_price": "$100", "amount": "200"}],
        }
        clean = clean_extracted_data(raw)
        assert clean["total_amount"] == 1234.56
        assert clean["currency"] == "USD"
        assert clean["invoice_number"] == "INV-001"
        assert clean["line_items"][0]["quantity"] == 2.0
        assert clean["line_items"][0]["amount"] == 200.0

    def test_normalize_date(self):
        from ai.postprocessing import normalize_date
        assert normalize_date("2024-03-15") == "2024-03-15"
        assert normalize_date("03/15/2024") == "2024-03-15"
        assert normalize_date(None) is None
