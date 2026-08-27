"""Índice denso: FAISS IndexFlatIP sobre vectores L2-normalizados (= coseno).
Si `faiss` no importa en este entorno, cae a búsqueda exacta con numpy — mismo
resultado matemático, porque IndexFlatIP ya es una búsqueda exhaustiva."""
import numpy as np

try:
    import faiss
    _HAS_FAISS = True
except ImportError:  # Regla A4: degradación sin la dependencia nativa
    _HAS_FAISS = False


class DenseIndex:
    def __init__(self, embedding_provider):
        self._provider = embedding_provider
        self._refs = ()
        self._vectors = None
        self._faiss_index = None

    def build(self, refs: tuple, texts: tuple) -> None:
        self._refs = tuple(refs)
        vectors = self._provider.encode(texts).astype("float32")
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
