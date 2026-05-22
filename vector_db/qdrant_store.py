from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PayloadSchemaType, PointStruct, VectorParams
from qdrant_client.http.exceptions import ResponseHandlingException

from vector_db.document_builder import Document


def _to_uint64(value: str) -> int:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]
    return int(digest, 16)


class QdrantStore:
    def __init__(
        self,
        url: str,
        api_key: str | None,
        collection: str,
        local_path: str | Path | None = None,
    ) -> None:
        self._remote_client = QdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=False,
            check_compatibility=False,
        )
        self._local_path = Path(local_path) if local_path else None
        self.client = self._remote_client
        self.collection = collection

    def _switch_to_local(self) -> None:
        if self._local_path is None:
            raise RuntimeError("Qdrant remote connection failed and no local fallback path is configured.")
        self.client = QdrantClient(
            path=str(self._local_path),
            prefer_grpc=False,
            check_compatibility=False,
        )

    def _with_local_fallback(self, action):
        try:
            return action()
        except (ResponseHandlingException, ConnectionError, OSError):
            if self.client is self._remote_client and self._local_path is not None:
                self._switch_to_local()
                return action()
            raise

    def ensure_collection(self, vector_size: int) -> None:
        def _ensure() -> None:
            try:
                self.client.get_collection(self.collection)
            except Exception:
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(
                        size=vector_size, distance=Distance.COSINE
                    ),
                )

            self.client.create_payload_index(
                collection_name=self.collection,
                field_name="source_table",
                field_schema=PayloadSchemaType.KEYWORD,
            )

        try:
            self._with_local_fallback(_ensure)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to connect to Qdrant at the configured remote URL and no usable local fallback was available for collection {self.collection!r}."
            ) from exc

    def upsert_documents(self, docs: list[Document], vectors: list[list[float]]) -> None:
        def _upsert() -> None:
            points = [
                PointStruct(
                    id=_to_uint64(doc.point_id),
                    vector=vector,
                    payload={**doc.payload, "text": doc.text, "point_id": doc.point_id},
                )
                for doc, vector in zip(docs, vectors, strict=True)
            ]
            self.client.upsert(collection_name=self.collection, points=points)

        self._with_local_fallback(_upsert)

    def search(
        self,
        query_vector: list[float],
        limit: int = 8,
        filters: dict[str, Any] | None = None,
    ):
        from qdrant_client.http.models import FieldCondition, Filter, MatchValue

        qfilter = None
        if filters:
            qfilter = Filter(
                must=[
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filters.items()
                ]
            )

        def _search():
            response = self.client.query_points(
                collection_name=self.collection,
                query=query_vector,
                query_filter=qfilter,
                limit=limit,
            )
            return response.points

        return self._with_local_fallback(_search)

    def delete_by_source_table(self, source_table: str) -> None:
        from qdrant_client.http.models import FieldCondition, Filter, FilterSelector, MatchValue

        def _delete() -> None:
            self.client.delete(
                collection_name=self.collection,
                points_selector=FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="source_table", match=MatchValue(value=source_table)
                            )
                        ]
                    )
                )
            )

        self._with_local_fallback(_delete)
