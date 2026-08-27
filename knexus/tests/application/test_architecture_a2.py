"""Regla A2 (ARCHITECTURE.md §6): los use-cases dependen de puertos, no de
adapters concretos; y cada adapter concreto implementa el puerto que le
corresponde — no basta con "funcionar por duck typing"."""
import ast
import pathlib

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.dense_index import DenseIndex
from src.ports.embedding_provider import EmbeddingProvider
from src.ports.entity_repository import EntityRepository
from src.ports.graph_store import GraphStore
from src.ports.lexical_index import LexicalIndex
from src.ports.vector_index import VectorIndex

APPLICATION_DIR = pathlib.Path(__file__).resolve().parents[2] / "src" / "application"

ADAPTER_TO_PORT = (
    (DatasetEntityRepository, EntityRepository),
    (HashingProvider, EmbeddingProvider),
    (SentenceTransformerProvider, EmbeddingProvider),
    (BM25Index, LexicalIndex),
    (DenseIndex, VectorIndex),
    (NetworkXGraphStore, GraphStore),
)


def test_cada_adapter_implementa_su_puerto():
    for adapter_cls, port_cls in ADAPTER_TO_PORT:
        assert issubclass(adapter_cls, port_cls), (
            f"{adapter_cls.__name__} no hereda de {port_cls.__name__} — "
            "funciona por duck typing, pero A2 exige el contrato explícito"
        )


FORBIDDEN_CONCRETE_IMPORTS = {
    "SentenceTransformerProvider", "HashingProvider", "DatasetEntityRepository",
    "BM25Index", "DenseIndex", "NetworkXGraphStore",
}


def test_application_no_importa_clases_concretas_de_adapters():
    """A2 prohíbe depender de una IMPLEMENTACIÓN concreta y swappeable de un
    puerto (instanciar `SentenceTransformerProvider` directo en un use-case
    impediría cambiarla por `HashingProvider` sin tocar `application/`). No
    prohíbe reutilizar funciones utilitarias de adapters/ que no son
    "la implementación de un puerto" — `to_query_entity`, `build_corpus`,
    `fuse`, etc. no tienen alternativa intercambiable; son mappers, no adapters."""
    if not APPLICATION_DIR.exists():
        return  # aún no existe la capa; el resto de A2 no aplica todavía
    for path in APPLICATION_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name not in FORBIDDEN_CONCRETE_IMPORTS, (
                        f"{path.name} importa la clase concreta '{alias.name}' — "
                        "debe recibirse ya instanciada (inyección de dependencias) "
                        "y tiparse contra su puerto, no importarse directo (Regla A2)"
                    )
