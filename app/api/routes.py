import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, verify_auth
from app.core.config import settings
from models.schemas import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceUpdate,
    ProcessingResult,
)
from services.invoice_service import InvoiceService

router = APIRouter(dependencies=[Depends(verify_auth)])


@router.post("/invoices/upload", response_model=ProcessingResult)
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProcessingResult:
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension {ext} not allowed. Use: {settings.allowed_extensions}",
        )

    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large",
        )

    filename = f"{uuid.uuid4()}{ext}"
    filepath = Path(settings.upload_dir) / filename
    filepath.write_bytes(content)

    service = InvoiceService(db)
    result = service.process_invoice(str(filepath))
    return result


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[InvoiceResponse]:
    service = InvoiceService(db)
    return service.list_invoices(skip, limit)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    db: Session = Depends(get_db),
) -> InvoiceResponse:
    service = InvoiceService(db)
    invoice = service.update_invoice(invoice_id, data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    service = InvoiceService(db)
    if not service.delete_invoice(invoice_id):
        raise HTTPException(status_code=404, detail="Invoice not found")
