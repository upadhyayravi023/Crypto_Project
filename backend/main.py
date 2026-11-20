"""Render imports this FastAPI app using ``uvicorn backend.main:app``."""
from app.api.main import app

__all__ = ["app"]
