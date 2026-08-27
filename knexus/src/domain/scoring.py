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
    return sum(weight * getattr(fv, name) for name, weight in WEIGHTS.items())
