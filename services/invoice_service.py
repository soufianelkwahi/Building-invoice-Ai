import json
import time

from sqlalchemy.orm import Session

from ai.classifier import InvoiceClassifier
from ai.extractor import InvoiceExtractor
from ai.postprocessing import clean_extracted_data
from db.models import Invoice
from models.schemas import InvoiceCreate, InvoiceUpdate
from pipelines.invoice_pipeline import InvoicePipeline


class InvoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = InvoicePipeline()

    def process_invoice(self, filepath: str):
        start = time.time()
        result = self.pipeline.run(filepath)
        elapsed = (time.time() - start) * 1000

        line_items = result.get("extracted_data", {}).get("line_items", [])
        extracted = result.get("extracted_data", {})
        classification = result.get("classification", {})

        invoice_data = InvoiceCreate(
            invoice_number=extracted.get("invoice_number", ""),
            vendor_name=extracted.get("vendor_name", ""),
            vendor_address=extracted.get("vendor_address"),
            customer_name=extracted.get("customer_name", ""),
            invoice_date=extracted.get("invoice_date"),
            due_date=extracted.get("due_date"),
            subtotal=extracted.get("subtotal", 0.0),
            tax_amount=extracted.get("tax_amount"),
            total_amount=extracted.get("total_amount", 0.0),
            currency=extracted.get("currency", "USD"),
            category=classification.get("category", "other"),
            confidence_score=classification.get("confidence", 0.0),
            raw_text=extracted.get("raw_text", extracted.get("text", "")),
            file_path=filepath,
            line_items=line_items,
        )

        invoice = self._create_invoice(invoice_data)
        return {
            "invoice": invoice,
            "category": classification.get("category", "other"),
            "confidence": classification.get("confidence", 0.0),
            "processing_time_ms": round(elapsed, 2),
        }

    def _create_invoice(self, data: InvoiceCreate) -> Invoice:
        db_invoice = Invoice(
            invoice_number=data.invoice_number,
            vendor_name=data.vendor_name,
            vendor_address=data.vendor_address,
            customer_name=data.customer_name,
            invoice_date=data.invoice_date,
            due_date=data.due_date,
            subtotal=data.subtotal,
            tax_amount=data.tax_amount,
            total_amount=data.total_amount,
            currency=data.currency,
            category=data.category,
            status=data.status,
            confidence_score=data.confidence_score,
            raw_text=data.raw_text,
            file_path=data.file_path,
            line_items=json.dumps([item.model_dump() for item in data.line_items]),
        )
        self.db.add(db_invoice)
        self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice

    def get_invoice(self, invoice_id: int) -> Invoice | None:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def list_invoices(self, skip: int = 0, limit: int = 100) -> list[Invoice]:
        return (
            self.db.query(Invoice)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_invoice(self, invoice_id: int, data: InvoiceUpdate) -> Invoice | None:
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(invoice, key, value)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete_invoice(self, invoice_id: int) -> bool:
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return False
        self.db.delete(invoice)
        self.db.commit()
        return True
