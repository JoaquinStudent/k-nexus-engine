"""Métricas de recuperación (Sprint-07). PURAS: sólo listas/sets de
`entity_id`, sin pipeline ni dataset — testeables en aislamiento
(`tests/evaluation/test_metrics.py`)."""


def precision_at_k(ranked: list, relevant: set, k: int) -> float:
    """`k` es siempre el denominador, incluso si `ranked` trae menos de `k`
    candidatos — un ranking corto no debe inflar la precisión."""
    if k <= 0:
        return 0.0
    top_k = ranked[:k]
    hits = sum(1 for entity_id in top_k if entity_id in relevant)
    return hits / k


def recall_at_k(ranked: list, relevant: set, k: int) -> float:
    """Nunca puede exceder `k / len(relevant)` — ese es el TECHO que hay que
    reportar junto al número, no esconder (SPEC.md §13)."""
    if not relevant:
        return 0.0
    hits = sum(1 for entity_id in ranked[:k] if entity_id in relevant)
    return hits / len(relevant)


def mrr(ranked: list, relevant: set) -> float:
    """Reciprocal rank del primer elemento relevante; 0.0 si ninguno aparece."""
    for position, entity_id in enumerate(ranked, start=1):
        if entity_id in relevant:
            return 1.0 / position
    return 0.0


def mean(values: list) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
