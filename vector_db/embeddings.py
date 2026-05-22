from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    @property
    def dimension(self) -> int: ...

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class SentenceTransformersEmbedder:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        get_dim = getattr(self._model, "get_embedding_dimension", None)
        if callable(get_dim):
            self._dimension = int(get_dim())
        else:
            self._dimension = int(self._model.get_sentence_embedding_dimension())

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]


class OpenAIEmbedder:
    def __init__(self, api_key: str, model_name: str, dimension: int) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model_name = model_name
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self._model_name, input=texts)
        return [item.embedding for item in response.data]
