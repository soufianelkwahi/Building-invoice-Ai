"""Invoice AI package."""

from .parser import parse_invoice_text


def create_app():
    """Lazy import FastAPI app factory so parser-only usage doesn't require API deps."""
    from .api import create_app as _create_app

    return _create_app()


__all__ = ["create_app", "parse_invoice_text"]
