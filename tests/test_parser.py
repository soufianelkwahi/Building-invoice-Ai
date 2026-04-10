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


if __name__ == "__main__":
    unittest.main()
