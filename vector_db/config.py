from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_root: Path
    duckdb_path: Path
    gold_schema_yml: Path
    qdrant_url: str
    qdrant_api_key: str | None
    qdrant_local_path: Path
    qdrant_collection: str
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
    openai_api_key: str | None
    groq_api_key: str | None
    groq_base_url: str
    chat_model: str
    row_limit_per_table: int | None
    index_batch_size: int


def _getenv(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def _resolve_path(raw_path: str, project_root: Path) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    root_relative = (project_root / candidate).resolve()
    if root_relative.exists():
        return root_relative
    dbt_relative = (project_root / "dbt_duckdb" / candidate).resolve()
    return dbt_relative


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    duckdb_env = os.getenv("DUCKDB_PATH", "warehouse/data/bronze_warehouse.duckdb")
    duckdb_path = _resolve_path(duckdb_env, project_root)

    gold_schema_env = os.getenv(
        "GOLD_SCHEMA_YML_PATH", "dbt_duckdb/models/gold/gold_schema.yml"
    )
    gold_schema_path = _resolve_path(gold_schema_env, project_root)

    return Settings(
        project_root=project_root,
        duckdb_path=duckdb_path,
        gold_schema_yml=gold_schema_path,
        qdrant_url=_getenv("QDRANT_URL", "CLUSTER_URL", default="http://localhost:6333"),
        qdrant_api_key=_getenv("QDRANT_API_KEY", "API_KEY"),
        qdrant_local_path=Path(
            _getenv("QDRANT_LOCAL_PATH", default=str(project_root / ".qdrant_local"))
        ),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "gold_knowledge"),
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "sentence_transformers"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_base_url=os.getenv(
            "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
        ),
        chat_model=os.getenv("CHAT_MODEL", "openai/gpt-oss-20b"),
        row_limit_per_table=(int(os.getenv("ROW_LIMIT_PER_TABLE", "0")) or None),
        index_batch_size=int(os.getenv("INDEX_BATCH_SIZE", "256")),
    )
