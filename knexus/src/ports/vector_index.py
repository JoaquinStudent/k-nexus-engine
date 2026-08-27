"""Puerto: búsqueda por similitud vectorial (denso). Implementación en
adapters/retrieval/. Espejo de `LexicalIndex` — mismo contrato de salida
`(ref, score)` para que la capa `application/` fusione ambos rankings sin
distinguir su origen."""
from abc import ABC, abstractmethod


class VectorIndex(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 10) -> tuple:
        """Retorna hasta k tuplas (ref, score) ordenadas por score descendente."""
        ...
