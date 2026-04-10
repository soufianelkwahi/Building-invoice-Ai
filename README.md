# Invoice AI (Starter)

مشروع بداية لبناء **Invoice AI** لاستخراج بيانات الفواتير من النص وتحويلها إلى JSON منظم.

## المميزات الحالية
- استخراج رقم الفاتورة، تاريخ الفاتورة، تاريخ الاستحقاق.
- استخراج اسم المورد واسم العميل.
- استخراج Subtotal / Tax / Total.
- استنتاج العملة من الرمز ($, €, £).
- واجهة CLI بسيطة.
- اختبارات وحدة جاهزة.

## هيكل المشروع
- `src/invoice_ai/parser.py`: منطق التحليل والاستخراج.
- `src/invoice_ai/cli.py`: واجهة سطر الأوامر.
- `tests/test_parser.py`: اختبارات الوحدة.

## التشغيل
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### استخدام CLI
أنشئ ملف نصي لفاتورة (مثلاً `sample_invoice.txt`) ثم:

```bash
invoice-ai sample_invoice.txt
```

النتيجة ستكون JSON مثل:
```json
{
  "invoice_number": "INV-2026-008",
  "invoice_date": "2026-04-10",
  "due_date": "2026-04-20",
  "vendor_name": "ACME Corp",
  "customer_name": "Globex LLC",
  "subtotal": 1000.0,
  "tax": 100.0,
  "total": 1100.0,
  "currency": "USD"
}
```

## الاختبارات
```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## الخطوة القادمة (AI فعلي)
لبناء نسخة أقوى:
1. إضافة OCR (مثل Tesseract أو Azure Document Intelligence) للفواتير المصورة/PDF.
2. إضافة LLM Extraction schema-based (مثلاً عبر OpenAI JSON schema).
3. إضافة API (FastAPI) + قاعدة بيانات (PostgreSQL).
4. إضافة لوحة تحكم للمراجعة البشرية (Human-in-the-loop).
