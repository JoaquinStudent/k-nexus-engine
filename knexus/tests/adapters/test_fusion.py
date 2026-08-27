"""Fusión RRF + agregación campo→entidad (Sprint-04)."""
from src.adapters.retrieval.fusion import aggregate_by_entity, fuse, reciprocal_rank_fusion
from src.ports.entity_repository import Provenance


def _prov(entity_id, field_name, source_file="x.csv"):
    return Provenance(source_file=source_file, entity_type="PROJECT", entity_id=entity_id, field_name=field_name)


def test_aggregate_by_entity_se_queda_con_el_mejor_campo():
    hits = (
        (_prov("PRJ-004", "title"), 0.3),
        (_prov("PRJ-004", "methodology"), 0.9),
        (_prov("PRJ-002", "abstract"), 0.5),
    )
    agg = aggregate_by_entity(hits)
    assert agg["PRJ-004"] == (_prov("PRJ-004", "methodology"), 0.9)
    assert agg["PRJ-002"][1] == 0.5


def test_rrf_determinista_mismo_input_mismo_output():
    ranking_a = ("PRJ-004", "PRJ-002", "PRJ-007")
    ranking_b = ("PRJ-002", "PRJ-004", "PRJ-010")
    r1 = reciprocal_rank_fusion(ranking_a, ranking_b)
    r2 = reciprocal_rank_fusion(ranking_a, ranking_b)
    assert r1 == r2


def test_rrf_favorece_lo_que_aparece_arriba_en_ambos_rankings():
    ranking_denso = ("PRJ-004", "PRJ-002", "PRJ-007")
    ranking_lexico = ("PRJ-002", "PRJ-004", "PRJ-010")
    scores = reciprocal_rank_fusion(ranking_denso, ranking_lexico)
    # PRJ-004 y PRJ-002 están en el top-2 de ambos; PRJ-007/PRJ-010 solo en uno.
    assert scores["PRJ-004"] > scores["PRJ-007"]
    assert scores["PRJ-002"] > scores["PRJ-010"]


def test_rrf_entidad_ausente_de_un_ranking_no_se_rellena_con_cero():
    # Sólo aparece en un ranking: su score es simplemente la contribución de
    # ESE ranking, no se penaliza artificialmente por "no aparecer" en el otro.
    scores = reciprocal_rank_fusion(("A",), ())
    assert scores == {"A": 1.0 / (60 + 1)}


def test_fuse_evidencia_prefiere_el_campo_denso():
    dense_hits = ((_prov("PRJ-004", "methodology"), 0.9),)
    bm25_hits = ((_prov("PRJ-004", "title"), 12.0),)
    result = fuse(dense_hits, bm25_hits, top_n=10)
    assert len(result) == 1
    candidate = result[0]
    assert candidate.entity_id == "PRJ-004"
    assert candidate.evidence.field_name == "methodology"
    assert candidate.sim_semantic == 0.9


def test_fuse_entidad_solo_lexica_usa_evidencia_lexica_y_sim_cero():
    bm25_hits = ((_prov("THS-001", "abstract"), 8.0),)
    result = fuse((), bm25_hits, top_n=10)
    assert result[0].entity_id == "THS-001"
    assert result[0].evidence.field_name == "abstract"
    assert result[0].sim_semantic == 0.0


def test_fuse_respeta_top_n():
    dense_hits = tuple((_prov(f"E{i}", "title"), 1.0 - i * 0.01) for i in range(20))
    result = fuse(dense_hits, (), top_n=5)
    assert len(result) == 5


def test_fuse_orden_desciende_por_rrf_score():
    dense_hits = tuple((_prov(f"E{i}", "title"), 1.0 - i * 0.01) for i in range(10))
    result = fuse(dense_hits, (), top_n=10)
    scores = [c.rrf_score for c in result]
    assert scores == sorted(scores, reverse=True)
