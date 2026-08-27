"""query_builder.py: NEED/entidad existente vs texto libre."""
import pytest

from src.adapters.repository.dataset_repository import DatasetEntityRepository
from src.application.query_builder import build_query


@pytest.fixture(scope="module")
def repo():
    return DatasetEntityRepository()


def test_id_existente_delega_en_to_query_entity(repo):
    query = build_query("NEED-001", repo)
    assert query.entity_type == "need"
    assert "prediccion" in query.problem_types
    assert query.methods == ()  # el NEED nunca trae método (por diseño, ADR-007)


def test_texto_libre_infiere_problem_type_y_sector():
    query = build_query("predicción y prevención de deserción estudiantil", repo=_EmptyRepo())
    assert query.entity_type == "query"
    assert "prediccion" in query.problem_types
    assert "educacion" in query.domains
    assert query.methods == ()  # nunca se asigna método a texto libre


def test_texto_libre_sin_senal_cae_a_vacio_no_revienta():
    query = build_query("hola, esto no matchea ningun vocabulario controlado", repo=_EmptyRepo())
    assert query.problem_types == ()
    assert query.domains == ()


def test_texto_en_ingles_tambien_se_reconoce_como_texto_libre():
    query = build_query("student attrition prediction", repo=_EmptyRepo())
    assert query.entity_type == "query"


class _EmptyRepo:
    """Repo vacío para probar la rama de texto libre sin depender de la carga real."""
    def get(self, entity_id):
        raise KeyError(entity_id)
