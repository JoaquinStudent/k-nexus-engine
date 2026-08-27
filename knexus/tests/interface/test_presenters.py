"""Tests Rojo->Verde de la capa de presentación (`interface/presenters.py`).
Funciones puras: nada de FastAPI, nada de Jinja, nada de pipeline real."""
import pytest

from src.adapters.repository.dataset_paths import ENTITY_TABLES
from src.domain.models import FeatureVector
from src.domain.scoring import WEIGHTS, compute_score
from src.interface import presenters
from src.ports.entity_repository import StoredEntity


def _fv(**overrides):
    base = dict(
        sim_semantica=0.6, sim_lexica=0.1, compat_metodo=0.8, compat_dominio=0.5,
        densidad_evidencia=0.7, soporte_capacidad=1.0, enlace_estructural=0.0,
    )
    for key, value in overrides.items():
        base[key] = value
    return FeatureVector(**base)


def test_breakdown_tiene_las_7_features_en_orden_de_weights():
    fv = _fv()
    segments = presenters.breakdown_segments(fv)
    assert [s["name"] for s in segments] == list(WEIGHTS.keys())


def test_breakdown_suma_el_score():
    """Aditividad, mismo principio que `compute_score`/`comparar`: la suma de
    las contribuciones de los 7 segmentos reproduce EXACTO el score final."""
    fv = _fv(compat_metodo=0.9, compat_dominio=0.4, sim_semantica=0.7)
    segments = presenters.breakdown_segments(fv)
    total = sum(s["pct"] for s in segments) / 100
    assert total == pytest.approx(compute_score(fv), abs=1e-9)


def test_feature_na_se_pinta_na_no_cero():
    """ADR-007/ADR-009: `compat_metodo`/`compat_dominio` en None es N/A, nunca
    un 0 falso. La UI debe distinguirlo, no mostrar una barra vacía igual que
    una feature que de verdad puntuó 0."""
    fv = _fv(compat_metodo=None, compat_dominio=None)
    segments = presenters.breakdown_segments(fv)
    by_name = {s["name"]: s for s in segments}
    assert by_name["compat_metodo"]["na"] is True
    assert by_name["compat_metodo"]["value"] is None
    assert by_name["compat_metodo"]["pct"] == 0
    assert by_name["compat_dominio"]["na"] is True
    # las features SÍ medibles no deben marcarse N/A por contagio
    assert by_name["sim_semantica"]["na"] is False


def test_breakdown_re_normalizado_sigue_sumando_el_score_con_na():
    fv = _fv(compat_metodo=None, compat_dominio=None, sim_semantica=0.6)
    segments = presenters.breakdown_segments(fv)
    total = sum(s["pct"] for s in segments) / 100
    assert total == pytest.approx(compute_score(fv), abs=1e-9)


@pytest.mark.parametrize("score,expected", [(0.75, "alta"), (0.6, "alta"), (0.5, "media"), (0.4, "media"), (0.1, "baja")])
def test_relevance_band_usa_los_umbrales_del_dominio(score, expected):
    assert presenters.relevance_band(score) == expected


def test_title_of_cubre_los_13_tipos_de_entidad():
    for _relative_path, (entity_type, _id_col, text_cols) in ENTITY_TABLES.items():
        first_col = text_cols[0]
        entity = StoredEntity(
            entity_id="X-1", entity_type=entity_type,
            raw={first_col: "Un titulo de prueba con varias palabras de mas"},
        )
        title = presenters.title_of(entity)
        assert title, f"{entity_type} debe producir un titulo no vacio"


def test_title_of_trunca_descripciones_largas_sin_nombre_propio():
    """COMPETENCY/LEARNING_OUTCOME no tienen columna de nombre — su primer
    campo indexable ES la descripción larga; debe truncarse, no mostrarse entera."""
    long_text = " ".join(f"palabra{i}" for i in range(40))
    entity = StoredEntity(entity_id="COMP-1", entity_type="COMPETENCY", raw={"description": long_text})
    title = presenters.title_of(entity)
    assert len(title) < len(long_text)


def test_title_of_no_trunca_nombres_cortos():
    entity = StoredEntity(entity_id="PRJ-004", entity_type="PROJECT", raw={"title": "Análisis de permanencia universitaria"})
    assert presenters.title_of(entity) == "Análisis de permanencia universitaria"
