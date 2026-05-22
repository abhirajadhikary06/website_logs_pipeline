from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import duckdb


@dataclass(frozen=True)
class TableData:
    model_name: str
    rows: list[dict[str, Any]]
    schema_name: str


def connect_duckdb(path: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(path)


def detect_schema_for_model(conn: duckdb.DuckDBPyConnection, model_name: str) -> str:
    result = conn.execute(
        """
        SELECT table_schema
        FROM information_schema.tables
        WHERE table_name = ?
        ORDER BY CASE WHEN table_schema = 'gold' THEN 0 ELSE 1 END, table_schema
        LIMIT 1
        """,
        [model_name],
    ).fetchone()
    if result is None:
        raise ValueError(f"Model table not found in DuckDB: {model_name}")
    return str(result[0])


def load_table_rows(
    conn: duckdb.DuckDBPyConnection,
    model_name: str,
    row_limit: int | None = None,
) -> TableData:
    schema_name = detect_schema_for_model(conn, model_name)
    query = f'SELECT * FROM "{schema_name}"."{model_name}"'
    if row_limit:
        query += f" LIMIT {row_limit}"
    rows = conn.execute(query).fetchdf().to_dict(orient="records")
    return TableData(model_name=model_name, rows=rows, schema_name=schema_name)
