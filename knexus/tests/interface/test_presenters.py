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


class _NoGraph:
    def neighbors(self, entity_id):
        return ()


def test_subgraph_svg_escapa_entity_id_de_texto_libre():
    """`entity_id` puede ser texto libre sin validar (consulta en texto libre
    -> StoredEntity placeholder, `ui/routes.py:_query_entity_or_placeholder`).
    El SVG se renderiza con `| safe` en connection.html — si no se escapa aquí,
    una query como '<script>...' se ejecuta en el navegador (XSS reflejado
    vía el parámetro `q`)."""
    malicious = StoredEntity(entity_id="<script>alert(1)</script>", entity_type="QUERY")
    svg = presenters.subgraph_svg(malicious, malicious, (), graph=_NoGraph())
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg


# --- serialize_metrics (M8, Sprint-07) ---

def _sample_report(**overrides):
    report = {
        "needs_evaluated": 2,
        "avg_latency_ms": 210.5,
        "avg_dense_latency_ms": 1.8,
        "evidence_coverage": 0.91,
        "precision_recall": {
            "cluster": {
                "full": {"p5": 0.6, "p10": 0.5, "r10": 0.2, "r30": 0.4, "mrr": 0.7},
                "cosine": {"p5": 0.3, "p10": 0.25, "r10": 0.1, "r30": 0.2, "mrr": 0.4},
                "dense": {"p5": 0.2, "p10": 0.15, "r10": 0.05, "r30": 0.15, "mrr": 0.3},
            },
            "strict": {
                "full": {"p5": 0.5, "p10": 0.4, "r10": 0.15, "r30": 0.3, "mrr": 0.6},
                "cosine": {"p5": 0.2, "p10": 0.2, "r10": 0.08, "r30": 0.18, "mrr": 0.3},
                "dense": {"p5": 0.1, "p10": 0.1, "r10": 0.04, "r30": 0.1, "mrr": 0.2},
            },
        },
        "recall_ceilings": {
            "cluster": {"r10_ceiling": 0.36, "r30_ceiling": 0.97},
            "strict": {"r10_ceiling": 0.30, "r30_ceiling": 0.90},
        },
        "construct_validity": {
            "full": {"trap_rate": 0.18, "capability_rate": 0.43, "method_rate": 0.44, "actionable_rate": 0.63, "unscored_rate": 0.0},
            "cosine": {"trap_rate": 0.5, "capability_rate": 0.1, "method_rate": 0.1, "actionable_rate": 0.2, "unscored_rate": 0.0},
            "dense": {"trap_rate": 0.6, "capability_rate": 0.05, "method_rate": 0.05, "actionable_rate": 0.1, "unscored_rate": 0.3},
        },
        "per_need": [
            {"need_id": "NEED-001", "relevant_cluster": 6, "relevant_strict": 1,
             "p5_full": 0.6, "p5_cosine": 0.3, "p5_dense": 0.2, "latency_ms": 200.0},
            {"need_id": "NEED-005", "relevant_cluster": 4, "relevant_strict": 1,
             "p5_full": 0.6, "p5_cosine": 0.3, "p5_dense": 0.2, "latency_ms": 221.0},
        ],
        "meta": {
            "generated_at": "2026-08-27T00:00:00+00:00",
            "provider": "paraphrase-multilingual-MiniLM-L12-v2",
            "fast": False,
            "entities_indexed": 2512,
            "qrels_rows": 97,
            "needs_evaluated": 2,
            "top_k_primary": 5,
            "top_k_secondary": 10,
            "top_k_recall_wide": 30,
            "elapsed_s": 120.0,
        },
    }
    report.update(overrides)
    return report


def test_serialize_metrics_sin_reporte_es_estado_valido_no_error():
    result = presenters.serialize_metrics(None)
    assert result == {"available": False}


def test_serialize_metrics_shape_completo():
    result = presenters.serialize_metrics(_sample_report())
    assert result["available"] is True
    assert len(result["stat_tiles"]) == 3
    assert len(result["precision_at_k"]) == 2
    assert [row["arm"] for row in result["ablation"]] == ["full", "cosine", "dense"]
    assert len(result["construct_validity"]) == 3
    assert result["per_need"][0]["need_id"] == "NEED-001"


def test_serialize_metrics_deltas_son_exactos():
    result = presenters.serialize_metrics(_sample_report())
    assert result["ablation_delta_cosine"] == pytest.approx(0.6 - 0.3)
    assert result["ablation_delta_dense"] == pytest.approx(0.6 - 0.2)


def test_serialize_metrics_barras_acotadas_0_100():
    result = presenters.serialize_metrics(_sample_report())
    for row in result["ablation"]:
        assert 0.0 <= row["pct"] <= 100.0
    for row in result["precision_at_k"]:
        assert 0.0 <= row["pct"] <= 100.0
