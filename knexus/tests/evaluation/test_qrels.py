"""Valida `evaluation/qrels.csv` contra el repositorio REAL — no contra un
fixture a mano. El set etiquetado es el cimiento de Sprint-07: si un
`application_context` está mal escrito, el cluster de relevancia queda vacío
y P@K sale falsamente bajo sin que nada lo avise (caza "label rot")."""
import pytest

from evaluation import qrels
from src.adapters.repository.dataset_repository import DatasetEntityRepository


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


@pytest.fixture(scope="module")
def rows():
    return qrels.load_rows()


def test_todo_need_id_existe_en_el_repo(repo, rows):
    need_ids = {e.entity_id for e in repo.by_type("NEED")}
    faltantes = sorted({row.need_id for row in rows} - need_ids)
    assert not faltantes, f"need_id en qrels.csv que no existen en el dataset: {faltantes}"


def test_todo_contexto_matchea_al_menos_una_entidad(repo, rows):
    """El test que caza un `application_context` mal escrito: si el string no
    matchea NINGUNA entidad PROJECT/THESIS real, es casi seguro un typo."""
    errors = qrels.validation_errors(repo, rows)
    typo_errors = [e for e in errors if "no matchea ninguna entidad" in e]
    assert not typo_errors, "\n".join(typo_errors)


def test_ningun_cluster_vacio(repo, rows):
    relevant = qrels.build_relevant_sets(repo, rows)
    vacios = [need_id for need_id in qrels.needs_covered(rows) if not relevant.get(need_id)]
    assert not vacios, f"needs con cluster de relevancia vacío: {vacios}"


def test_validation_errors_vacio_sobre_el_set_real(repo, rows):
    """El set commiteado debe pasar su propia validación — si esto falla, el
    resto de Sprint-07 mide sobre un set roto."""
    assert qrels.validation_errors(repo, rows) == ()


def test_cluster_agrupa_es_en_need001():
    """Caso de referencia (SPEC.md): NEED-001 agrupa 'permanencia estudiantil'
    y 'student attrition' — el cruce ES/EN que el sistema debe resolver."""
    rows_ = qrels.load_rows()
    contexts = {row.context for row in rows_ if row.need_id == "NEED-001"}
    assert "permanencia estudiantil" in contexts
    assert "student attrition" in contexts


def test_strict_toma_solo_la_primera_fila_por_need(repo, rows):
    strict = qrels.build_relevant_sets(repo, rows, strict=True)
    full = qrels.build_relevant_sets(repo, rows, strict=False)
    # la variante estricta nunca puede ser más grande que la del cluster completo
    for need_id in qrels.needs_covered(rows):
        assert strict.get(need_id, set()) <= full.get(need_id, set())


def test_meta_needs_fuera_de_alcance_no_estan_en_qrels(rows):
    """NEED-021..042 son necesidades meta/institucionales sin candidato
    temático real (verificado en la auditoría del sprint) — no deben
    aparecer etiquetadas."""
    covered = set(qrels.needs_covered(rows))
    meta_needs = {f"NEED-{i:03d}" for i in range(21, 43)}
    assert not (covered & meta_needs)
