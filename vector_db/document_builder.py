from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from vector_db.metadata import ModelMeta


@dataclass(frozen=True)
class Document:
    point_id: str
    text: str
    payload: dict[str, Any]


KEY_FIELD_CANDIDATES = (
    "website_name",
    "check_date",
    "check_hour",
    "domain",
    "website_key",
)


def _infer_grain(model_name: str) -> str:
    if model_name == "gold_hourly_performance":
        return "website_name + check_date + check_hour"
    if model_name == "gold_sla_monitoring":
        return "website_name + check_date"
    if model_name in {"gold_website_rankings", "gold_website_health_summary"}:
        return "website_name"
    if model_name == "gold_error_trends":
        return "check_date"
    if model_name == "gold_executive_kpis":
        return "single snapshot row"
    return "table specific grain"


def _payload_row_keys(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in KEY_FIELD_CANDIDATES:
        if key in row and row[key] is not None:
            out[key] = str(row[key])
    return out


def _stable_row_hash(row: dict[str, Any]) -> str:
    canonical = json.dumps(row, sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()


def build_table_document(model: ModelMeta, source_schema: str) -> Document:
    column_text = "\n".join(
        f"- {column.name}: {column.description}" for column in model.columns
    )
    grain = _infer_grain(model.name)
    text = (
        f"Model: {model.name}\n"
        f"Type: Gold analytics table\n"
        f"Purpose: {model.description}\n"
        f"Grain: {grain}\n"
        "Columns:\n"
        f"{column_text}\n"
        "Business use: supports analytics, monitoring, and KPI questions."
    )
    payload = {
        "model_name": model.name,
        "doc_type": "table",
        "source_table": model.name,
        "source_schema": source_schema,
        "grain": grain,
    }
    return Document(point_id=f"table::{model.name}", text=text, payload=payload)


def build_row_documents(
    model: ModelMeta,
    rows: list[dict[str, Any]],
    source_schema: str,
) -> list[Document]:
    grain = _infer_grain(model.name)
    docs: list[Document] = []
    for row in rows:
        row_pairs = ", ".join(f"{k}={v}" for k, v in row.items())
        row_hash = _stable_row_hash(row)
        text = (
            f"Model {model.name} row summary. "
            f"Grain {grain}. "
            f"Values: {row_pairs}."
        )
        payload = {
            "model_name": model.name,
            "doc_type": "row",
            "source_table": model.name,
            "source_schema": source_schema,
            "grain": grain,
            "row_hash": row_hash,
            **_payload_row_keys(row),
        }
        docs.append(
            Document(point_id=f"row::{model.name}::{row_hash}", text=text, payload=payload)
        )
    return docs
