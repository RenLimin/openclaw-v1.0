"""
Unit tests for Iris RAG Engine.
"""
import os
import tempfile
import shutil
import pytest
import numpy as np
from pathlib import Path

# Add workspace to path
import sys
workspace = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace))

from skills.iris import RAGEngine, VectorStore, DocumentParser


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp = tempfile.mkdtemp(prefix="iris_test_")
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def sample_docs(temp_dir):
    """Create sample test documents."""
    docs_dir = Path(temp_dir) / "docs"
    docs_dir.mkdir()
    
    # Create sample documents
    docs = [
        ("ai_intro.txt", "Artificial intelligence (AI) is intelligence demonstrated by machines, "
         "in contrast to the natural intelligence displayed by humans and animals. "
         "AI research has been defined as the field of study of intelligent agents. "
         "Machine learning is a subset of artificial intelligence."),
        
        ("ml_basics.txt", "Machine learning (ML) is a field of inquiry devoted to understanding "
         "and building methods that learn from data. ML algorithms build a mathematical model "
         "based on sample data, known as training data, in order to make predictions or decisions "
         "without being explicitly programmed to do so."),
        
        ("deep_learning.txt", "Deep learning is part of a broader family of machine learning methods "
         "based on artificial neural networks with representation learning. "
         "Learning can be supervised, semi-supervised or unsupervised. "
         "Deep learning architectures include deep neural networks, recurrent neural networks, "
         "convolutional neural networks and transformers."),
        
        ("nlp_intro.txt", "Natural language processing (NLP) is an interdisciplinary subfield of "
         "computer science and linguistics. It is primarily concerned with giving computers the "
         "ability to support and manipulate human language. NLP tasks include text translation, "
         "sentiment analysis, speech recognition, text summarization and question answering."),
        
        ("rag_systems.txt", "Retrieval-augmented generation (RAG) is a technique for enhancing "
         "the accuracy and reliability of generative AI models. RAG works by fetching facts "
         "from an external knowledge base before generating responses. "
         "This approach reduces hallucinations and improves response quality.")
    ]
    
    for filename, content in docs:
        with open(docs_dir / filename, "w") as f:
            f.write(content)
    
    return str(docs_dir)


class TestDocumentParser:
    """Tests for DocumentParser class."""
    
    def test_parse_txt(self, temp_dir):
        """Test parsing plain text file."""
        parser = DocumentParser()
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Hello, world! This is a test document.")
        
        result = parser.parse_file(str(test_file))
        
        assert result["content"] == "Hello, world! This is a test document."
        assert result["file_name"] == "test.txt"
        assert result["file_type"] == ".txt"
        assert "file_hash" in result
    
    def test_chunk_text(self):
        """Test text chunking."""
        parser = DocumentParser(chunk_size=100, chunk_overlap=20)
        
        text = "This is sentence one. This is sentence two. This is sentence three. " \
               "This is sentence four. This is sentence five. This is sentence six."
        
        chunks = parser.chunk_text(text)
        
        assert len(chunks) > 0
        assert all("text" in c for c in chunks)
        assert all("index" in c for c in chunks)
        assert chunks[0]["index"] == 0
    
    def test_chunk_semantic(self):
        """Test semantic chunking mode."""
        parser = DocumentParser(use_semantic_boundaries=True)
        
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. " * 10
        
        chunks = parser.chunk_text(text)
        
        assert len(chunks) > 0
        assert chunks[0]["metadata"]["chunk_method"] == "semantic"


