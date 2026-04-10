from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class InvoiceJob(Base):
    __tablename__ = "invoice_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_type: Mapped[str] = mapped_column(String(20), default="text")
    status: Mapped[str] = mapped_column(String(20), default="processed")
    raw_text: Mapped[str] = mapped_column(Text)
    parsed_data: Mapped[dict] = mapped_column(JSON, default={})
    confidence: Mapped[str] = mapped_column(String(10), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
