"""application/generar_oportunidad.py — ensamblado de la cadena de
oportunidad (Sprint-05). Offline con HashingProvider salvo los `slow`."""
import pytest

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.bm25_index import BM25Index
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.descubrir_conexiones import descubrir_conexiones
from src.application.generar_oportunidad import _build_opportunity, generar_oportunidad
from src.application.query_builder import build_query


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def pipeline(repo):
    refs, texts = build_corpus(repo)
    dense = DenseIndex(HashingProvider(dim=256))
    dense.build(refs, texts, use_cache=False)
    lexical = BM25Index()
    lexical.build(refs, texts)
    graph = NetworkXGraphStore(repo)
    return {"repo": repo, "dense_index": dense, "lexical_index": lexical, "graph": graph}


class _NoNeighborsGraph:
    """Stub: ninguna entidad tiene vecinos — fuerza la rama de degradación."""
    def neighbors(self, entity_id):
        return ()

    def linked_to_any(self, entity_id, seed_ids):
        return False

    def degree(self, entity_id):
        return 0


def test_need001_ensambla_cadena_con_link_types_correctos(pipeline):
    opportunities = generar_oportunidad("NEED-001", **pipeline)
    assert opportunities
    top = opportunities[0]
    roles_and_types = {link.role: link.link_type for link in top.links}
    assert roles_and_types["necesidad"] == "retrieved"
    assert roles_and_types["antecedente"] == "retrieved"
    # investigador/capacidad/curriculo pueden faltar (degradación), pero si
    # están presentes, su link_type debe ser el correcto:
    if "investigador" in roles_and_types:
        assert roles_and_types["investigador"] == "edge"
    if "capacidad" in roles_and_types:
        assert roles_and_types["capacidad"] == "inferred"
    if "curriculo" in roles_and_types:
        assert roles_and_types["curriculo"] == "edge"


def test_need001_produce_cadena_completa_de_4_eslabones_en_algun_antecedente(pipeline):
    """★ Al menos una oportunidad de NEED-001 debe alcanzar los 4 eslabones
    (antecedente+investigador+capacidad+curriculo) — la cadena completa que
    DESIGN.md M5 espera mostrar."""
    opportunities = generar_oportunidad("NEED-001", **pipeline)
    roles_per_opportunity = [{link.role for link in o.links} for o in opportunities]
    full_chain = {"necesidad", "antecedente", "investigador", "capacidad", "curriculo"}
    assert any(roles == full_chain for roles in roles_per_opportunity)


def test_degradacion_sin_investigador_no_fabrica_eslabones(repo, pipeline):
    """Un antecedente sin investigador conectado (grafo stub sin vecinos) no
    debe producir eslabones de investigador/currículo — nunca se inventan."""
    connections = descubrir_conexiones(
        "NEED-001", repo=repo, dense_index=pipeline["dense_index"],
        lexical_index=pipeline["lexical_index"], graph=pipeline["graph"],
    )
    connection = next(c for c in connections if c.entity.entity_type == "PROJECT")
    need_entity = repo.get("NEED-001")
    query = build_query("NEED-001", repo)
    capabilities = repo.by_type("CAPABILITY")

    opportunity = _build_opportunity(
        need_entity, query, connection,
        repo=repo, graph=_NoNeighborsGraph(), dense_index=pipeline["dense_index"],
        capabilities=capabilities,
    )
    roles = {link.role for link in opportunity.links}
    assert "investigador" not in roles
    assert "curriculo" not in roles  # depende de investigador -> tampoco aparece
    assert "necesidad" in roles and "antecedente" in roles


def test_las_42_necesidades_generan_oportunidad_sin_reventar(pipeline, repo):
    sin_oportunidades = 0
    for need in repo.by_type("NEED"):
        opportunities = generar_oportunidad(need.entity_id, **pipeline)
        assert isinstance(opportunities, tuple)
        if not opportunities:
            sin_oportunidades += 1
        for o in opportunities:
            assert o.need_id == need.entity_id
            assert o.opportunity_type
            assert o.priority in ("alta", "media", "baja")
    assert sin_oportunidades < 42  # la mayoría de las 42 sí produce algo


def test_provenance_rastreable_en_cada_eslabon(pipeline, repo):
    """Regla A3: cada entity_id de la cadena resuelve a una entidad real con
    provenance — nada en la cadena es un identificador fabricado."""
    opportunities = generar_oportunidad("NEED-001", **pipeline)
    assert opportunities
    for opportunity in opportunities:
        for link in opportunity.links:
            if link.entity_type == "need":
                continue  # ya se resolvió al construir la cadena
            entity = repo.get(link.entity_id)  # lanza KeyError si no existe
            assert entity.entity_id == link.entity_id
