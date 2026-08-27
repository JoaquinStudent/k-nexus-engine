"""Verificación con el modelo real: el eslabón curricular se PUNTÚA, no se
traversa a ciegas. Con HashingProvider la discriminación semántica es débil
(documentado desde Sprint-03/04); este test exige el modelo real.
"""
import pytest

from src.adapters.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.retrieval.corpus import build_corpus
from src.adapters.retrieval.dense_index import DenseIndex
from src.application.generar_oportunidad import _pick_curricular
from src.application.query_builder import build_query


@pytest.mark.slow
def test_curricular_pertinente_puntua_mas_que_irrelevante_del_mismo_programa():
    """★ Para NEED-001, "Analítica educativa" (SUB-083, programa PRG-012 de
    INV-127) debe puntuar por encima de "Lenguaje y conocimiento" (SUB-084,
    mismo programa) — ambas comparten disciplinary_area/sector, así que sólo
    la relevancia semántica real las distingue. Si el ensamblado traversara a
    ciegas (primer subject del programa) esto no estaría garantizado."""
    repo = DatasetEntityRepository()
    refs, texts = build_corpus(repo)
    dense = DenseIndex(SentenceTransformerProvider())
    dense.build(refs, texts)
    graph = NetworkXGraphStore(repo)

    query = build_query("NEED-001", repo)
    researcher = repo.get("INV-127")
    capabilities = repo.by_type("CAPABILITY")

    picked = _pick_curricular(query, researcher, repo, dense, capabilities)
    assert picked is not None
    best_entity, best_score = picked
    assert best_entity.entity_id == "SUB-083"

    # y confirmar explícitamente que SUB-083 > SUB-084 en la puntuación real
    from src.adapters.repository.projection import to_candidate_entity
    from src.domain.features import compute_features
    from src.domain.models import CandidatePair
    from src.domain.scoring import compute_score
    from src.adapters.retrieval.fusion import aggregate_by_entity

    sims = aggregate_by_entity(dense.search(query.text, k=1000))
    scores = {}
    for sid in ("SUB-083", "SUB-084"):
        entity = repo.get(sid)
        _, sim = sims.get(sid, (None, 0.0))
        candidate = to_candidate_entity(entity, capabilities=capabilities)
        fv = compute_features(CandidatePair(query=query, candidate=candidate, sim_semantic=sim))
        scores[sid] = compute_score(fv)
    assert scores["SUB-083"] > scores["SUB-084"]
