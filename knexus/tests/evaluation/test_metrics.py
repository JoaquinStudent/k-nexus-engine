"""Tests Rojo->Verde de `evaluation/metrics.py` — funciones puras, sin
pipeline ni dataset real."""
import pytest

from evaluation.metrics import mean, mrr, precision_at_k, recall_at_k


def test_precision_at_k_conocido():
    ranked = ["a", "b", "c", "d", "e"]
    relevant = {"a", "c", "z"}
    assert precision_at_k(ranked, relevant, 5) == pytest.approx(2 / 5)
    assert precision_at_k(ranked, relevant, 1) == pytest.approx(1.0)


def test_precision_at_k_ranked_mas_corto_que_k_no_infla_el_score():
    ranked = ["a"]
    relevant = {"a", "b", "c"}
    # k=5 pero sólo hay 1 candidato -- el denominador sigue siendo k, no len(ranked)
    assert precision_at_k(ranked, relevant, 5) == pytest.approx(1 / 5)


def test_recall_at_k_conocido():
    ranked = ["a", "b", "c", "d", "e"]
    relevant = {"a", "c", "z"}
    assert recall_at_k(ranked, relevant, 5) == pytest.approx(2 / 3)


def test_recall_at_k_reporta_su_techo():
    """R@k nunca puede exceder k/len(relevant) -- el techo se expone, no se
    esconde (SPEC.md §13: pool de 28 relevantes -> R@10 tope 0.36)."""
    ranked = list("abcdefghij")  # 10 candidatos, todos relevantes
    relevant = set("abcdefghij") | {"z1", "z2", "z3", "z4", "z5", "z6", "z7", "z8", "z9", "z10",
                                     "z11", "z12", "z13", "z14", "z15", "z16", "z17", "z18"}  # 28 total
    r10 = recall_at_k(ranked, relevant, 10)
    assert r10 == pytest.approx(10 / 28)
    assert r10 < 10 / 10


def test_recall_sin_relevantes_es_cero_no_division_por_cero():
    assert recall_at_k(["a", "b"], set(), 5) == 0.0


def test_mrr_encuentra_el_primer_relevante():
    ranked = ["x", "y", "a", "z"]
    relevant = {"a"}
    assert mrr(ranked, relevant) == pytest.approx(1 / 3)


def test_mrr_sin_relevantes_es_cero():
    assert mrr(["a", "b", "c"], set()) == 0.0
    assert mrr(["a", "b", "c"], {"nope"}) == 0.0


def test_mrr_relevante_en_primera_posicion():
    assert mrr(["a", "b"], {"a"}) == 1.0


def test_mean_de_vacio_es_cero():
    assert mean([]) == 0.0


def test_mean_conocido():
    assert mean([1.0, 2.0, 3.0]) == pytest.approx(2.0)
