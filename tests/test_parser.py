import unittest

from invoice_ai.parser import parse_invoice_text


class InvoiceParserTests(unittest.TestCase):
    def test_parse_common_invoice_fields(self) -> None:
        sample = """
        ACME Corp
        Invoice # INV-2026-008
        Date: 10/04/2026
        Due Date: 20/04/2026
        Vendor: ACME Corp
        Bill To: Globex LLC
        Subtotal: $1,000.00
        Tax: $100.00
        Total: $1,100.00
        """

        parsed = parse_invoice_text(sample)

        self.assertEqual(parsed["invoice_number"], "INV-2026-008")
        self.assertEqual(parsed["invoice_date"], "2026-04-10")
        self.assertEqual(parsed["due_date"], "2026-04-20")
        self.assertEqual(parsed["vendor_name"], "ACME Corp")
        self.assertEqual(parsed["customer_name"], "Globex LLC")
        self.assertEqual(parsed["subtotal"], 1000.0)
        self.assertEqual(parsed["tax"], 100.0)
        self.assertEqual(parsed["total"], 1100.0)
        self.assertEqual(parsed["currency"], "USD")

    def test_infer_due_date_from_net_terms(self) -> None:
        sample = """
        Invoice Number: INV-77
        Invoice Date: 2026-04-10
        Payment Terms: Net 30
        Vendor: Nile Services
        Customer: Desert Retail
        Subtotal: EUR 100,50
        Tax: EUR 19,50
        """

        parsed = parse_invoice_text(sample)

        self.assertEqual(parsed["invoice_number"], "INV-77")
        self.assertEqual(parsed["invoice_date"], "2026-04-10")
        self.assertEqual(parsed["due_date"], "2026-05-10")
        self.assertEqual(parsed["subtotal"], 100.5)
        self.assertEqual(parsed["tax"], 19.5)
        self.assertEqual(parsed["total"], 120.0)
        self.assertEqual(parsed["currency"], "EUR")

    def test_parse_european_amount_and_currency_from_text(self) -> None:
        sample = """
        Invoice # AB-42
        Date: 01.03.2026
        Supplier: Studio One
        Bill To: Client Two
        Currency: GBP
        Subtotal: £1.234,50
        VAT: £246,90
        Grand Total: £1.481,40
        """

        parsed = parse_invoice_text(sample)

        self.assertEqual(parsed["invoice_date"], "2026-03-01")
        self.assertEqual(parsed["subtotal"], 1234.5)
        self.assertEqual(parsed["tax"], 246.9)
        self.assertEqual(parsed["total"], 1481.4)
        self.assertEqual(parsed["currency"], "GBP")


if __name__ == "__main__":
    unittest.main()
