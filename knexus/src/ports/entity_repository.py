"""Puerto de repositorio de entidades con provenance. Frontera del dominio puro:
estos DTO viven fuera de `domain/` porque cargan metadatos de origen (Regla A1
del dominio no aplica aquí; `domain/` sigue sin conocer nada de esto)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Provenance:
    source_file: str
    entity_type: str
    entity_id: str
    field_name: str
    created_by: str = "ChaparroVillavicencioJoaquin"


@dataclass(frozen=True)
class ProvenancedText:
    text: str
    provenance: Provenance


@dataclass
class StoredEntity:
    entity_id: str
    entity_type: str
    raw: dict = field(default_factory=dict)
    texts: tuple = ()
    keywords: tuple = ()
    domains: tuple = ()
    methods: tuple = ()
    problem_types: tuple = ()


@dataclass(frozen=True)
class Edge:
    relation: str
    src_id: str
    dst_id: str
    attrs: dict = field(default_factory=dict)


class EntityRepository(ABC):
    @abstractmethod
    def get(self, entity_id: str) -> StoredEntity:
        ...

    @abstractmethod
    def by_type(self, entity_type: str) -> tuple:
        ...

    @abstractmethod
    def all(self) -> tuple:
        ...

    @abstractmethod
    def provenance_of(self, entity_id: str) -> tuple:
        ...

    @abstractmethod
    def edges(self, relation: str) -> tuple:
        ...
