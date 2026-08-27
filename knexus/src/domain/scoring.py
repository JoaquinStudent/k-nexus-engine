"""Combinación ponderada de features → score de relevancia. PURO (Regla A1)."""
from src.domain.models import FeatureVector

WEIGHTS = {
    "compat_metodo": 0.20,
    "compat_dominio": 0.20,
    "sim_semantica": 0.18,
    "soporte_capacidad": 0.15,
    "densidad_evidencia": 0.12,
    "enlace_estructural": 0.10,
    "sim_lexica": 0.05,
}


def compute_score(fv: FeatureVector) -> float:
    # Se excluyen las features N/A (None) y se re-normalizan los pesos restantes a
    # 1.0. Con las 7 features presentes, total == 1.0 → idéntico al cálculo directo.
    active = {name: getattr(fv, name) for name in WEIGHTS if getattr(fv, name) is not None}
    total = sum(WEIGHTS[name] for name in active)
    if not total:
        return 0.0
    return sum(WEIGHTS[name] * active[name] for name in active) / total
