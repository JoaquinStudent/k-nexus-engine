"""Arreglo sistémico (Sprint-03): las dos veces que este proyecto perdió una
feature (ADR-007 sobre compat_metodo, y el hallazgo de graph_linked/
has_capability_support/compat_dominio en este mismo sprint) el síntoma fue el
mismo — una feature constante para todos los candidatos reales, invisible
porque ningún test unitario con fixtures a mano lo detecta. Estos tests miden
la distribución de las 7 features sobre una muestra real y fallan si alguna
degenera en casi-constante. Habrían cazado los tres hallazgos el día que se
introdujeron.
"""
import collections

import pytest

from src.adapters.embeddings.hashing_provider import HashingProvider
from src.adapters.graph.networkx_store import NetworkXGraphStore
from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.repository.projection import to_candidate_entity, to_query_entity
from src.adapters.retrieval.dense_index import DenseIndex
from src.domain.features import compute_features
from src.domain.models import CandidatePair

MAX_SINGLE_VALUE_SHARE = 0.90  # ninguna feature puede quedar en un solo valor >90% de la muestra
MIN_VOCAB_COVERAGE = {"PROJECT": 0.70, "THESIS": 0.70}


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def graph(repo):
    return NetworkXGraphStore(repo)


def _feature_vectors(repo, graph):
    """Muestra real: NEED-001 contra ~100 proyectos + ~40 investigadores reales
    (algunos genuinamente enlazados a esos proyectos, la mayoría no) — con
    capacidades reales y un índice denso (HashingProvider, offline) para que
    sim_semantica también varíe con datos reales, no un valor fijo."""
    need_entity = repo.get("NEED-001")
    need = to_query_entity(need_entity)
    capabilities = repo.by_type("CAPABILITY")

    projects = sorted(repo.by_type("PROJECT"), key=lambda e: e.entity_id)[:100]
    seed_ids = tuple(p.entity_id for p in projects[:15])  # PRJ-001..PRJ-015 (aristas reales)

    provider = HashingProvider(dim=128)
    dense = DenseIndex(provider)
    refs = tuple(p.entity_id for p in projects)
    texts = tuple(" ".join(t.text for t in p.texts) for p in projects)
    dense.build(refs, texts)
    need_vec = provider.encode((need_entity.raw.get("description", ""),))[0]
    project_texts_vec = provider.encode(texts)
    sims = project_texts_vec @ need_vec

    vectors = []
    for p, sim in zip(projects, sims):
        candidate = to_candidate_entity(p, graph=graph, seed_ids=seed_ids, capabilities=capabilities)
        vectors.append(compute_features(CandidatePair(query=need, candidate=candidate, sim_semantic=float(sim))))

    # Muestra de investigadores que garantiza AMBOS casos reales: conectados a
    # una semilla (arista researcher_project real) y genuinamente sin arista —
    # tomar un slice ciego de by_type() no lo garantiza (los IDs conectados a
    # PRJ-001..PRJ-015 no caen en las primeras filas del CSV).
    connected_ids = {e.src_id for e in repo.edges("researcher_project") if e.dst_id in seed_ids}
    all_ids = [r.entity_id for r in repo.by_type("RESEARCHER")]
    unconnected_ids = [rid for rid in all_ids if rid not in connected_ids][:30]
    researchers = [repo.get(rid) for rid in sorted(connected_ids) + unconnected_ids]
    for r in researchers:
        candidate = to_candidate_entity(r, graph=graph, seed_ids=seed_ids)
        vectors.append(compute_features(CandidatePair(query=need, candidate=candidate, sim_semantic=0.3)))

    return vectors


@pytest.fixture(scope="module")
def sample_vectors(repo, graph):
    return _feature_vectors(repo, graph)


# sim_lexica queda fuera de este chequeo A PROPÓSITO: institutional_needs.csv
# no tiene columna `keywords` (a diferencia de projects/theses), así que para
# TODA consulta NEED sim_lexica es 0.0 de forma legítima y constante. No es
# un hallazgo a corregir — es exactamente el diseño del SPEC (peso 0.05, "la
# más débil... evita premiar la trampa léxica"): forzarla a variar iría en
# contra del objetivo de no premiar coincidencia superficial de keywords.
FEATURE_NAMES = (
    "sim_semantica", "compat_metodo", "compat_dominio",
    "densidad_evidencia", "soporte_capacidad", "enlace_estructural",
)


def test_sim_lexica_es_cero_constante_por_diseno_no_por_bug(sample_vectors):
    values = {fv.sim_lexica for fv in sample_vectors}
    assert values == {0.0}, "si esto cambia, institutional_needs.csv ganó una columna keywords"


@pytest.mark.parametrize("feature_name", FEATURE_NAMES)
def test_ninguna_feature_es_casi_constante(sample_vectors, feature_name):
    values = [getattr(fv, feature_name) for fv in sample_vectors]
    counts = collections.Counter(values)
    most_common_value, most_common_count = counts.most_common(1)[0]
    share = most_common_count / len(values)
    assert len(counts) > 1, f"{feature_name} tiene un único valor ({most_common_value}) en toda la muestra"
    assert share <= MAX_SINGLE_VALUE_SHARE, (
        f"{feature_name} es casi-constante: {share:.0%} de la muestra vale {most_common_value!r}"
    )


def test_soporte_capacidad_discrimina_en_ambos_sentidos(sample_vectors):
    values = {fv.soporte_capacidad for fv in sample_vectors}
    assert values == {0.0, 1.0}


def test_enlace_estructural_discrimina_en_ambos_sentidos(sample_vectors):
    values = {fv.enlace_estructural for fv in sample_vectors}
    assert values == {0.0, 1.0}


def test_compat_metodo_no_es_solo_na(sample_vectors):
    non_na = [fv.compat_metodo for fv in sample_vectors if fv.compat_metodo is not None]
    assert len(non_na) / len(sample_vectors) > 0.5


def test_compat_dominio_no_es_solo_na(sample_vectors):
    non_na = [fv.compat_dominio for fv in sample_vectors if fv.compat_dominio is not None]
    assert len(non_na) / len(sample_vectors) > 0.5


# ---------------------------------------------------------------------------
# Cobertura de vocabulario (evidencia medible del sprint: 17-18-40% -> >70%)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("entity_type,minimum", MIN_VOCAB_COVERAGE.items())
def test_cobertura_de_metodo_supera_el_objetivo(repo, entity_type, minimum):
    entities = repo.by_type(entity_type)
    covered = sum(1 for e in entities if e.methods)
    assert covered / len(entities) > minimum, (
        f"cobertura de método en {entity_type}: {covered}/{len(entities)}"
    )


def test_cobertura_de_problem_type_need_mejoro_sustancialmente(repo):
    needs = repo.by_type("NEED")
    covered = sum(1 for n in needs if n.problem_types)
    # línea base pre-Sprint-03 medida: 40% (17/42). Objetivo: mayoría clara.
    assert covered / len(needs) > 0.70, f"cobertura problem_type NEED: {covered}/{len(needs)}"


def test_cobertura_de_sector_need_mejoro_desde_cero(repo):
    # ADR-009: antes de Sprint-03 esto era 0/42 (0%) sin excepción -- ninguna
    # columna de dominio existe en institutional_needs.csv.
    needs = repo.by_type("NEED")
    covered = sum(1 for n in needs if n.domains)
    assert covered > 0, "compat_dominio sigue muerto para todo NEED"
    assert covered / len(needs) > 0.50, f"cobertura de sector NEED: {covered}/{len(needs)}"
