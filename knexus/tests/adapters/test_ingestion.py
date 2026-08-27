"""Sprint-02: ingesta + provenance + entity store.

Cierra el lazo abierto por ADR-007 (Sprint-01.5): `compat_metodo` debe
desempatar sobre entidades REALES del dataset, no sobre fixtures inyectados.
"""
import pytest

from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.adapters.repository.enrichment import infer_problem_types, mine_methods
from src.adapters.repository.projection import to_candidate_entity, to_query_entity
from src.adapters.repository.vocabulary import METHOD_TAGS, PROBLEM_TYPE_TAGS
from src.domain.features import compute_features
from src.domain.models import CandidatePair
from src.domain.relation_type import classify_relation
from src.domain.scoring import compute_score

EXPECTED_COUNTS = {
    "FACULTY": 6,
    "PROGRAM": 18,
    "RESEARCH_GROUP": 24,
    "RESEARCH_LINE": 60,
    "CAPABILITY": 96,
    "RESEARCHER": 180,
    "SUBJECT": 126,
    "COMPETENCY": 252,
    "LEARNING_OUTCOME": 378,
    "NEED": 42,
    "PROJECT": 320,
    "THESIS": 650,
    "PUBLICATION": 360,
}


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


def test_conteos_por_tabla_cuadran_con_manifest(repo):
    for entity_type, expected in EXPECTED_COUNTS.items():
        assert len(repo.by_type(entity_type)) == expected, entity_type


def test_conteos_de_aristas_cuadran_con_manifest(repo):
    assert len(repo.edges("researcher_project")) == 746
    assert len(repo.edges("project_group")) == 320
    assert len(repo.edges("thesis_advisor")) == 650
    assert len(repo.edges("publication_researcher")) == 720
    assert len(repo.edges("publication_project")) == 200
    assert len(repo.edges("researcher_group")) == 180
    assert len(repo.edges("researcher_expertise")) == 720


def test_provenance_completa_y_placeholder_autor(repo):
    provenance = repo.provenance_of("PRJ-004")
    assert provenance, "PRJ-004 debería tener texto con provenance"
    for p in provenance:
        assert p.source_file
        assert p.entity_type
        assert p.entity_id == "PRJ-004"
        assert p.field_name
        assert p.created_by == "ChaparroVillavicencioJoaquin"


def test_trazabilidad_end_to_end_methodology(repo):
    # DoD Sprint-02 / Regla A3: el texto de un campo se reconstruye hasta su origen.
    provenance = repo.provenance_of("PRJ-004")
    methodology_prov = [p for p in provenance if p.field_name == "methodology"]
    assert methodology_prov, "compat_metodo depende de trazar 'methodology'"
    assert methodology_prov[0].source_file == "03_knowledge_needs_projects.csv"


def test_fusion_md_aporta_texto_adicional(repo):
    # PRJ-004 tiene project_profile_004.md en document_catalog.csv.
    provenance = repo.provenance_of("PRJ-004")
    md_sources = {p.source_file for p in provenance if p.source_file.endswith(".md")}
    assert "project_profile_004.md" in md_sources


def test_enriquecimiento_methods_sobre_datos_reales(repo):
    prj004 = repo.get("PRJ-004")
    assert "clasificacion_supervisada" in prj004.methods

    prj002 = repo.get("PRJ-002")
    assert "analitica_educativa" in prj002.methods

    prj006 = repo.get("PRJ-006")
    assert "modelos_longitudinales" in prj006.methods


def test_enriquecimiento_problem_types_need_001(repo):
    need001 = repo.get("NEED-001")
    assert "prediccion" in need001.problem_types
    # El NEED nunca recibe métodos: el MD lo declara a propósito.
    assert need001.methods == ()


def test_anti_drift_vocabulario_metodo():
    tags = mine_methods("clasificación supervisada, analítica educativa, encuesta")
    assert set(tags) <= METHOD_TAGS


def test_anti_drift_vocabulario_problem_type():
    tags = infer_problem_types("predicción y prevención de deserción")
    assert set(tags) <= PROBLEM_TYPE_TAGS


def test_cierre_adr007_need001_desempata_sobre_datos_reales(repo):
    """★ Test estrella de Sprint-02: reemplaza el fixture inyectado (DoD-3 de
    Sprint-01) por NEED-001, PRJ-004 y PRJ-002 REALES del dataset. PRJ-004
    (clasificación supervisada, transferabilidad 0.90) debe superar a PRJ-002
    (analítica educativa, transferabilidad 0.70) y tipar antecedente_metodologico
    — sin que el NEED haya declarado un solo método."""
    need = to_query_entity(repo.get("NEED-001"))
    assert need.methods == ()
    assert "prediccion" in need.problem_types

    prj004 = to_candidate_entity(repo.get("PRJ-004"))
    prj002 = to_candidate_entity(repo.get("PRJ-002"))

    fv_004 = compute_features(CandidatePair(query=need, candidate=prj004, sim_semantic=0.88))
    fv_002 = compute_features(CandidatePair(query=need, candidate=prj002, sim_semantic=0.88))

    assert fv_004.compat_metodo is not None and fv_002.compat_metodo is not None
    assert fv_004.compat_metodo > fv_002.compat_metodo

    score_004 = compute_score(fv_004)
    score_002 = compute_score(fv_002)
    assert score_004 > score_002

    assert classify_relation(fv_004, prj004.entity_type) == "antecedente_metodologico"


def test_need_sin_texto_matcheable_cae_a_na(repo):
    # Un NEED cuyo texto no matchea ningún tipo de problema conocido debe
    # producir compat_metodo=None (N/A), nunca un 0 falso.
    sin_senal = [
        n for n in repo.by_type("NEED")
        if not infer_problem_types(n.raw.get("description", ""), n.raw.get("context", ""))
    ]
    assert sin_senal, "se espera al menos un NEED sin problem_type inferible en 42 casos reales"
    query = to_query_entity(sin_senal[0])
    candidate = to_candidate_entity(repo.get("PRJ-004"))
    fv = compute_features(CandidatePair(query=query, candidate=candidate, sim_semantic=0.5))
    assert fv.compat_metodo is None
