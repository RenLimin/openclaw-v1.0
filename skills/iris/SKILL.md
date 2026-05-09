# Iris RAG Engine Skill 🐦‍⬛

**Skill Name**: iris-rag-engine
**Version**: 1.0.0
**Author**: Iris 🐦‍⬛
**Category**: Knowledge Management

## Overview

Iris is a lightweight, fast private knowledge base engine designed for the OpenClaw multi-agent system. It provides vector-based semantic search across documents with zero LLM inference overhead in retrieval mode.

## Capabilities

### 1. Vector Retrieval Layer
- FAISS high-performance index with L2 / Cosine similarity options
- SQLite metadata storage (integrated with delivery_management.db schema)
- Top-k retrieval with configurable similarity thresholds
- Index persistence with auto-save on modification

### 2. Document Processing Pipeline
- Multi-format document parsing (TXT, MD, PDF, DOCX, Excel)
- Intelligent text chunking with semantic sentence boundaries
- Rich metadata extraction and attachment
- Batch directory import with progress tracking

### 3. Search and Management API
- Pure vector search with no LLM dependency
- Standardized JSON output format
- Cross-collection multi-domain search
- Incremental update with file hash change detection

## Dependencies

```
faiss-cpu>=1.8.0
numpy>=1.24.0
sentence-transformers>=2.2.0
PyPDF2>=3.0.0
python-docx>=1.0.0
openpyxl>=3.1.0
click>=8.1.0
```

## CLI Interface

**Entry Point**: `python -m skills.iris <command>`

### Commands

| Command | Description |
|---------|-------------|
| `import --path <path> --collection <name>` | Import file/directory to collection |
| `search "<query>" [--collection <name>] [--top-k N]` | Search knowledge base |
| `list` | List all collections with statistics |
| `stats` | Show engine-wide statistics |
| `create --name <name> [--description <desc>]` | Create new collection |
| `delete --collection <name> --path <path>` | Delete document from collection |

## Examples

```bash
# Import product documentation
python -m skills.iris import --path ./docs/products --collection products

# Search for product information
python -m skills.iris search "delivery time estimates" --collection products --top-k 5

# List all knowledge collections
python -m skills.iris list
```

## Integration with OpenClaw

This skill integrates with the `delivery_management.db` database, adding RAG-specific tables:
- `rag_collections` - Knowledge base collections
- `rag_documents` - Document metadata
- `rag_chunks` - Text chunks with vector references

## Performance Targets

- **Accuracy**: ≥95% retrieval accuracy on test queries
- **Latency**: < 50ms per search query
- **Throughput**: ≥100 documents/min import speed

## Skill Vetting Score Target

**Target Score**: ≥80/100

## Version History

- **v1.0.0** (2026-05-06): Initial release with full feature set
