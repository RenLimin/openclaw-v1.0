"""
CLI entry point for Iris RAG Engine.

Usage:
    python -m skills.iris import --path docs/ --collection products
    python -m skills.iris search "query text" --collection products --top-k 10
    python -m skills.iris list
    python -m skills.iris stats
"""
import click
import json
import sys
from pathlib import Path

# Add workspace to path for imports
workspace = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace))

from skills.iris.rag_engine import RAGEngine


@click.group()
@click.option("--db-path", help="Path to SQLite database file")
@click.option("--index-dir", help="Directory for FAISS index files")
@click.pass_context
def cli(ctx, db_path, index_dir):
    """Iris RAG Engine - Private Knowledge Base System"""
    ctx.ensure_object(dict)
    ctx.obj["db_path"] = db_path
    ctx.obj["index_dir"] = index_dir


def get_engine(ctx):
    """Get RAG engine instance from context."""
    return RAGEngine(
        db_path=ctx.obj.get("db_path"),
        index_dir=ctx.obj.get("index_dir")
    )


@cli.command()
@click.option("--path", "-p", required=True, help="File or directory path to import")
@click.option("--collection", "-c", default="default", help="Collection name")
@click.option("--recursive/--no-recursive", default=True, help="Scan subdirectories")
@click.option("--incremental/--no-incremental", default=True, help="Skip unchanged files")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def import_cmd(ctx, path, collection, recursive, incremental, output_json):
    """Import documents into knowledge base"""
    engine = get_engine(ctx)
    path_obj = Path(path)
    
    if path_obj.is_file():
        result = engine.import_file(
            file_path=str(path_obj),
            collection=collection,
            incremental=incremental
        )
        if output_json:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if result["status"] == "imported":
                click.echo(f"✅ Imported: {result['file']} ({result['chunks']} chunks)")
            elif result["status"] == "skipped":
                click.echo(f"⏭️  Skipped: {result['file']} (unchanged)")
            else:
                click.echo(f"⚠️  Empty: {result['file']}")
    elif path_obj.is_dir():
        result = engine.import_directory(
            dir_path=str(path_obj),
            collection=collection,
            recursive=recursive,
            incremental=incremental
        )
        if output_json:
            click.echo(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            click.echo(f"\n📦 Import to collection: {collection}")
            click.echo(f"   Total files: {result['total']}")
            click.echo(f"   Imported: {result['imported']}")
            click.echo(f"   Skipped: {result['skipped']}")
            click.echo(f"   Failed: {result['failed']}")
            click.echo(f"   Total chunks: {result['total_chunks']}")
    else:
        click.echo(f"❌ Path not found: {path}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--collection", "-c", help="Collection to search (all if not specified)")
@click.option("--top-k", "-k", type=int, default=5, help="Number of results")
@click.option("--threshold", "-t", type=float, help="Similarity threshold")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def search(ctx, query, collection, top_k, threshold, output_json):
    """Search the knowledge base"""
    engine = get_engine(ctx)
    results = engine.search(
        query=query,
        collection=collection,
        top_k=top_k,
        threshold=threshold
    )
    
    if output_json:
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            click.echo("No results found.")
            return
        
        click.echo(f"\n🔍 Search results for: '{query}'")
        click.echo(f"   Collection: {collection or 'All'}")
        click.echo(f"   Results: {len(results)}\n")
        
        for i, result in enumerate(results, 1):
            score_pct = result['score'] * 100
            click.echo(f"{i}. [{score_pct:.1f}%] {result['file_name']} ({result['collection']})")
            click.echo(f"   {result['text'][:200]}{'...' if len(result['text']) > 200 else ''}")
            click.echo()


@cli.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_cmd(ctx, output_json):
    """List all collections"""
    engine = get_engine(ctx)
    collections = engine.list_collections()
    
    if output_json:
        click.echo(json.dumps(collections, indent=2, ensure_ascii=False))
    else:
        if not collections:
            click.echo("No collections found.")
            return
        
        click.echo("\n📚 Collections:")
        for coll in collections:
            click.echo(f"  • {coll['name']}")
            click.echo(f"    Documents: {coll['doc_count']}, Chunks: {coll['chunk_count']}")
            if coll['description']:
                click.echo(f"    {coll['description']}")
            click.echo()


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def stats(ctx, output_json):
    """Show RAG engine statistics"""
    engine = get_engine(ctx)
    stats_data = engine.get_stats()
    
    if output_json:
        click.echo(json.dumps(stats_data, indent=2, ensure_ascii=False))
    else:
        click.echo("\n📊 Iris RAG Engine Statistics")
        click.echo("=" * 40)
        click.echo(f"  Database: {stats_data['db_path']}")
        click.echo(f"  Index Directory: {stats_data['index_dir']}")
        click.echo(f"  Collections: {stats_data['collections_count']}")
        click.echo(f"  Total Documents: {stats_data['total_documents']}")
        click.echo(f"  Total Chunks: {stats_data['total_chunks']}")
        click.echo()


@cli.command()
@click.option("--name", "-n", required=True, help="Collection name")
@click.option("--description", "-d", default="", help="Collection description")
@click.pass_context
def create(ctx, name, description):
    """Create a new collection"""
    engine = get_engine(ctx)
    if engine.create_collection(name, description):
        click.echo(f"✅ Collection '{name}' created successfully.")
    else:
        click.echo(f"⚠️  Collection '{name}' already exists.")


@cli.command()
@click.option("--collection", "-c", required=True, help="Collection name")
@click.option("--path", "-p", required=True, help="File path to delete")
@click.pass_context
def delete(ctx, collection, path):
    """Delete a document from a collection"""
    engine = get_engine(ctx)
    if engine.delete_document(collection, path):
        click.echo(f"✅ Document deleted from collection '{collection}'.")
    else:
        click.echo(f"⚠️  Document not found in collection '{collection}'.")


if __name__ == "__main__":
    cli()
