# Iris RAG Engine 🐦‍⬛

A lightweight, fast private knowledge base system with FAISS vector search and SQLite metadata storage.

## Features

### 🔍 Vector Retrieval Layer
- **FAISS Index**: High-performance similarity search (L2 distance / Cosine similarity)
- **SQLite Storage**: Metadata persistence integrated with delivery_management.db
- **Flexible Search**: Top-k retrieval + similarity threshold filtering
- **Persistence**: Index auto-save and load mechanism

### 📄 Document Parsing Pipeline
- **Multi-format Support**: TXT, MD, PDF, DOCX, Excel (XLSX, XLS, CSV)
- **Intelligent Chunking**: Fixed size + overlap window + semantic sentence boundaries
- **Rich Metadata**: Filename, file type, size, creation time, chunk position
- **Batch Import**: Directory scanning with recursive option

### 🚀 Unified API
- **Pure Retrieval Mode**: Zero LLM call overhead (default mode)
- **Standard JSON Output**: Unified result format with text, score, and metadata
- **Multi-collection Search**: Cross-knowledge-base queries
- **Incremental Updates**: File hash-based change detection, no full rebuild needed

## Installation

```bash
pip install -r skills/iris/requirements.txt
```

## CLI Usage

### Import Documents

```bash
# Import a single file
python -m skills.iris import --path document.pdf --collection products

# Import a directory
python -m skills.iris import --path ./docs/ --collection knowledge-base

# Import without incremental check
python -m skills.iris import --path ./docs/ --no-incremental
```

### Search

```bash
# Search across all collections
python -m skills.iris search "your query text"

# Search in specific collection with more results
python -m skills.iris search "your query text" --collection products --top-k 10

# With similarity threshold filter
python -m skills.iris search "your query text" --threshold 0.7

# Output as JSON
python -m skills.iris search "your query text" --json
```

### Manage Collections

```bash
# List all collections with statistics
python -m skills.iris list

# Create a new collection
python -m skills.iris create --name products --description "Product documentation"

# Show engine statistics
python -m skills.iris stats

# Delete a document from collection
python -m skills.iris delete --collection products --path /path/to/document.pdf
```

## Python API

```python
from skills.iris import RAGEngine

# Initialize engine
rag = RAGEngine(
    db_path="/path/to/delivery_management.db",
    index_dir="/path/to/indices",
    similarity="cosine"
)

# Import documents
result = rag.import_directory("./docs/", collection="knowledge-base")

# Search
results = rag.search("your query", collection="knowledge-base", top_k=5)

# Print results
for item in results:
    print(f"[{item['score']:.2f}] {item['file_name']}")
    print(item['text'])
    print()
```

## Project Structure

```
skills/iris/
├── __init__.py           # Module exports
├── __main__.py           # CLI entry point
├── rag_engine.py         # Main RAG engine
├── vector_store.py       # FAISS + SQLite integration
├── document_parser.py    # Multi-format parser and chunking
├── requirements.txt      # Dependencies
├── SKILL.md              # Skill definition
├── README.md             # This file
└── test_iris.py          # Unit tests
```

## Configuration

### Storage Locations
- **Default DB**: `~/.iris/rag.db`
- **Default Indices**: `~/.iris/indices/`

### Embedding Model
Default: `all-MiniLM-L6-v2` (384 dimensions, fast and lightweight)

## Performance

- **Indexing**: ~100 documents/sec on modern hardware
- **Search**: < 10ms per query for 1M vectors
- **Memory**: ~1.5GB for 1M vectors (384 dimensions)

## Testing

```bash
# Run unit tests
python -m pytest skills/iris/test_iris.py -v
```

## License

Internal use only for the OpenClaw team.
