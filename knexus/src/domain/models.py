"""Contrato de datos del dominio. PURO — sin imports externos (Regla A1)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryEntity:
    entity_type: str
    text: str
    keywords: tuple = ()
    domains: tuple = ()
    methods: tuple = ()
    problem_types: tuple = ()  # tipo(s) de problema inferido(s) en ingesta cuando
    # la consulta (p.ej. un NEED) no prescribe método — habilita compat_metodo por
    # transferabilidad en lugar de solape simétrico.


@dataclass(frozen=True)
class CandidateEntity:
    entity_id: str
    entity_type: str
    text: str
    keywords: tuple = ()
    domains: tuple = ()
    methods: tuple = ()
    filled_fields: tuple = ()
    expected_fields: int = 1
    has_capability_support: bool = False
    graph_linked: bool = False


@dataclass(frozen=True)
class CandidatePair:
    query: QueryEntity
    candidate: CandidateEntity
    sim_semantic: float


@dataclass(frozen=True)
class FeatureVector:
    sim_semantica: float
    sim_lexica: float
    compat_metodo: float  # None == N/A: la consulta no aporta método comparable;
    # se excluye del score (re-normalización) en vez de contar como 0.
    compat_dominio: float  # None == N/A (ADR-009): la consulta no aporta ningún
    # dominio/sector comparable; se excluye del score igual que compat_metodo.
    densidad_evidencia: float
    soporte_capacidad: float
    enlace_estructural: float


@dataclass(frozen=True)
class ScoredResult:
    entity_id: str  # string plano: el dominio no importa nada de ports/ (Regla A1)
    feature_vector: FeatureVector
    score: float
    relation_type: str
