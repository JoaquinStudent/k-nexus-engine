"""domain/opportunity.py — PURO (Regla A1). Tipo de oportunidad y prioridad a
partir de la cadena de ChainLink ya ensamblada (Sprint-05)."""
from src.domain.opportunity import ChainLink, classify_opportunity, opportunity_priority


def _link(role, link_type, score=None, entity_id="X", entity_type="project", relation_type=""):
    return ChainLink(
        role=role, entity_id=entity_id, entity_type=entity_type,
        link_type=link_type, score=score, relation_type=relation_type,
    )


# ---------------------------------------------------------------------------
# classify_opportunity — tabla de casos
# ---------------------------------------------------------------------------

def test_continuidad_investigativa_antecedente_metodologico_con_investigador():
    links = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.7, relation_type="antecedente_metodologico"),
        _link("investigador", "edge", entity_type="researcher"),
    )
    assert classify_opportunity(links) == "continuidad_investigativa"


def test_activacion_capacidad_cuando_antecedente_no_aporta_metodo_fuerte():
    links = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.5, relation_type="antecedente_relevante"),
        _link("capacidad", "inferred", entity_type="capability"),
    )
    assert classify_opportunity(links) == "activacion_capacidad"


def test_metodologico_gana_sobre_capacidad_si_ambos_presentes():
    # Prioridad: continuidad_investigativa antes que activacion_capacidad.
    links = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.8, relation_type="antecedente_metodologico"),
        _link("investigador", "edge", entity_type="researcher"),
        _link("capacidad", "inferred", entity_type="capability"),
    )
    assert classify_opportunity(links) == "continuidad_investigativa"


def test_integracion_curricular_cuando_hay_componente_curricular():
    links = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.5, relation_type="antecedente_relevante"),
        _link("curriculo", "edge", score=0.6, entity_type="subject"),
    )
    assert classify_opportunity(links) == "integracion_curricular"


def test_colaboracion_interdisciplinaria_cuando_se_marca_cross_faculty():
    links = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.4, relation_type="coincidencia_superficial"),
        _link("investigador", "edge", entity_type="researcher"),
    )
    assert classify_opportunity(links, cross_faculty=True) == "colaboracion_interdisciplinaria"


def test_exploratoria_como_resto():
    links = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.3, relation_type="coincidencia_superficial"),
    )
    assert classify_opportunity(links) == "exploratoria"


# ---------------------------------------------------------------------------
# opportunity_priority
# ---------------------------------------------------------------------------

def test_prioridad_sube_con_el_score_del_antecedente():
    bajo = (_link("necesidad", "retrieved", entity_type="need"), _link("antecedente", "retrieved", score=0.2))
    alto = (_link("necesidad", "retrieved", entity_type="need"), _link("antecedente", "retrieved", score=0.8))
    assert opportunity_priority(alto) != "baja" or opportunity_priority(bajo) == "baja"
    assert _priority_rank(opportunity_priority(alto)) >= _priority_rank(opportunity_priority(bajo))


def test_prioridad_sube_con_mas_eslabones_duros_a_igual_score():
    solo_antecedente = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.65, relation_type="antecedente_metodologico"),
    )
    cadena_completa = (
        _link("necesidad", "retrieved", entity_type="need"),
        _link("antecedente", "retrieved", score=0.65, relation_type="antecedente_metodologico"),
        _link("investigador", "edge", entity_type="researcher"),
        _link("curriculo", "edge", score=0.5, entity_type="subject"),
    )
    assert _priority_rank(opportunity_priority(cadena_completa)) > _priority_rank(opportunity_priority(solo_antecedente))


def test_sin_antecedente_prioridad_es_baja():
    links = (_link("necesidad", "retrieved", entity_type="need"),)
    assert opportunity_priority(links) == "baja"


def _priority_rank(p):
    return {"baja": 0, "media": 1, "alta": 2}[p]