class TestVectorStore:
    """Tests for VectorStore class."""
    
    def test_create_collection(self, temp_dir):
        """Test creating a collection."""
        db_path = Path(temp_dir) / "test.db"
        index_dir = Path(temp_dir) / "indices"
        
        store = VectorStore(str(db_path), str(index_dir), dimension=384)
        
        result = store.create_collection("test_collection", "Test description")
        assert result is True
        
        # Should return False for duplicate
        result = store.create_collection("test_collection")
        assert result is False
    
    def test_list_collections(self, temp_dir):
        """Test listing collections."""
        db_path = Path(temp_dir) / "test.db"
        index_dir = Path(temp_dir) / "indices"
        
        store = VectorStore(str(db_path), str(index_dir), dimension=384)
        store.create_collection("coll1")
        store.create_collection("coll2")
        
        collections = store.list_collections()
        
        assert len(collections) == 2
        assert {c["name"] for c in collections} == {"coll1", "coll2"}
    
    def test_add_and_search(self, temp_dir):
        """Test adding vectors and searching."""
        db_path = Path(temp_dir) / "test.db"
        index_dir = Path(temp_dir) / "indices"
        
        store = VectorStore(str(db_path), str(index_dir), dimension=8, similarity="l2")
        store.create_collection("test")
        
        # Add document
        doc_id = store.add_document(
            collection_name="test",
            file_path="/test/doc1.txt",
            file_name="doc1.txt",
            file_type=".txt",
            file_size=100,
            file_hash="abc123"
        )
        
        # Add chunks
        chunks = [
            {"index": 0, "text": "test text 1", "start_pos": 0, "end_pos": 10, "metadata": {}},
            {"index": 1, "text": "test text 2", "start_pos": 10, "end_pos": 20, "metadata": {}},
        ]
        
        vectors = np.array([
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ], dtype=np.float32)
        
        n_added = store.add_chunks("test", doc_id, chunks, vectors)
        assert n_added == 2
        
        # Search
        query = np.array([[0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], dtype=np.float32)
        results = store.search(query, "test", top_k=2)
        
        assert len(results) == 2
        assert results[0]["text"] == "test text 1"


class TestRAGEngine:
    """Tests for RAGEngine class."""
    
    def test_engine_initialization(self, temp_dir):
        """Test engine initialization."""
        db_path = Path(temp_dir) / "rag.db"
        index_dir = Path(temp_dir) / "indices"
        
        engine = RAGEngine(
            db_path=str(db_path),
            index_dir=str(index_dir),
            embedding_model="all-MiniLM-L6-v2"
        )
        
        assert engine is not None
        assert engine.embedding_dim == 384
    
    def test_import_directory(self, temp_dir, sample_docs):
        """Test importing directory of documents."""
        db_path = Path(temp_dir) / "rag.db"
        index_dir = Path(temp_dir) / "indices"
        
        engine = RAGEngine(db_path=str(db_path), index_dir=str(index_dir))
        
        result = engine.import_directory(
            sample_docs,
            collection="test_docs",
            incremental=False
        )
        
        assert result["total"] == 5
        assert result["imported"] == 5
        assert result["total_chunks"] >= 5
        
        # Check collection stats
        collections = engine.list_collections()
        assert len(collections) == 1
        assert collections[0]["name"] == "test_docs"
        assert collections[0]["doc_count"] == 5
    
    def test_search_accuracy(self, temp_dir, sample_docs):
        """Test search accuracy (target >=95%)."""
        db_path = Path(temp_dir) / "rag.db"
        index_dir = Path(temp_dir) / "indices"
        
        engine = RAGEngine(db_path=str(db_path), index_dir=str(index_dir))
        
        engine.import_directory(sample_docs, collection="test_docs", incremental=False)
        
        # Test queries with expected results
        test_cases = [
            ("What is artificial intelligence?", "ai_intro.txt"),
            ("Machine learning and training data", "ml_basics.txt"),
            ("Neural networks and transformers", "deep_learning.txt"),
            ("Natural language processing NLP tasks", "nlp_intro.txt"),
            ("Retrieval augmented generation facts", "rag_systems.txt"),
            ("What is AI?", "ai_intro.txt"),
            ("neural network deep learning", "deep_learning.txt"),
            ("text translation sentiment analysis", "nlp_intro.txt"),
            ("hallucinations knowledge base", "rag_systems.txt"),
            ("predictions mathematical model", "ml_basics.txt"),
        ]
        
        correct = 0
        total = len(test_cases)
        
        for query, expected_file in test_cases:
            results = engine.search(query, collection="test_docs", top_k=1)
            if results and results[0]["file_name"] == expected_file:
                correct += 1
            else:
                print(f"❌ Query '{query}': expected {expected_file}, "
                      f"got {results[0]['file_name'] if results else 'None'}")
        
        accuracy = correct / total
        print(f"\n✅ Search Accuracy: {accuracy:.2%} ({correct}/{total})")
        
        # Must meet >=95% accuracy target
        assert accuracy >= 0.95, f"Accuracy {accuracy:.2%} below 95% target"
    
    def test_incremental_import(self, temp_dir, sample_docs):
        """Test incremental import skips unchanged files."""
        db_path = Path(temp_dir) / "rag.db"
        index_dir = Path(temp_dir) / "indices"
        
        engine = RAGEngine(db_path=str(db_path), index_dir=str(index_dir))
        
        # First import
        result1 = engine.import_directory(sample_docs, collection="test", incremental=True)
        assert result1["imported"] == 5
        assert result1["skipped"] == 0
        
        # Second import (should skip all)
        result2 = engine.import_directory(sample_docs, collection="test", incremental=True)
        assert result2["imported"] == 0
        assert result2["skipped"] == 5
    
    def test_multi_collection_search(self, temp_dir, sample_docs):
        """Test search across multiple collections."""
        db_path = Path(temp_dir) / "rag.db"
        index_dir = Path(temp_dir) / "indices"
        
        engine = RAGEngine(db_path=str(db_path), index_dir=str(index_dir))
        
        engine.import_directory(sample_docs, collection="coll1", incremental=False)
        engine.import_directory(sample_docs, collection="coll2", incremental=False)
        
        # Search across all collections
        results = engine.search("machine learning", collection=None, top_k=10)
        
        # Should have results from both collections
        collections_found = {r["collection"] for r in results}
        assert "coll1" in collections_found
        assert "coll2" in collections_found
    
    def test_get_stats(self, temp_dir, sample_docs):
        """Test getting engine statistics."""
        db_path = Path(temp_dir) / "rag.db"
        index_dir = Path(temp_dir) / "indices"
        
        engine = RAGEngine(db_path=str(db_path), index_dir=str(index_dir))
        engine.import_directory(sample_docs, collection="test", incremental=False)
        
        stats = engine.get_stats()
        
        assert stats["collections_count"] == 1
        assert stats["total_documents"] == 5
        assert stats["total_chunks"] >= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
