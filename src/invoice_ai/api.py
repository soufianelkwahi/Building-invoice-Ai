from __future__ import annotations

from io import BytesIO

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from .models import InvoiceJob
from .service import process_invoice_text

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None


class ParseInvoiceRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw invoice text content")


class InvoiceJobResponse(BaseModel):
    id: int
    source_type: str
    status: str
    confidence: str
    parsed_data: dict


class HealthResponse(BaseModel):
    status: str


def require_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _extract_text_from_pdf(content: bytes) -> str:
    if PdfReader is None:
        raise HTTPException(status_code=501, detail="PDF support requires pypdf dependency")
    reader = PdfReader(BytesIO(content))
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()


def _extract_text_from_image(_content: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=501, detail="Image OCR requires pytesseract and Pillow") from exc

    image = Image.open(BytesIO(_content))
    return pytesseract.image_to_string(image)


def create_app() -> FastAPI:
    app = FastAPI(title="Invoice AI API", version="0.3.0")

    Base.metadata.create_all(bind=engine)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/parse", response_model=InvoiceJobResponse, dependencies=[Depends(require_api_key)])
    def parse_invoice(payload: ParseInvoiceRequest, db: Session = Depends(get_db)) -> InvoiceJobResponse:
        job = process_invoice_text(payload.text, source_type="text")
        db.add(job)
        db.commit()
        db.refresh(job)
        return InvoiceJobResponse(
            id=job.id,
            source_type=job.source_type,
            status=job.status,
            confidence=job.confidence,
            parsed_data=job.parsed_data,
        )

    @app.post("/ingest-file", response_model=InvoiceJobResponse, dependencies=[Depends(require_api_key)])
    async def ingest_file(file: UploadFile = File(...), db: Session = Depends(get_db)) -> InvoiceJobResponse:
        content = await file.read()
        ctype = file.content_type or ""

        if "pdf" in ctype or file.filename.lower().endswith(".pdf"):
            text = _extract_text_from_pdf(content)
            source_type = "pdf"
        elif ctype.startswith("image/"):
            text = _extract_text_from_image(content)
            source_type = "image"
        else:
            text = content.decode("utf-8", errors="ignore")
            source_type = "text"

        job = process_invoice_text(text, source_type=source_type)
        db.add(job)
        db.commit()
        db.refresh(job)
        return InvoiceJobResponse(
            id=job.id,
            source_type=job.source_type,
            status=job.status,
            confidence=job.confidence,
            parsed_data=job.parsed_data,
        )

    @app.get("/jobs/{job_id}", response_model=InvoiceJobResponse, dependencies=[Depends(require_api_key)])
    def get_job(job_id: int, db: Session = Depends(get_db)) -> InvoiceJobResponse:
        job = db.get(InvoiceJob, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return InvoiceJobResponse(
            id=job.id,
            source_type=job.source_type,
            status=job.status,
            confidence=job.confidence,
            parsed_data=job.parsed_data,
        )

    return app


app = create_app()
