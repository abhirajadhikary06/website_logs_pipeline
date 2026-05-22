from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from vector_db.config import load_settings
from vector_db.embeddings import OpenAIEmbedder, SentenceTransformersEmbedder
from vector_db.qdrant_store import QdrantStore

from dotenv import load_dotenv
load_dotenv()
@dataclass(frozen=True)
class RetrievedContext:
    score: float
    text: str
    payload: dict[str, Any]


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


def retrieve(question: str, limit: int = 6) -> list[RetrievedContext]:
    settings = load_settings()
    embedder = _build_embedder(settings)
    store = QdrantStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection=settings.qdrant_collection,
        local_path=settings.qdrant_local_path,
    )
    query_vector = embedder.embed([question])[0]
    hits = store.search(query_vector=query_vector, limit=limit)

    return [
        RetrievedContext(
            score=float(hit.score),
            text=str(hit.payload.get("text", "")),
            payload=dict(hit.payload),
        )
        for hit in hits
    ]
