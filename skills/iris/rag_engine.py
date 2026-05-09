"""
Main RAG Engine module for Iris.
Unifies vector store, document parser, and embedding model.
"""
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False

from .vector_store import VectorStore
from .document_parser import DocumentParser


class RAGEngine:
    """Main RAG engine class."""
    
    def __init__(self, db_path: Optional[str] = None, index_dir: Optional[str] = None,
                 embedding_model: str = "all-MiniLM-L6-v2", chunk_size: int = 512,
                 chunk_overlap: int = 50, similarity: str = "cosine"):
        """
        Initialize RAG engine.
        
        Args:
            db_path: Path to SQLite database (default: ~/.iris/rag.db)
            index_dir: Directory for FAISS indices (default: ~/.iris/indices)
            embedding_model: Name of sentence-transformers model
            chunk_size: Target chunk size
            chunk_overlap: Chunk overlap size
            similarity: Similarity metric ("cosine" or "l2")
        """
        # Set default paths
        home_dir = Path.home() / ".iris"
        home_dir.mkdir(exist_ok=True)
        
        self.db_path = db_path or str(home_dir / "rag.db")
        self.index_dir = index_dir or str(home_dir / "indices")
        
        # Initialize components
        self.parser = DocumentParser(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_semantic_boundaries=True
        )
        
        # Load embedding model
        if EMBEDDING_AVAILABLE:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        else:
            raise ImportError("sentence-transformers is required")
        
        # Initialize vector store
        self.vector_store = VectorStore(
            db_path=self.db_path,
            index_dir=self.index_dir,
            dimension=self.embedding_dim,
            similarity=similarity
        )
    
    def import_file(self, file_path: str, collection: str = "default",
                 incremental: bool = True) -> Dict[str, Any]:
        """
        Import a single file into the RAG engine.
        
        Args:
            file_path: Path to the file
            collection: Collection name
            incremental: Skip if file hasn't changed
            
        Returns:
            Import statistics
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Parse the document
        doc = self.parser.parse_file(str(path))
        
        # Check if incremental update check
        if incremental:
            stored_hash = self.vector_store.get_document_hash(collection, doc["file_path"])
            if stored_hash == doc["file_hash"]:
                return {
                    "status": "skipped",
                    "reason": "file unchanged",
                    "file": doc["file_name"],
                    "collection": collection
                }
        
        # Chunk the text
        chunks = self.parser.chunk_text(
            doc["content"],
            metadata={
                "file_name": doc["file_name"],
                "file_type": doc["file_type"],
                "file_path": doc["file_path"]
            }
        )
        
        if not chunks:
            return {
                "status": "empty",
                "file": doc["file_name"],
                "collection": collection
            }
        
        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        
        # Add to vector store
        doc_id = self.vector_store.add_document(
            collection_name=collection,
            file_path=doc["file_path"],
            file_name=doc["file_name"],
            file_type=doc["file_type"],
            file_size=doc["file_size"],
            file_hash=doc["file_hash"]
        )
        
        n_chunks = self.vector_store.add_chunks(
            collection_name=collection,
            document_id=doc_id,
            chunks=chunks,
            vectors=embeddings
        )
        
        return {
            "status": "imported",
            "file": doc["file_name"],
            "collection": collection,
            "chunks": n_chunks,
            "document_id": doc_id
        }
    
    def import_directory(self, dir_path: str, collection: str = "default",
                         recursive: bool = True, incremental: bool = True,
                         extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Import all files from a directory.
        
        Args:
            dir_path: Path to directory
            collection: Collection name
            recursive: Scan subdirectories
            incremental: Skip unchanged files
            extensions: List of allowed extensions
            
        Returns:
            Import statistics
        """
        path = Path(dir_path)
        if not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")
        
        docs = self.parser.parse_directory(str(path), recursive=recursive, extensions=extensions)
        
        results = {
            "collection": collection,
            "total": len(docs),
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "total_chunks": 0,
            "files": []
        }
        
        for doc in tqdm(docs, desc=f"Importing to {collection}"):
            try:
                # Check incremental
                if incremental:
                    stored_hash = self.vector_store.get_document_hash(collection, doc["file_path"])
                    if stored_hash == doc["file_hash"]:
                        results["skipped"] += 1
                        results["files"].append({
                            "file": doc["file_name"],
                            "status": "skipped"
                        })
                        continue
                
                # Chunk and embed
                chunks = self.parser.chunk_text(
                    doc["content"],
                    metadata={
                        "file_name": doc["file_name"],
                        "file_type": doc["file_type"],
                        "file_path": doc["file_path"]
                    }
                )
                
                if not chunks:
                    results["skipped"] += 1
                    continue
                
                texts = [chunk["text"] for chunk in chunks]
                embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
                
                doc_id = self.vector_store.add_document(
                    collection_name=collection,
                    file_path=doc["file_path"],
                    file_name=doc["file_name"],
                    file_type=doc["file_type"],
                    file_size=doc["file_size"],
                    file_hash=doc["file_hash"]
                )
                
                n_chunks = self.vector_store.add_chunks(
                    collection_name=collection,
                    document_id=doc_id,
                    chunks=chunks,
                    vectors=embeddings
                )
                
                results["imported"] += 1
                results["total_chunks"] += n_chunks
                results["files"].append({
                    "file": doc["file_name"],
                    "status": "imported",
                    "chunks": n_chunks
                })
                
            except Exception as e:
                results["failed"] += 1
                results["files"].append({
                    "file": doc["file_name"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def search(self, query: str, collection: Optional[str] = None,
               top_k: int = 5, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search the RAG engine.
        
        Args:
            query: Search query text
            collection: Collection to search (None for all)
            top_k: Number of results
            threshold: Similarity threshold
            
        Returns:
            List of search results
        """
        # Embed query
        query_vector = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Search vector store
        results = self.vector_store.search(
            query_vector=query_vector,
            collection_name=collection,
            top_k=top_k,
            threshold=threshold
        )
        
        return results
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections."""
        return self.vector_store.list_collections()
    
    def create_collection(self, name: str, description: str = "") -> bool:
        """Create a new collection."""
        return self.vector_store.create_collection(name, description)
    
    def delete_document(self, collection: str, file_path: str) -> bool:
        """Delete a document from collection."""
        return self.vector_store.delete_document(collection, file_path)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG engine statistics."""
        collections = self.list_collections()
        
        total_docs = sum(c["doc_count"] for c in collections)
        total_chunks = sum(c["chunk_count"] for c in collections)
        
        return {
            "db_path": self.db_path,
            "index_dir": self.index_dir,
            "collections_count": len(collections),
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "collections": collections
        }
