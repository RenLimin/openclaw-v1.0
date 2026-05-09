"""
Iris RAG Engine - Private Knowledge Base System.

A lightweight, fast RAG engine with FAISS vector search and SQLite metadata storage.
"""

__version__ = "1.0.0"
__author__ = "Iris 🐦‍⬛"

from .rag_engine import RAGEngine
from .vector_store import VectorStore
from .document_parser import DocumentParser

__all__ = ["RAGEngine", "VectorStore", "DocumentParser"]
