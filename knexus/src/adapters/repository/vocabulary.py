"""Re-exporta `src.domain.vocabulary` (movido ahí en Sprint-04, Regla A2).

Se mantiene este módulo para no romper los import existentes de Sprint-02/03
(`capability_match.py`, `tests/adapters/test_ingestion.py`). El vocabulario
en sí vive en `domain/vocabulary.py` — ver ese archivo para el porqué del
movimiento.
"""
from src.domain.vocabulary import (  # noqa: F401
    METHOD_PHRASES,
    METHOD_TAGS,
    NEED_SECTOR_PHRASES,
    PROBLEM_TYPE_PHRASES,
    PROBLEM_TYPE_TAGS,
    SECTORS,
)
