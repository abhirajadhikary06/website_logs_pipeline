# Streamlit Retrieval App

## What it does
- Embeds user question
- Searches Qdrant `gold_knowledge` collection
- Routes result by `doc_type`
- For row-level hits, does exact lookup in DuckDB using row keys from payload

## Run app
```powershell
streamlit run streamlit_app/app.py
```

## Typical flow
1. Run dbt gold models so DuckDB has fresh gold tables.
2. Run indexing from `vector_db`.
3. Start Streamlit and ask questions.
