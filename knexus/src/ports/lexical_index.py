"""Puerto: búsqueda léxica por términos. Implementación en adapters/retrieval/."""
from abc import ABC, abstractmethod


class LexicalIndex(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 10) -> tuple:
        """Retorna hasta k tuplas (ref, score) ordenadas por score descendente."""
        ...
