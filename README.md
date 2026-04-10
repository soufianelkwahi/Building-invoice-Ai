# Invoice AI (Starter)

مشروع بداية لبناء **Invoice AI** لاستخراج بيانات الفواتير من النص وتحويلها إلى JSON منظم.

## المميزات الحالية
- استخراج رقم الفاتورة، تاريخ الفاتورة، تاريخ الاستحقاق.
- استخراج اسم المورد واسم العميل.
- استخراج Subtotal / Tax / Total.
- استنتاج العملة من الرمز أو الكود (`$`, `€`, `£`, `USD`, `EUR`, `GBP`, `SAR`, `AED`).
- دعم مبالغ بصيغ متعددة (مثل `1,100.50` و `1.100,50`).
- استنتاج `due_date` تلقائياً من `Net XX` إذا لم يكن تاريخ الاستحقاق موجودًا.
- حساب `total` تلقائياً من `subtotal + tax` إذا كان الإجمالي غير مذكور.
- واجهة CLI بسيطة.
- API جاهز باستخدام FastAPI.
- اختبارات وحدة تغطي سيناريوهات متعددة.

## هيكل المشروع
- `src/invoice_ai/parser.py`: منطق التحليل والاستخراج.
- `src/invoice_ai/cli.py`: واجهة سطر الأوامر.
- `src/invoice_ai/api.py`: API عبر FastAPI.
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
invoice-ai parse sample_invoice.txt
```

> ما زال هذا الأمر يعمل أيضاً للتوافق: `invoice-ai sample_invoice.txt`

### تشغيل API
```bash
invoice-ai serve --host 0.0.0.0 --port 8000
```

#### فحص الصحة
```bash
curl http://127.0.0.1:8000/health
```

#### تحليل فاتورة عبر API
```bash
curl -X POST http://127.0.0.1:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"text":"Invoice # INV-1\nDate: 10/04/2026\nSubtotal: $100\nTax: $10\nTotal: $110"}'
```

## الاختبارات
```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## الخطوة القادمة (AI فعلي)
لبناء نسخة أقوى:
1. إضافة OCR (مثل Tesseract أو Azure Document Intelligence) للفواتير المصورة/PDF.
2. إضافة LLM Extraction schema-based (مثلاً عبر OpenAI JSON schema).
3. إضافة PostgreSQL + تتبع حالة المعالجة.
4. إضافة لوحة تحكم للمراجعة البشرية (Human-in-the-loop).
