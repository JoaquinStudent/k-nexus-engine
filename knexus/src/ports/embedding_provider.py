"""Puerto: texto → vector. Implementaciones en adapters/embeddings/."""
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def encode(self, texts: tuple):
        """Retorna una matriz (len(texts), dim) de vectores L2-normalizados."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Identificador estable del modelo/config — clave de la caché de
        vectores (`vector_cache.py`); dos providers con distinto `name` nunca
        deben compartir caché."""
        ...
