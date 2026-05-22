from __future__ import annotations

from vector_db.config import load_settings
from vector_db.document_builder import build_row_documents, build_table_document
from vector_db.duckdb_reader import connect_duckdb, load_table_rows
from vector_db.embeddings import OpenAIEmbedder, SentenceTransformersEmbedder
from vector_db.metadata import load_gold_models
from vector_db.qdrant_store import QdrantStore


def _build_embedder(settings):
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "EMBEDDING_PROVIDER=openai requires OPENAI_API_KEY in .env"
            )
        return OpenAIEmbedder(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    return SentenceTransformersEmbedder(model_name=settings.embedding_model)


def _batched(items, batch_size: int):
    for start in range(0, len(items), batch_size):
        yield start, items[start : start + batch_size]


def run_indexing(delete_before_upsert: bool = False) -> dict[str, int]:
    settings = load_settings()
    print(f"Loading gold model metadata from {settings.gold_schema_yml}", flush=True)
    models = load_gold_models(settings.gold_schema_yml)
    print(f"Preparing embedder using provider={settings.embedding_provider}", flush=True)
    embedder = _build_embedder(settings)
    store = QdrantStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection=settings.qdrant_collection,
        local_path=settings.qdrant_local_path,
    )
    print("Ensuring Qdrant collection exists", flush=True)
    store.ensure_collection(vector_size=embedder.dimension)

    print(f"Opening DuckDB at {settings.duckdb_path}", flush=True)
    conn = connect_duckdb(str(settings.duckdb_path))
    table_doc_count = 0
    row_doc_count = 0

    for index, model in enumerate(models, start=1):
        print(f"[{index}/{len(models)}] Reading {model.name}", flush=True)
        table_data = load_table_rows(
            conn=conn, model_name=model.name, row_limit=settings.row_limit_per_table
        )
        print(
            f"[{index}/{len(models)}] Building documents for {model.name} ({len(table_data.rows)} rows)",
            flush=True,
        )
        table_doc = build_table_document(model, source_schema=table_data.schema_name)
        row_docs = build_row_documents(
            model,
            table_data.rows,
            source_schema=table_data.schema_name,
        )
        docs = [table_doc, *row_docs]

        if delete_before_upsert:
            print(f"[{index}/{len(models)}] Clearing existing points for {model.name}", flush=True)
            store.delete_by_source_table(model.name)

        print(
            f"[{index}/{len(models)}] Embedding and upserting {len(docs)} documents in batches of {settings.index_batch_size}",
            flush=True,
        )
        for batch_number, (start, doc_batch) in enumerate(
            _batched(docs, settings.index_batch_size), start=1
        ):
            print(
                f"[{index}/{len(models)}] {model.name} batch {batch_number} docs {start + 1}-{start + len(doc_batch)}",
                flush=True,
            )
            vectors = embedder.embed([doc.text for doc in doc_batch])
            store.upsert_documents(doc_batch, vectors)
        print(f"[{index}/{len(models)}] Done {model.name}", flush=True)

        table_doc_count += 1
        row_doc_count += len(row_docs)

    conn.close()
    print("Indexing complete", flush=True)
    return {"table_docs": table_doc_count, "row_docs": row_doc_count}
