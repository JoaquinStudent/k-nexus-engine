"""Cálculo de las 7 features auditables. PURO — sin imports externos (Regla A1)."""
from src.domain.models import CandidatePair, FeatureVector


def _jaccard(a: tuple, b: tuple) -> float:
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def sim_semantica(pair: CandidatePair) -> float:
    return max(0.0, min(1.0, pair.sim_semantic))


def sim_lexica(pair: CandidatePair) -> float:
    return _jaccard(pair.query.keywords, pair.candidate.keywords)


def compat_metodo(pair: CandidatePair) -> float:
    return _jaccard(pair.query.methods, pair.candidate.methods)


def compat_dominio(pair: CandidatePair) -> float:
    return _jaccard(pair.query.domains, pair.candidate.domains)


def densidad_evidencia(pair: CandidatePair) -> float:
    expected = pair.candidate.expected_fields
    if expected <= 0:
        return 0.0
    ratio = len(pair.candidate.filled_fields) / expected
    return max(0.0, min(1.0, ratio))


def soporte_capacidad(pair: CandidatePair) -> float:
    return 1.0 if pair.candidate.has_capability_support else 0.0


def enlace_estructural(pair: CandidatePair) -> float:
    return 1.0 if pair.candidate.graph_linked else 0.0


def compute_features(pair: CandidatePair) -> FeatureVector:
    return FeatureVector(
        sim_semantica=sim_semantica(pair),
        sim_lexica=sim_lexica(pair),
        compat_metodo=compat_metodo(pair),
        compat_dominio=compat_dominio(pair),
        densidad_evidencia=densidad_evidencia(pair),
        soporte_capacidad=soporte_capacidad(pair),
        enlace_estructural=enlace_estructural(pair),
    )
