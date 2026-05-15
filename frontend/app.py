import io
import os
import httpx
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "invoice-ai-frontend-secret"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "sk-invoice-ai-dev")


@app.route("/")
def index():
    invoices = []
    try:
        r = httpx.get(
            f"{API_BASE}/api/v1/invoices",
            headers={"x-api-key": API_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            invoices = r.json()
    except Exception as e:
        flash(f"Error fetching invoices: {e}", "error")
    return render_template("index.html", invoices=invoices)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("index"))
    try:
        files = {"file": (secure_filename(file.filename), file.read(), file.content_type)}
        r = httpx.post(
            f"{API_BASE}/api/v1/invoices/upload",
            files=files,
            headers={"x-api-key": API_KEY},
            timeout=120,
        )
        if r.status_code == 200:
            flash("Invoice processed successfully!", "success")
        else:
            detail = r.json().get("detail", "Unknown error")
            flash(f"Upload failed: {detail}", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("index"))


@app.route("/invoices/<int:invoice_id>", methods=["POST"])
def delete_invoice(invoice_id):
    try:
        r = httpx.delete(
            f"{API_BASE}/api/v1/invoices/{invoice_id}",
            headers={"x-api-key": API_KEY},
            timeout=10,
        )
        if r.status_code == 204:
            flash("Invoice deleted", "success")
        else:
            flash("Failed to delete invoice", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
