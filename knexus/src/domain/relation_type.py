"""Tipado de la conexión a partir del vector de features. PURO (Regla A1)."""
from src.domain.models import FeatureVector

ALTO = 0.6
CURRICULAR_TYPES = ("subject", "competency")


def classify_relation(fv: FeatureVector, candidate_entity_type: str) -> str:
    if candidate_entity_type in CURRICULAR_TYPES:
        return "integracion_curricular"
    if candidate_entity_type == "researcher" and fv.enlace_estructural >= ALTO:
        return "investigador_complementario"
    if fv.soporte_capacidad >= ALTO and fv.compat_metodo < ALTO and fv.compat_dominio < ALTO:
        return "activacion_capacidad"
    if fv.compat_metodo >= ALTO and fv.densidad_evidencia >= ALTO:
        return "antecedente_metodologico"
    if fv.compat_dominio >= ALTO and fv.sim_semantica >= ALTO:
        return "antecedente_relevante"
    # ponytail: cualquier resto (solo sim_lexica/sim_semantica altas, resto bajo)
    # cae aquí por diseño — coincidir en tema/texto sin método, dominio, capacidad
    # ni enlace estructural es la trampa que el reto pide no premiar.
    return "coincidencia_superficial"
