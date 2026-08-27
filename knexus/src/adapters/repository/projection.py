"""Puente StoredEntity (ports) → QueryEntity/CandidateEntity (domain).

`has_capability_support` y `graph_linked` son contextuales (Sprint-03, ADR-008):
- `graph_linked` es relacional, no "existe en el grafo" (eso sería casi-constante
  `True`). Sin `graph`/`seed_ids` sigue en `False` — cero regresión respecto a
  Sprint-02; con contexto, verdadero si el candidato es adyacente a otro
  candidato fuerte de la MISMA consulta (necesidad→antecedente→investigador).
- `has_capability_support` cruza sector + tipo de capacidad (vía método) +
  madurez (`capability_match.py`). Sin `capabilities` sigue en `False`.
"""
from src.adapters.repository.capability_match import has_capability_support as _capability_match
from src.adapters.repository.dataset_paths import ENTITY_TABLES, MD_SECTION_COUNTS
from src.domain.models import CandidateEntity, QueryEntity
from src.ports.entity_repository import StoredEntity

# Total FIJO de campos indexables por tipo (columnas CSV + secciones MD del
# tipo, si las tiene) — NUNCA se infla con lo que trae una instancia concreta.
# Bug corregido en Sprint-03: antes `expected = max(declarado, len(filled))`
# hacía que expected nunca pudiera ser menor que filled, saturando
# densidad_evidencia en 1.0 para el 96% de las entidades con MD fusionado
# (detectado por `test_ninguna_feature_es_casi_constante`).
_EXPECTED_FIELDS_BY_TYPE = {
    entity_type: len(text_cols) + MD_SECTION_COUNTS.get(entity_type, 0)
    for entity_type, _id_col, text_cols in ENTITY_TABLES.values()
}


def to_query_entity(entity: StoredEntity) -> QueryEntity:
    text = " ".join(t.text for t in entity.texts)
    return QueryEntity(
        entity_type=entity.entity_type.lower(),
        text=text,
        keywords=entity.keywords,
        domains=entity.domains,
        methods=entity.methods,
        problem_types=entity.problem_types,
    )


def to_candidate_entity(
    entity: StoredEntity, *, graph=None, seed_ids: tuple = (), capabilities: tuple = (),
) -> CandidateEntity:
    text = " ".join(t.text for t in entity.texts)
    filled_fields = tuple(dict.fromkeys(t.provenance.field_name for t in entity.texts))
    expected_fields = max(_EXPECTED_FIELDS_BY_TYPE.get(entity.entity_type, 1), 1)

    graph_linked = bool(graph is not None and seed_ids and graph.linked_to_any(entity.entity_id, seed_ids))
    capability_support = bool(capabilities) and _capability_match(entity.domains, entity.methods, capabilities)

    return CandidateEntity(
        entity_id=entity.entity_id,
        entity_type=entity.entity_type.lower(),
        text=text,
        keywords=entity.keywords,
        domains=entity.domains,
        methods=entity.methods,
        filled_fields=filled_fields,
        expected_fields=expected_fields,
        has_capability_support=capability_support,
        graph_linked=graph_linked,
    )
