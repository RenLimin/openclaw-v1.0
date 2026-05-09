"""
Vector Store module for Iris RAG engine.
Provides FAISS index wrapper and SQLite metadata storage.
"""
import os
import json
import sqlite3
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class VectorStore:
    """Vector store combining FAISS for similarity search and SQLite for metadata."""
    
    def __init__(self, db_path: str, index_dir: str, dimension: int = 384, 
                 similarity: str = "cosine"):
        """
        Initialize vector store.
        
        Args:
            db_path: Path to SQLite database file
            index_dir: Directory to store FAISS index files
            dimension: Embedding dimension (default 384 for all-MiniLM-L6-v2)
            similarity: Similarity metric - "cosine" or "l2"
        """
        self.db_path = db_path
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.similarity = similarity.lower()
        
        self.indices: Dict[str, faiss.Index] = {}
        self._init_db()
        self._load_indices()
    
    def _init_db(self):
        """Initialize SQLite database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_hash TEXT,
                FOREIGN KEY (collection_id) REFERENCES rag_collections(id),
                UNIQUE(collection_id, file_path)
            )
        """)
        
        # Create chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                vector_id INTEGER NOT NULL,
                start_pos INTEGER,
                end_pos INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES rag_documents(id),
                UNIQUE(document_id, chunk_index)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_indices(self):
        """Load all existing FAISS indices from disk."""
        for index_file in self.index_dir.glob("*.faiss"):
            collection_name = index_file.stem
            try:
                index = faiss.read_index(str(index_file))
                self.indices[collection_name] = index
            except Exception as e:
                print(f"Failed to load index {collection_name}: {e}")
    
    def _save_index(self, collection_name: str):
        """Save FAISS index to disk."""
        if collection_name in self.indices:
            index_path = self.index_dir / f"{collection_name}.faiss"
            faiss.write_index(self.indices[collection_name], str(index_path))
    
    def _create_index(self, collection_name: str) -> faiss.Index:
        """Create a new FAISS index."""
        if self.similarity == "cosine":
            index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine
        else:  # l2
            index = faiss.IndexFlatL2(self.dimension)
        
        self.indices[collection_name] = index
        self._save_index(collection_name)
        return index
    
    def create_collection(self, name: str, description: str = "") -> bool:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            description: Optional description
            
        Returns:
            True if created, False if already exists
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO rag_collections (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            conn.close()
            self._create_index(name)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections with statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.description, c.created_at,
                   COUNT(DISTINCT d.id) as doc_count,
                   COUNT(DISTINCT ch.id) as chunk_count
            FROM rag_collections c
            LEFT JOIN rag_documents d ON c.id = d.collection_id
            LEFT JOIN rag_chunks ch ON d.id = ch.document_id
            GROUP BY c.id
        """)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "created_at": row[3],
                "doc_count": row[4],
                "chunk_count": row[5]
            }
            for row in rows
        ]
    
    def get_collection_id(self, collection_name: str) -> Optional[int]:
        """Get collection ID by name."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM rag_collections WHERE name = ?", (collection_name,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def add_document(self, collection_name: str, file_path: str, file_name: str,
                     file_type: str, file_size: int, file_hash: str) -> int:
        """
        Add or update a document record.
        
        Returns:
            Document ID
        """
        collection_id = self.get_collection_id(collection_name)
        if collection_id is None:
            self.create_collection(collection_name)
            collection_id = self.get_collection_id(collection_name)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if document exists
        cursor.execute("""
            SELECT id FROM rag_documents 
            WHERE collection_id = ? AND file_path = ?
        """, (collection_id, file_path))
        row = cursor.fetchone()
        
        if row:
            # Update existing document
            doc_id = row[0]
            cursor.execute("""
                UPDATE rag_documents 
                SET file_name = ?, file_type = ?, file_size = ?, 
                    file_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (file_name, file_type, file_size, file_hash, doc_id))
            # Delete old chunks
            cursor.execute("DELETE FROM rag_chunks WHERE document_id = ?", (doc_id,))
        else:
            # Insert new document
            cursor.execute("""
                INSERT INTO rag_documents 
                (collection_id, file_path, file_name, file_type, file_size, file_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (collection_id, file_path, file_name, file_type, file_size, file_hash))
            doc_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return doc_id
    
    def add_chunks(self, collection_name: str, document_id: int, 
                   chunks: List[Dict[str, Any]], vectors: np.ndarray) -> int:
        """
        Add chunks and their vectors to the store.
        
        Args:
            collection_name: Name of the collection
            document_id: Document ID
            chunks: List of chunk dicts with text, index, start_pos, end_pos, metadata
            vectors: Numpy array of shape (n_chunks, dimension)
            
        Returns:
            Number of chunks added
        """
        if collection_name not in self.indices:
            self._create_index(collection_name)
        
        index = self.indices[collection_name]
        n_vectors = index.ntotal
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for i, chunk in enumerate(chunks):
            vector_id = n_vectors + i
            cursor.execute("""
                INSERT INTO rag_chunks 
                (document_id, chunk_index, text, vector_id, start_pos, end_pos, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id,
                chunk["index"],
                chunk["text"],
                vector_id,
                chunk.get("start_pos"),
                chunk.get("end_pos"),
                json.dumps(chunk.get("metadata", {}))
            ))
        
        conn.commit()
        conn.close()
        
        # Normalize vectors for cosine similarity
        if self.similarity == "cosine":
            faiss.normalize_L2(vectors)
        
        index.add(vectors)
        self._save_index(collection_name)
        
        return len(chunks)
    
    def search(self, query_vector: np.ndarray, collection_name: Optional[str] = None,
               top_k: int = 5, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector of shape (1, dimension)
            collection_name: Collection to search (None for all collections)
            top_k: Number of results to return
            threshold: Similarity threshold (filter results below this)
            
        Returns:
            List of search results with text, score, and metadata
        """
        if collection_name:
            collections = [collection_name]
        else:
            collections = list(self.indices.keys())
        
        all_results = []
        
        for coll_name in collections:
            if coll_name not in self.indices:
                continue
            
            index = self.indices[coll_name]
            
            # Normalize query for cosine
            if self.similarity == "cosine":
                query_norm = query_vector.copy()
                faiss.normalize_L2(query_norm)
                distances, indices = index.search(query_norm, top_k)
                scores = distances[0]  # For cosine, higher = better
            else:
                distances, indices = index.search(query_vector, top_k)
                scores = 1.0 / (1.0 + distances[0])  # Convert L2 to similarity
            
            # Get metadata from DB
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for i, (vec_id, score) in enumerate(zip(indices[0], scores)):
                if vec_id < 0:
                    continue  # No result
                if threshold is not None and score < threshold:
                    continue
                
                cursor.execute("""
                    SELECT ch.text, ch.metadata, d.file_name, d.file_path, d.file_type
                    FROM rag_chunks ch
                    JOIN rag_documents d ON ch.document_id = d.id
                    JOIN rag_collections c ON d.collection_id = c.id
                    WHERE c.name = ? AND ch.vector_id = ?
                """, (coll_name, int(vec_id)))
                row = cursor.fetchone()
                
                if row:
                    all_results.append({
                        "text": row[0],
                        "score": float(score),
                        "collection": coll_name,
                        "file_name": row[2],
                        "file_path": row[3],
                        "file_type": row[4],
                        "metadata": json.loads(row[1]) if row[1] else {}
                    })
            
            conn.close()
        
        # Sort by score descending and take top_k
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]
    
    def delete_document(self, collection_name: str, file_path: str) -> bool:
        """
        Delete a document and its chunks.
        Note: FAISS doesn't support easy deletion, so we mark chunks as invalid.
        For true cleanup, rebuild the index.
        """
        collection_id = self.get_collection_id(collection_name)
        if collection_id is None:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM rag_chunks 
            WHERE document_id IN (
                SELECT id FROM rag_documents 
                WHERE collection_id = ? AND file_path = ?
            )
        """, (collection_id, file_path))
        cursor.execute("""
            DELETE FROM rag_documents 
            WHERE collection_id = ? AND file_path = ?
        """, (collection_id, file_path))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    
    def get_document_hash(self, collection_name: str, file_path: str) -> Optional[str]:
        """Get stored hash of a document for change detection."""
        collection_id = self.get_collection_id(collection_name)
        if collection_id is None:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_hash FROM rag_documents
            WHERE collection_id = ? AND file_path = ?
        """, (collection_id, file_path))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
