"""Puerto: relaciones explícitas y caminos. Implementación en adapters/graph/."""
from abc import ABC, abstractmethod


class GraphStore(ABC):
    @abstractmethod
    def neighbors(self, entity_id: str) -> tuple:
        """Vecinos directos de `entity_id` en cualquier relación cargada."""
        ...

    @abstractmethod
    def linked_to_any(self, entity_id: str, seed_ids: tuple) -> bool:
        """True si `entity_id` es adyacente a alguno de `seed_ids`."""
        ...

    @abstractmethod
    def degree(self, entity_id: str) -> int:
        ...
