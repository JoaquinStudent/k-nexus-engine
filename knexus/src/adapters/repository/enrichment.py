"""Enriquecimiento de entidades: methods, problem_types, keywords, domains.

Deriva señales a partir del texto crudo del dataset (que el MD del NEED-001
declara explícitamente que no prescribe método) usando el vocabulario
controlado de `vocabulary.py`. Vive en adapters/, no en domain/: el dominio
sólo consume las tuplas ya resueltas (Regla A1).
"""
import unicodedata

from src.adapters.repository.vocabulary import METHOD_PHRASES, NEED_SECTOR_PHRASES, PROBLEM_TYPE_PHRASES


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


def split_keywords(value: str) -> tuple:
    if not value:
        return ()
    return tuple(kw.strip() for kw in value.split(";") if kw.strip())


def extract_domains(*values: str) -> tuple:
    domains = []
    for value in values:
        for part in split_keywords(value) if ";" in (value or "") else ([value] if value else []):
            if part and part not in domains:
                domains.append(part)
    return tuple(domains)
