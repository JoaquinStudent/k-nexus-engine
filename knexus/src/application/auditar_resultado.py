"""Use-case "¿por qué A antes que B?" (módulo M7 de `DESIGN.md`): compara dos
`RankedConnection` de la MISMA consulta feature por feature y señala cuál
explica la mayor parte de la diferencia de score.

Datos estructurados, no prosa — la redacción ("Transferable method + available
capability") es del `Explainer` en Sprint-05.
"""
from dataclasses import dataclass

from src.domain.scoring import WEIGHTS

FEATURE_NAMES = tuple(WEIGHTS.keys())


def _contribution(feature_vector, name: str) -> float:
    """Contribución normalizada de una feature al score de SU candidato (la
    misma que usa `compute_score`); 0.0 si la feature es N/A para ese lado —
    así que sumar las contribuciones de todas las features reproduce el score
    exacto, y el delta por feature reproduce exacto el delta de score."""
    value = getattr(feature_vector, name)
    if value is None:
        return 0.0
    active = {n: getattr(feature_vector, n) for n in WEIGHTS if getattr(feature_vector, n) is not None}
    total_weight = sum(WEIGHTS[n] for n in active)
    if not total_weight:
        return 0.0
    return WEIGHTS[name] * value / total_weight


@dataclass(frozen=True)
class FeatureComparison:
    name: str
    value_a: object  # float o None (N/A)
    value_b: object
    weight: float
    delta: float      # contribución_a - contribución_b; suma exacta = score_a - score_b
    favors: str       # "A", "B" o "empate"


@dataclass(frozen=True)
class ComparisonResult:
    connection_a: object  # RankedConnection
    connection_b: object
    score_delta: float
    features: tuple       # FeatureComparison, ordenadas por |delta| descendente
    dominant_feature: str


def comparar(connection_a, connection_b) -> ComparisonResult:
    fv_a = connection_a.scored.feature_vector
    fv_b = connection_b.scored.feature_vector

    features = []
    for name in FEATURE_NAMES:
        contribution_a = _contribution(fv_a, name)
        contribution_b = _contribution(fv_b, name)
        delta = contribution_a - contribution_b
        favors = "A" if delta > 0 else ("B" if delta < 0 else "empate")
        features.append(FeatureComparison(
            name=name,
            value_a=getattr(fv_a, name),
            value_b=getattr(fv_b, name),
            weight=WEIGHTS[name],
            delta=delta,
            favors=favors,
        ))
    features.sort(key=lambda f: -abs(f.delta))
    dominant = features[0].name if features else ""

    return ComparisonResult(
        connection_a=connection_a,
        connection_b=connection_b,
        score_delta=connection_a.scored.score - connection_b.scored.score,
        features=tuple(features),
        dominant_feature=dominant,
    )
