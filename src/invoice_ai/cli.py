from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from .api import create_app
from .parser import parse_invoice_text


def _run_parse(input_path: Path) -> None:
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    content = input_path.read_text(encoding="utf-8")
    result = parse_invoice_text(content)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def _run_serve(host: str, port: int) -> None:
    app = create_app()
    uvicorn.run(app, host=host, port=port)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="invoice-ai",
        description="Extract structured invoice fields from plain text.",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    parse_parser = subparsers.add_parser("parse", help="Parse invoice text file")
    parse_parser.add_argument("input", type=Path, help="Path to a text file containing invoice content")

    serve_parser = subparsers.add_parser("serve", help="Run Invoice AI API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind the API server")

    parser.add_argument("input", nargs="?", type=Path, help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.command == "serve":
        _run_serve(args.host, args.port)
        return

    if args.command == "parse":
        _run_parse(args.input)
        return

    if args.input:
        _run_parse(args.input)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
