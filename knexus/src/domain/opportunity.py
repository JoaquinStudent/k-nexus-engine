"""Reglas de ensamblado de oportunidad. PURO (Regla A1).

Los 4 eslabones de la cadena (necesidad→antecedente→investigador→capacidad→
currículo) NO tienen la misma fuerza probatoria — cada `ChainLink` declara su
`link_type`:
  - "retrieved": salió del reranking de 7 features (el antecedente).
  - "edge": hecho duro — una arista real del grafo o una FK real del dataset
    (investigador vía researcher_project; currículo vía primary_program_id,
    aunque el subject/competency específico se elija por score entre los del
    programa).
  - "inferred": no hay tabla de enlace; se infiere (capacidad, ADR-008).

Presentar los tres como si fueran lo mismo sería la "trazabilidad de mentira"
que la rúbrica penaliza — por eso `link_type` es obligatorio y las reglas de
este módulo lo usan para tipar y priorizar, no solo la UI para colorear.
"""
from dataclasses import dataclass

ALTO = 0.6
MEDIO = 0.4


@dataclass(frozen=True)
class ChainLink:
    role: str                    # necesidad | antecedente | investigador | capacidad | curriculo
    entity_id: str
    entity_type: str
    link_type: str                # retrieved | edge | inferred
    score: float = None            # None si el eslabón es un hecho puro, sin score propio
    relation_type: str = ""        # sólo poblado para el antecedente (Sprint-04, relation_type.py)
    rationale_features: tuple = ()  # tuple[(nombre, valor), ...] — por qué este eslabón, no prosa


@dataclass(frozen=True)
class Opportunity:
    need_id: str
    links: tuple                  # tuple[ChainLink, ...]
    opportunity_type: str
    priority: str
    score: float                  # score del antecedente — el ancla de toda la oportunidad


def _find(links: tuple, role: str):
    return next((link for link in links if link.role == role), None)


def classify_opportunity(links: tuple, *, cross_faculty: bool = False) -> str:
    """Orden de prioridad de las reglas (la primera que aplica gana) — mismo
    patrón que `relation_type.classify_relation`."""
    roles = {link.role for link in links}
    antecedente = _find(links, "antecedente")
    antecedente_metodologico = antecedente is not None and antecedente.relation_type == "antecedente_metodologico"

    if antecedente_metodologico and "investigador" in roles:
        return "continuidad_investigativa"
    if "capacidad" in roles and not antecedente_metodologico:
        return "activacion_capacidad"
    if "curriculo" in roles:
        return "integracion_curricular"
    if cross_faculty and "investigador" in roles:
        return "colaboracion_interdisciplinaria"
    return "exploratoria"


def opportunity_priority(links: tuple) -> str:
    """Combina el score del antecedente con cuántos eslabones "edge" (hechos
    duros) tiene la cadena — una cadena de 4 eslabones con score alto vale más
    que una de 2 con el mismo score."""
    antecedente = _find(links, "antecedente")
    score = antecedente.score if antecedente is not None and antecedente.score is not None else 0.0
    hard_links = sum(1 for link in links if link.link_type == "edge")

    if score >= ALTO and hard_links >= 2:
        return "alta"
    if score >= MEDIO or hard_links >= 1:
        return "media"
    return "baja"
