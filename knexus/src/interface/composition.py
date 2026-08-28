"""Composition root de la capa `interface/` (Regla A2 de ARCHITECTURE.md):
único módulo autorizado a instanciar los adapters concretos de cada puerto.
`descubrir_conexiones`/`generar_oportunidad` reciben el pipeline ya
construido — nunca lo arman ellos mismos.

Movido aquí desde `scripts/query_cli.py` (Sprint-04/05) para que exista una
sola definición del arranque; ahora también la reusa `interface/app.py`.
"""
import time
from functools import lru_cache

from src.adapters.explain.factory import build_explainer
from src.adapters.explain.template_explainer import TemplateExplainer
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.descubrir_conexiones import descubrir_conexiones
from src.application.generar_oportunidad import generar_oportunidad
from src.ports.explainer import Explainer


class _CachingExplainer(Explainer):
    """Envuelve un `Explainer` real (LLM) para no pagar una llamada de red
    nueva cada vez que se recarga la MISMA página. Clave = id() del DTO, no
    su contenido: `discover`/`opportunities` ya están cacheados por query
    (arriba), así que la misma query+entidad siempre entrega el MISMO objeto
    Python -- id() alcanza sin tener que volver hasheables los DTOs (algunos,
    como RankedConnection, no lo son por StoredEntity).
    ponytail: dict sin límite de tamaño -- vive lo que dura el proceso; subir
    a un LRU si una sesión tan larga como para que la memoria importe."""

    def __init__(self, inner: Explainer):
        self._inner = inner
        self._cache: dict = {}

    def _cached(self, method_name: str, dto) -> str:
        key = (method_name, id(dto))
        if key not in self._cache:
            self._cache[key] = getattr(self._inner, method_name)(dto)
        return self._cache[key]

    def explain_connection(self, connection) -> str:
        return self._cached("explain_connection", connection)

    def explain_opportunity(self, opportunity) -> str:
        return self._cached("explain_opportunity", opportunity)

    def explain_comparison(self, comparison) -> str:
        return self._cached("explain_comparison", comparison)


def build_pipeline(fast: bool = False, *, log=lambda msg: None):
    """Retorna `(repo, dense_index, lexical_index, graph)` ya construidos.
    `fast=True` usa `HashingProvider` (offline, sin descargar el modelo real)
    — pensado para tests y `--fast` del CLI, no para la demo."""
    log("Cargando repositorio...")
    repo = DatasetEntityRepository()
    refs, texts = build_corpus(repo)

    if fast:
        from src.adapters.embeddings.hashing_provider import HashingProvider
        provider = HashingProvider(dim=256)
        log("Modo rápido: HashingProvider (sin similitud semántica real).")
    else:
        from src.adapters.embeddings.sentence_transformer_provider import SentenceTransformerProvider
        log("Cargando modelo de embeddings (primera vez puede tardar)...")
        provider = SentenceTransformerProvider()

    dense = DenseIndex(provider)
    t0 = time.time()
    dense.build(refs, texts, use_cache=not fast)
    log(f"Índice denso listo en {time.time() - t0:.1f}s.")

    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return repo, dense, lexical, graph


class QueryService:
    """Pipeline ya construido + caché de consulta.

    `generar_oportunidad` llama por dentro a `descubrir_conexiones` con la
    MISMA query (`generar_oportunidad.py`) — sin esta caché, navegar
    Resultados -> Oportunidad -> Auditoría sobre la misma consulta repetiría
    todo el pipeline en cada salto.
    """

    def __init__(self, repo, dense_index, lexical_index, graph, explainer=None):
        self.repo = repo
        self.dense_index = dense_index
        self.lexical_index = lexical_index
        self.graph = graph
        # build_explainer() ya implementa la degradación de Regla A4 (sin
        # OPENROUTER_API_KEY -> TemplateExplainer); no se reimplementa aquí.
        base_explainer = explainer if explainer is not None else build_explainer()
        self._explainer_is_template = isinstance(base_explainer, TemplateExplainer)
        # Cachea la redacción del LLM -- sin esto, recargar la misma página
        # de conexión/oportunidad/auditoría vuelve a llamar a OpenRouter cada
        # vez, aunque el resultado (rankeo, score) sea idéntico por venir de
        # discover()/opportunities(), que sí están cacheados.
        self.explainer = _CachingExplainer(base_explainer)
        # ponytail: la query es un string — lru_cache es toda la caché que hace falta.
        self.discover = lru_cache(maxsize=64)(self._discover)
        self.opportunities = lru_cache(maxsize=64)(self._opportunities)

    @property
    def explainer_degraded(self) -> bool:
        """True si el sistema corre sin LLM — TemplateExplainer por defecto o
        por degradación (Regla A4). Alimenta el banner ámbar de M9."""
        return self._explainer_is_template

    def _discover(self, query: str) -> tuple:
        return descubrir_conexiones(
            query, repo=self.repo, dense_index=self.dense_index,
            lexical_index=self.lexical_index, graph=self.graph,
        )

    def _opportunities(self, query: str) -> tuple:
        return generar_oportunidad(
            query, repo=self.repo, dense_index=self.dense_index,
            lexical_index=self.lexical_index, graph=self.graph,
        )

    @classmethod
    def build(cls, fast: bool = False, *, log=lambda msg: None) -> "QueryService":
        return cls(*build_pipeline(fast=fast, log=log))
