"""Índice léxico: BM25Okapi (rank-bm25) sobre los mismos campos que el denso.
Tokeniza con `_fold()` (minúsculas + sin acentos) para que "analitica" y
"analítica" caigan en el mismo token — misma normalización que enrichment.py."""
from rank_bm25 import BM25Okapi

from src.adapters.repository.enrichment import _fold
from src.ports.lexical_index import LexicalIndex


def _tokenize(text: str) -> list:
    return _fold(text or "").split()


class BM25Index(LexicalIndex):
    def __init__(self):
        self._refs = ()
        self._bm25 = None

    def build(self, refs: tuple, texts: tuple) -> None:
        self._refs = tuple(refs)
        corpus = [_tokenize(t) for t in texts]
        self._bm25 = BM25Okapi(corpus)

    def search(self, query: str, k: int = 10) -> tuple:
        if not self._refs:
            return ()
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return tuple((self._refs[i], float(scores[i])) for i in ranked if scores[i] > 0)
