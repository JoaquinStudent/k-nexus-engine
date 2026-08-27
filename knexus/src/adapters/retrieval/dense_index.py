"""Índice denso: FAISS IndexFlatIP sobre vectores L2-normalizados (= coseno).
Si `faiss` no importa en este entorno, cae a búsqueda exacta con numpy — mismo
resultado matemático, porque IndexFlatIP ya es una búsqueda exhaustiva."""
import os

# ponytail: faiss y torch (sentence-transformers) empaquetan cada uno su
# propio runtime OpenMP; cargar ambos en el mismo proceso en macOS aborta con
# SIGABRT ("OMP: Error #15") al registrar el segundo. Es inocuo declarar que
# se tolera — ninguno de los dos usa paralelismo OpenMP dentro del otro aquí.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np

from src.adapters.retrieval import vector_cache
from src.ports.vector_index import VectorIndex

try:
    import faiss
    _HAS_FAISS = True
except ImportError:  # Regla A4: degradación sin la dependencia nativa
    _HAS_FAISS = False


class DenseIndex(VectorIndex):
    def __init__(self, embedding_provider):
        self._provider = embedding_provider
        self._refs = ()
        self._vectors = None
        self._faiss_index = None

    def build(self, refs: tuple, texts: tuple, *, use_cache: bool = True) -> None:
        self._refs = tuple(refs)
        texts = tuple(texts)
        cached = vector_cache.load(self._provider.name, texts) if use_cache else None
        if cached is not None:
            vectors = cached.astype("float32")
        else:
            vectors = self._provider.encode(texts).astype("float32")
            if use_cache:
                vector_cache.save(self._provider.name, texts, vectors)
        self._vectors = vectors
        if _HAS_FAISS:
            index = faiss.IndexFlatIP(vectors.shape[1])
            index.add(vectors)
            self._faiss_index = index

    def search(self, query: str, k: int = 10) -> tuple:
        if not self._refs:
            return ()
        q = self._provider.encode((query,)).astype("float32")
        k = min(k, len(self._refs))
        if _HAS_FAISS:
            scores, indices = self._faiss_index.search(q, k)
            pairs = list(zip(indices[0], scores[0]))
        else:
            sims = (self._vectors @ q[0])
            top = np.argsort(-sims)[:k]
            pairs = [(int(i), float(sims[i])) for i in top]
        return tuple((self._refs[i], float(s)) for i, s in pairs if i >= 0)
