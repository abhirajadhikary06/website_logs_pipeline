from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class ColumnMeta:
    name: str
    description: str


@dataclass(frozen=True)
class ModelMeta:
    name: str
    description: str
    columns: list[ColumnMeta]


def load_gold_models(schema_yml_path: Path) -> list[ModelMeta]:
    content = yaml.safe_load(schema_yml_path.read_text(encoding="utf-8"))
    models = content.get("models", [])
    out: list[ModelMeta] = []

    for model in models:
        columns = [
            ColumnMeta(name=c["name"], description=c.get("description", ""))
            for c in model.get("columns", [])
        ]
        out.append(
            ModelMeta(
                name=model["name"],
                description=model.get("description", ""),
                columns=columns,
            )
        )
    return out
