"""Adapter primario: embeddings multilingües reales vía sentence-transformers.

Modelo: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, ~470MB) en vez de
bge-m3 (~5GB con torch) — decisión de Sprint-03 para iterar rápido en hackathon
sin perder cobertura ES↔EN (L2 de MEMORY.md). Swap de una línea si se necesita
bge-m3 más adelante: cambiar `DEFAULT_MODEL`.
"""
import numpy as np

from src.ports.embedding_provider import EmbeddingProvider

DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str = DEFAULT_MODEL):
        from sentence_transformers import SentenceTransformer  # import perezoso: A4

        self._model_name = model_name
        self._model = SentenceTransformer(model_name)
        self._dim = self._model.get_embedding_dimension()

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return self._model_name

    def encode(self, texts: tuple) -> np.ndarray:
        vectors = self._model.encode(list(texts), normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float64)
