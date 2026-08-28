"""ports/explainer.py + adapters/explain/ — Regla A4 (degradación) y la regla
que no se rompe: el Explainer redacta, nunca aporta hechos."""
import re

import pytest

from src.adapters.explain.factory import build_explainer
from src.adapters.explain.llm_explainer import LlmExplainer
from src.adapters.explain.template_explainer import TemplateExplainer
from src.application.descubrir_conexiones import RankedConnection
from src.domain.models import FeatureVector, ScoredResult
from src.domain.opportunity import ChainLink, Opportunity
from src.ports.entity_repository import StoredEntity


def _feature_vector(**overrides):
    base = dict(
        sim_semantica=0.7, sim_lexica=0.0, compat_metodo=0.9, compat_dominio=0.5,
        densidad_evidencia=0.87, soporte_capacidad=1.0, enlace_estructural=0.0,
    )
    base.update(overrides)
    return FeatureVector(**base)


def _connection():
    fv = _feature_vector()
    scored = ScoredResult(entity_id="PRJ-004", feature_vector=fv, score=0.652, relation_type="antecedente_metodologico")
    entity = StoredEntity(entity_id="PRJ-004", entity_type="PROJECT")
    return RankedConnection(
        rank=1, scored=scored, entity=entity,
        evidence=None, evidence_text="",
        top_features=(("compat_metodo", 0.9, 0.18), ("soporte_capacidad", 1.0, 0.15)),
    )


def _opportunity():
    links = (
        ChainLink(role="necesidad", entity_id="NEED-001", entity_type="need", link_type="retrieved"),
        ChainLink(role="antecedente", entity_id="PRJ-004", entity_type="project", link_type="retrieved",
                  score=0.652, relation_type="antecedente_metodologico"),
        ChainLink(role="investigador", entity_id="INV-127", entity_type="researcher", link_type="edge"),
    )
    return Opportunity(
        need_id="NEED-001", links=links,
        opportunity_type="continuidad_investigativa", priority="alta", score=0.652,
    )


# ---------------------------------------------------------------------------
# TemplateExplainer: sin red, determinista
# ---------------------------------------------------------------------------

def test_template_explainer_es_determinista():
    explainer = TemplateExplainer()
    connection = _connection()
    assert explainer.explain_connection(connection) == explainer.explain_connection(connection)


def test_template_explainer_menciona_la_entidad_y_el_tipo_de_relacion():
    explainer = TemplateExplainer()
    text = explainer.explain_connection(_connection())
    assert "PRJ-004" in text
    assert "0.65" in text  # score, redondeado


def test_template_explainer_explica_oportunidad():
    explainer = TemplateExplainer()
    text = explainer.explain_opportunity(_opportunity())
    assert "NEED-001" in text
    assert "PRJ-004" in text
    assert "INV-127" in text
    assert "alta" in text


# ---------------------------------------------------------------------------
# ★ Grounding: la salida no inventa identificadores ni cifras
# ---------------------------------------------------------------------------

def _entity_ids_in(text: str) -> set:
    return set(re.findall(r"\b[A-Z]{2,4}-\d{3,4}\b", text))


def test_grounding_connection_no_inventa_ids():
    connection = _connection()
    text = TemplateExplainer().explain_connection(connection)
    input_ids = {connection.entity.entity_id, connection.scored.entity_id}
    assert _entity_ids_in(text) <= input_ids


def test_grounding_opportunity_no_inventa_ids():
    opportunity = _opportunity()
    text = TemplateExplainer().explain_opportunity(opportunity)
    input_ids = {link.entity_id for link in opportunity.links} | {opportunity.need_id}
    assert _entity_ids_in(text) <= input_ids


def test_grounding_numeros_provienen_del_input():
    connection = _connection()
    text = TemplateExplainer().explain_connection(connection)
    numbers_in_text = {float(n) for n in re.findall(r"\d+\.\d+", text)}
    allowed = {round(connection.scored.score, 2)} | {
        round(value, 2) for _, value, _ in connection.top_features
    }
    assert numbers_in_text <= allowed


# ---------------------------------------------------------------------------
# LlmExplainer: degrada sin API key válida / sin red / si falla la llamada
# ---------------------------------------------------------------------------

def _romper_httpx(monkeypatch):
    # Simula "sin red" sin depender de una llamada real a OpenRouter — los
    # tests corren sin red (README §4: "pytest -m 'not slow', sin red").
    import httpx

    def _raise(*args, **kwargs):
        raise httpx.ConnectError("sin red (test)")

    monkeypatch.setattr(httpx, "post", _raise)


def test_llm_explainer_sin_api_key_valida_degrada_a_template(monkeypatch):
    _romper_httpx(monkeypatch)
    explainer = LlmExplainer(api_key="sk-invalid-key-para-test")
    connection = _connection()
    text = explainer.explain_connection(connection)
    assert text == TemplateExplainer().explain_connection(connection)


def test_llm_explainer_opportunity_tambien_degrada(monkeypatch):
    _romper_httpx(monkeypatch)
    explainer = LlmExplainer(api_key="sk-invalid-key-para-test")
    opportunity = _opportunity()
    text = explainer.explain_opportunity(opportunity)
    assert text == TemplateExplainer().explain_opportunity(opportunity)


def test_factory_sin_env_var_devuelve_template_explainer(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    explainer = build_explainer()
    assert isinstance(explainer, TemplateExplainer)


def test_factory_con_env_var_devuelve_llm_explainer(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    explainer = build_explainer()
    assert isinstance(explainer, LlmExplainer)
