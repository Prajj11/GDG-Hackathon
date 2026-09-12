"""Digital Guardrails — app compatibility package.
Maps the app.* namespace seamlessly to the underlying trained models, database, and APIs.
"""
from backend.main import app

__all__ = ['app']
