"""Construye un `QueryEntity` a partir de lo que escribe/selecciona el usuario:
una entidad existente del dataset (`NEED-001`, `PRJ-004`...) o texto libre.

Un texto libre se enriquece con el MISMO mecanismo que un NEED (ADR-007/009,
`src.domain.text_matching`): sin esto, `compat_metodo` y `compat_dominio`
(0.20+0.20, los dos pesos más altos) caen a N/A y la consulta pierde el 40%
del peso del score. Nunca se le asigna un método al texto libre — sólo tipo de
problema y sector inferidos, igual que a un NEED.
"""
from src.adapters.repository.projection import to_query_entity
from src.domain.models import QueryEntity
from src.domain.text_matching import infer_problem_types, infer_sectors


def build_query(query_input: str, repo) -> QueryEntity:
    """`repo`: EntityRepository (puerto). Si `query_input` es el id de una
    entidad existente, se proyecta con `to_query_entity` (reusa el
    enriquecimiento ya hecho en ingesta). Si no, se trata como texto libre."""
    try:
        entity = repo.get(query_input.strip())
    except KeyError:
        entity = None
    if entity is not None:
        return to_query_entity(entity)
    return _from_free_text(query_input)


def _from_free_text(text: str) -> QueryEntity:
    return QueryEntity(
        entity_type="query",
        text=text,
        keywords=(),
        domains=infer_sectors(text),
        methods=(),
        problem_types=infer_problem_types(text),
    )
