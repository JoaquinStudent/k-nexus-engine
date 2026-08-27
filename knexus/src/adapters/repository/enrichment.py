"""Enriquecimiento de entidades: methods, problem_types, keywords, domains.

El matching de texto contra vocabulario (`_fold`, `mine_methods`,
`infer_problem_types`, `infer_sectors`) vive en `src.domain.text_matching`
desde Sprint-04 (Regla A2) y se re-exporta aquí para no romper los import
existentes. Lo que se queda en este módulo es específico de la ingesta CSV:
`split_keywords`/`extract_domains` operan sobre la convención de columnas del
dataset (semicolon-separated), no sobre vocabulario puro.
"""
from src.domain.text_matching import (  # noqa: F401
    _fold,
    _match_phrases,
    infer_problem_types,
    infer_sectors,
    mine_methods,
)


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
