"""
Universal Corpus Pattern Language

A Formal Specification System for AI-Native Interactive Systems.

This package provides:
- Pydantic models for pattern validation
- SQLAlchemy database layer for persistence
- FastAPI REST API for pattern management
- CLI tools for pattern operations
"""

__version__ = "1.0.0"
__author__ = "Universal Corpus Team"

from universal_corpus.models import Pattern, Metadata, Definition
from universal_corpus.database import PatternRepository, init_db, get_db

__all__ = [
    "Pattern",
    "Metadata",
    "Definition",
    "PatternRepository",
    "init_db",
    "get_db",
    "__version__",
]

