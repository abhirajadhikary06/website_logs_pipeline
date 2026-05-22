# Vector DB Indexing

## What it does
- Reads gold model metadata from `dbt_duckdb/models/gold/gold_schema.yml`
- Reads corresponding gold tables from DuckDB
- Builds:
  - table-level documents (`doc_type=table`)
  - row-level documents (`doc_type=row`)
- Embeds and upserts into one Qdrant collection

## Environment variables
- `DUCKDB_PATH` (already present in `.env`)
- `QDRANT_URL` (default: `http://localhost:6333`)
- `QDRANT_API_KEY` (optional)
- `QDRANT_COLLECTION` (default: `gold_knowledge`)
- `EMBEDDING_PROVIDER` (`sentence_transformers` or `openai`)
- `EMBEDDING_MODEL` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `EMBEDDING_DIMENSION` (only required for OpenAI mode)
- `OPENAI_API_KEY` (required for OpenAI mode)
- `ROW_LIMIT_PER_TABLE` (optional for sampling)

## Run indexing
```powershell
python -m vector_db.main
```

Refresh table-specific points before re-upsert:
```powershell
python -m vector_db.main --refresh
```
