"""Matching de texto contra el vocabulario controlado (`vocabulary.py`). PURO
— sólo `unicodedata` (stdlib), sin librerías externas (Regla A1).

Movido de `adapters/repository/enrichment.py` a `domain/` en Sprint-04: tanto
la ingesta (un NEED) como una consulta en vivo en texto libre
(`application/query_builder.py`) necesitan inferir `problem_types`/`sectors`
con el mismo mecanismo — vivir en `domain/` es lo que permite a `application/`
usarlo sin depender de un adapter concreto (Regla A2).
"""
import unicodedata

from src.domain.vocabulary import METHOD_PHRASES, NEED_SECTOR_PHRASES, PROBLEM_TYPE_PHRASES


def _fold(text: str) -> str:
    """minúsculas + sin acentos, para matching tolerante a variación tipográfica."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _match_phrases(text: str, phrase_to_tag: dict) -> tuple:
    folded = _fold(text or "")
    found = []
    for phrase, tag in phrase_to_tag.items():
        if _fold(phrase) in folded and tag not in found:
            found.append(tag)
    return tuple(found)


def mine_methods(*texts: str) -> tuple:
    combined = " ".join(t for t in texts if t)
    return _match_phrases(combined, METHOD_PHRASES)


def infer_problem_types(*texts: str) -> tuple:
    combined = " ".join(t for t in texts if t)
    return _match_phrases(combined, PROBLEM_TYPE_PHRASES)


def infer_sectors(*texts: str) -> tuple:
    """ADR-009: sector institucional inferido del texto de un NEED (que no trae
    ninguna columna de dominio) — mismo mecanismo que `infer_problem_types`."""
    combined = " ".join(t for t in texts if t)
    return _match_phrases(combined, NEED_SECTOR_PHRASES)
