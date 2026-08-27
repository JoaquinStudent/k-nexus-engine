"""Adapter de `EntityRepository` que carga Data V1.0 completa en memoria."""
import pathlib

from src.adapters.repository import csv_loader, md_loader
from src.adapters.repository.capability_match import domain_sector
from src.adapters.repository.dataset_paths import (
    DOMAIN_COLUMNS, KEYWORDS_COLUMNS, METHOD_SOURCE_COLUMNS,
    PROBLEM_TYPE_SOURCE_COLUMNS, dataset_root,
)
from src.adapters.repository.enrichment import (
    extract_domains, infer_problem_types, infer_sectors, mine_methods, split_keywords,
)
from src.ports.entity_repository import EntityRepository, StoredEntity

# Tipos que reciben inferencia de problem_types (consultas sin método prescrito).
QUERY_LIKE_TYPES = ("NEED",)
# Tipos que aportan método real minable (candidatos).
METHOD_BEARING_TYPES = ("PROJECT", "THESIS")


def _enrich(entity: StoredEntity) -> StoredEntity:
    raw = entity.raw
    keywords = tuple(
        kw for col in KEYWORDS_COLUMNS for kw in split_keywords(raw.get(col, ""))
    )
    fine_domains = extract_domains(*(raw.get(col, "") for col in DOMAIN_COLUMNS))
    # ADR-009: NEED no tiene NINGUNA columna de dominio (institutional_needs.csv
    # carece de disciplinary_area/application_domains/research_area) -> se
    # infiere un sector del texto. Para el resto se AÑADE el sector del dominio
    # fino (p.ej. "Psicología"→"educacion") para que compat_dominio tenga un
    # vocabulario común con el que cruzar contra el sector inferido del NEED.
    if entity.entity_type == "NEED":
        sectors = infer_sectors(*(raw.get(col, "") for col in PROBLEM_TYPE_SOURCE_COLUMNS))
    else:
        sectors = tuple(dict.fromkeys(s for d in fine_domains if (s := domain_sector(d))))
    domains = tuple(dict.fromkeys(fine_domains + sectors))

    methods = ()
    if entity.entity_type in METHOD_BEARING_TYPES:
        methods = mine_methods(*(raw.get(col, "") for col in METHOD_SOURCE_COLUMNS))

    problem_types = ()
    if entity.entity_type in QUERY_LIKE_TYPES:
        problem_types = infer_problem_types(
            *(raw.get(col, "") for col in PROBLEM_TYPE_SOURCE_COLUMNS)
        )

    entity.keywords = keywords
    entity.domains = domains
    entity.methods = methods
    entity.problem_types = problem_types
    return entity


class DatasetEntityRepository(EntityRepository):
    def __init__(self, root: pathlib.Path = None):
        root = root or dataset_root()
        entities = csv_loader.load_entities(root)
        catalog = csv_loader.load_document_catalog(root)
        md_texts = md_loader.load_documents(catalog, root)

        for entity_id, extra_texts in md_texts.items():
            if entity_id in entities:
                entities[entity_id].texts = entities[entity_id].texts + extra_texts

        for entity in entities.values():
            _enrich(entity)

        self._entities = entities
        self._edges = csv_loader.load_edges(root)

    def get(self, entity_id: str) -> StoredEntity:
        return self._entities[entity_id]

    def by_type(self, entity_type: str) -> tuple:
        return tuple(e for e in self._entities.values() if e.entity_type == entity_type)

    def all(self) -> tuple:
        return tuple(self._entities.values())

    def provenance_of(self, entity_id: str) -> tuple:
        return tuple(t.provenance for t in self._entities[entity_id].texts)

    def edges(self, relation: str) -> tuple:
        return self._edges.get(relation, ())
