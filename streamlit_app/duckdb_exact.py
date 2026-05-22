from __future__ import annotations

from typing import Any

import duckdb
from vector_db.config import load_settings
from vector_db.duckdb_reader import connect_duckdb, detect_schema_for_model


KEY_FIELDS = ("website_name", "check_date", "check_hour", "domain", "website_key")

from dotenv import load_dotenv
load_dotenv()


def fetch_exact_row(payload: dict[str, Any]) -> dict[str, Any] | None:
    model_name = payload.get("source_table")
    if not model_name:
        return None

    filters = {k: payload[k] for k in KEY_FIELDS if k in payload}
    if not filters:
        return None

    settings = load_settings()
    conn = connect_duckdb(str(settings.duckdb_path))

    try:
        where = " AND ".join(f'CAST("{k}" AS VARCHAR) = ?' for k in filters)
        values = [str(value) for value in filters.values()]

        candidate_schemas: list[str] = []
        source_schema = payload.get("source_schema")
        if source_schema:
            candidate_schemas.append(str(source_schema))

        detected_schema = detect_schema_for_model(conn, model_name)
        if detected_schema not in candidate_schemas:
            candidate_schemas.append(detected_schema)

        for schema_name in candidate_schemas:
            query = f'SELECT * FROM "{schema_name}"."{model_name}" WHERE {where} LIMIT 1'
            try:
                result = conn.execute(query, values).fetchone()
            except duckdb.CatalogException:
                continue
            if result is None:
                continue

            columns = [d[0] for d in conn.description]
            return dict(zip(columns, result, strict=True))

        return None
    finally:
        conn.close()
