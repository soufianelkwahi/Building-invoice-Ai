from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import parse_invoice_text


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="invoice-ai",
        description="Extract structured invoice fields from plain text.",
    )
    parser.add_argument("input", type=Path, help="Path to a text file containing invoice content")
    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file not found: {args.input}")

    content = args.input.read_text(encoding="utf-8")
    result = parse_invoice_text(content)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
