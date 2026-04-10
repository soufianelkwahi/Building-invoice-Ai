# Invoice AI (Starter)

مشروع بداية لبناء **Invoice AI** لاستخراج بيانات الفواتير من النص وتحويلها إلى JSON منظم، مع API وطبقة تخزين بسيطة.

## المميزات الحالية
- استخراج رقم الفاتورة، تاريخ الفاتورة، تاريخ الاستحقاق.
- استخراج اسم المورد واسم العميل.
- استخراج Subtotal / Tax / Total.
- استنتاج العملة من الرمز أو الكود (`$`, `€`, `£`, `USD`, `EUR`, `GBP`, `SAR`, `AED`).
- دعم مبالغ بصيغ متعددة (مثل `1,100.50` و `1.100,50`).
- استنتاج `due_date` تلقائياً من `Net XX` إذا لم يكن تاريخ الاستحقاق موجودًا.
- حساب `total` تلقائياً من `subtotal + tax` إذا كان الإجمالي غير مذكور.
- API فيه حماية بمفتاح (`x-api-key`).
- حفظ نتائج التحليل في قاعدة بيانات (SQLite افتراضياً أو PostgreSQL عبر متغير بيئة).
- endpoints لاستقبال نص أو ملف (`PDF / Image / Text`) مع تتبع job.

## هيكل المشروع
- `src/invoice_ai/parser.py`: منطق التحليل والاستخراج.
- `src/invoice_ai/api.py`: API عبر FastAPI.
- `src/invoice_ai/service.py`: منطق معالجة الفاتورة وتقدير الثقة.
- `src/invoice_ai/models.py`: موديل قاعدة البيانات.
- `src/invoice_ai/db.py`: إعداد الاتصال بقاعدة البيانات.
- `src/invoice_ai/config.py`: الإعدادات من environment.
- `src/invoice_ai/cli.py`: واجهة سطر الأوامر.
- `tests/test_parser.py`: اختبارات الوحدة.

## التشغيل
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## الإعدادات (Environment)
```bash
export INVOICE_AI_API_KEY="super-secret-key"
export INVOICE_AI_DATABASE_URL="sqlite:///./invoice_ai.db"
```

> إذا أردت PostgreSQL:
> `export INVOICE_AI_DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/invoice_ai"`

### استخدام CLI
```bash
invoice-ai parse sample_invoice.txt
```

### تشغيل API
```bash
invoice-ai serve --host 0.0.0.0 --port 8000
```

### فحص الصحة
```bash
curl http://127.0.0.1:8000/health
```

### تحليل نص عبر API
```bash
curl -X POST http://127.0.0.1:8000/parse \
  -H "x-api-key: super-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"text":"Invoice # INV-1\nDate: 10/04/2026\nSubtotal: $100\nTax: $10\nTotal: $110"}'
```

### تحليل ملف عبر API (PDF/صورة/نص)
```bash
curl -X POST http://127.0.0.1:8000/ingest-file \
  -H "x-api-key: super-secret-key" \
  -F "file=@sample_invoice.pdf"
```

### جلب نتيجة Job
```bash
curl -H "x-api-key: super-secret-key" http://127.0.0.1:8000/jobs/1
```

## الاختبارات
```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## ملاحظات
- OCR للصور يتطلب تثبيت `pytesseract` و `Pillow` وتثبيت محرك Tesseract على النظام.
- بدون OCR dependencies، API سيعيد `501` عند رفع صورة.
