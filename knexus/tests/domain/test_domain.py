import ast
import pathlib

import pytest

from src.domain.models import CandidateEntity, CandidatePair, FeatureVector, QueryEntity
from src.domain.features import compute_features
from src.domain.scoring import WEIGHTS, compute_score
from src.domain.relation_type import classify_relation
from src.domain.method_compat import transferability

DOMAIN_DIR = pathlib.Path(__file__).resolve().parents[2] / "src" / "domain"

ALLOWED_STDLIB = {"dataclasses"}


def _pair(sim_semantic, keywords=(), methods=(), domains=(), problem_types=(),
          c_keywords=(), c_methods=(), c_domains=(),
          filled_fields=(), expected_fields=1,
          has_capability_support=False, graph_linked=False,
          candidate_entity_type="project"):
    query = QueryEntity(
        entity_type="need", text="q", keywords=keywords, domains=domains,
        methods=methods, problem_types=problem_types,
    )
    candidate = CandidateEntity(
        entity_id="X-1",
        entity_type=candidate_entity_type,
        text="c",
        keywords=c_keywords,
        domains=c_domains,
        methods=c_methods,
        filled_fields=filled_fields,
        expected_fields=expected_fields,
        has_capability_support=has_capability_support,
        graph_linked=graph_linked,
    )
    return CandidatePair(query=query, candidate=candidate, sim_semantic=sim_semantic)


def test_features_rango():
    pair = _pair(
        sim_semantic=0.88,
        keywords=("a", "b"), c_keywords=("a", "c"),
        methods=("m1",), c_methods=("m1",),
        domains=("d1",), c_domains=("d1", "d2"),
        filled_fields=("f1", "f2"), expected_fields=4,
        has_capability_support=True, graph_linked=True,
    )
    fv = compute_features(pair)
    for value in (
        fv.sim_semantica, fv.sim_lexica, fv.compat_metodo, fv.compat_dominio,
        fv.densidad_evidencia, fv.soporte_capacidad, fv.enlace_estructural,
    ):
        assert 0.0 <= value <= 1.0


def test_scoring_pesos_suman_uno():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)


def test_A_vs_B_metodo_desempata():
    # PRJ-004: mismo sim_semantica que PRJ-007, pero método transferible fuerte.
    pair_a = _pair(
        sim_semantic=0.88,
        methods=("clasificacion_supervisada",), c_methods=("clasificacion_supervisada",),
        domains=("permanencia_estudiantil",), c_domains=("permanencia_estudiantil", "attrition"),
        filled_fields=("f1", "f2", "f3"), expected_fields=4,
        has_capability_support=True,
    )
    # PRJ-007: mismo tema, completado, menor soporte de método.
    pair_b = _pair(
        sim_semantic=0.88,
        methods=("clasificacion_supervisada",), c_methods=("encuesta",),
        domains=("permanencia_estudiantil",), c_domains=("permanencia_estudiantil",),
        filled_fields=("f1",), expected_fields=4,
        has_capability_support=False,
    )
    fv_a = compute_features(pair_a)
    fv_b = compute_features(pair_b)
    score_a = compute_score(fv_a)
    score_b = compute_score(fv_b)

    assert fv_a.sim_semantica == fv_b.sim_semantica
    assert fv_a.compat_metodo != fv_b.compat_metodo
    assert score_a > score_b


def test_A_vs_B_need_transferabilidad_desempata():
    # DoD-3 sobre la forma real de los datos: el NEED NO trae métodos (el MD lo
    # declara así). Se infiere problem_type="prediccion" del texto; el método REAL
    # del candidato desempata por transferabilidad, no por solape de conjuntos.
    pair_a = _pair(  # PRJ-004: clasificación supervisada → transferible a predicción
        sim_semantic=0.88,
        problem_types=("prediccion",), c_methods=("clasificacion_supervisada",),
        domains=("permanencia_estudiantil",), c_domains=("permanencia_estudiantil", "attrition"),
        filled_fields=("f1", "f2", "f3"), expected_fields=4,
        has_capability_support=True,
    )
    pair_b = _pair(  # PRJ-007: encuesta → poco transferible a una necesidad predictiva
        sim_semantic=0.88,
        problem_types=("prediccion",), c_methods=("encuesta",),
        domains=("permanencia_estudiantil",), c_domains=("permanencia_estudiantil",),
        filled_fields=("f1",), expected_fields=4,
        has_capability_support=False,
    )
    fv_a = compute_features(pair_a)
    fv_b = compute_features(pair_b)

    assert fv_a.sim_semantica == fv_b.sim_semantica
    assert fv_a.compat_metodo is not None and fv_b.compat_metodo is not None
    assert fv_a.compat_metodo > fv_b.compat_metodo
    assert compute_score(fv_a) > compute_score(fv_b)
    # El tipo estrella vuelve a ser alcanzable desde un NEED puro.
    assert classify_relation(fv_a, pair_a.candidate.entity_type) == "antecedente_metodologico"


def test_need_sin_senal_es_na_y_renormaliza():
    # NEED sin métodos ni problem_type derivable → compat_metodo N/A (no 0):
    # se excluye del score, los pesos restantes se re-normalizan y el techo de
    # 0.80 desaparece; el tipo metodológico queda (correctamente) inalcanzable.
    pair = _pair(
        sim_semantic=1.0,
        domains=("permanencia_estudiantil",), c_domains=("permanencia_estudiantil",),
        filled_fields=("f1", "f2", "f3", "f4"), expected_fields=4,
        has_capability_support=True, graph_linked=True,
    )
    fv = compute_features(pair)
    assert fv.compat_metodo is None

    score = compute_score(fv)
    assert 0.0 <= score <= 1.0
    assert score > 0.80  # sin N/A, el 0 de compat_metodo lo habría topado en ~0.80

    relation = classify_relation(fv, pair.candidate.entity_type)
    assert relation != "antecedente_metodologico"


def test_transferabilidad_tabla():
    assert transferability(("prediccion",), ("clasificacion_supervisada",)) > 0.8
    assert transferability(("prediccion",), ("encuesta",)) < 0.5
    assert transferability(("prediccion",), ("clasificacion_supervisada",)) > \
        transferability(("prediccion",), ("encuesta",))
    assert transferability(("prediccion",), ("metodo_inexistente",)) == 0.0
    assert transferability((), ("clasificacion_supervisada",)) == 0.0


def test_tipado_superficial():
    # Solo similitud léxica/semántica alta; método, dominio, capacidad y grafo bajos.
    pair = _pair(
        sim_semantic=0.85,
        keywords=("desercion", "riesgo"), c_keywords=("desercion", "riesgo"),
        methods=("etnografia",), c_methods=("optimizacion_lineal",),
        domains=("educacion",), c_domains=("logistica",),
        filled_fields=(), expected_fields=4,
        has_capability_support=False, graph_linked=False,
    )
    fv = compute_features(pair)
    relation = classify_relation(fv, pair.candidate.entity_type)
    assert relation == "coincidencia_superficial"


def test_arquitectura_dominio_puro():
    for path in DOMAIN_DIR.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue  # import relativo dentro del propio domain
                modules = [node.module.split(".")[0]] if node.module else []
            else:
                continue
            for module in modules:
                if module == "src":
                    continue  # import intra-domain (src.domain.*), no es dependencia externa
                assert module in ALLOWED_STDLIB, (
                    f"{path.name} importa '{module}', prohibido en domain/ (Regla A1)"
                )
