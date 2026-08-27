"""Adapter de degradación (Regla A4) — texto → vector determinista, sin red ni
descarga de modelo. Permite correr toda la suite y la demo offline si el
`SentenceTransformerProvider` no está disponible (sin internet, sin torch)."""
import hashlib

import numpy as np

from src.adapters.repository.enrichment import _fold
from src.ports.embedding_provider import EmbeddingProvider

_NGRAM = 3


def _hash_vector(text: str, dim: int) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float64)
    folded = _fold(text)
    tokens = folded.split() or [folded]
    grams = set()
    for token in tokens:
        padded = f"#{token}#"
        for i in range(len(padded) - _NGRAM + 1):
            grams.add(padded[i:i + _NGRAM])
    if not grams:
        grams = {folded or "#"}
    for gram in grams:
        digest = hashlib.sha256(gram.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


class HashingProvider(EmbeddingProvider):
    """Char-ngram hashing multilingüe-agnóstico: no capta similitud semántica
    ES↔EN (eso exige el modelo real), pero sí similitud léxica/morfológica y es
    perfectamente determinista y auditable."""

    def __init__(self, dim: int = 256):
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return f"hashing-{self._dim}"

    def encode(self, texts: tuple) -> np.ndarray:
        return np.array([_hash_vector(t, self._dim) for t in texts], dtype=np.float64)
