"""Adapter opcional: redacción vía LLM externo, a través de OpenRouter
(API compatible con OpenAI chat completions, enruta a cualquier modelo —
Claude, GPT, Llama...). Grounding estricto — el prompt incluye SOLO los
datos ya verificados del `RankedConnection`/`Opportunity` y pide
explícitamente no inventar hechos ni cifras.

Si la llamada falla por CUALQUIER motivo (sin API key, sin red, error del
proveedor), degrada a `TemplateExplainer` — la cadena y los scores siguen
siendo válidos sin el LLM (Regla A4 / R5 de MEMORY.md: "si cae la red en la
demo, se cae el sistema" es justo lo que esto evita).
"""
import httpx

from src.adapters.explain.template_explainer import (
    FEATURE_LABELS, OPPORTUNITY_TYPE_LABELS, RELATION_LABELS, TemplateExplainer,
)
from src.ports.explainer import Explainer

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

GROUNDING_INSTRUCTION = (
    "Redacta en español, en una o dos frases, SOLO a partir de los datos "
    "provistos abajo. No inventes entidades, cifras ni afirmaciones que no "
    "estén explícitas en los datos. Marca tu respuesta como una explicación "
    "generada, no como un hecho institucional adicional."
)


class LlmExplainer(Explainer):
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-haiku", fallback: Explainer = None):
        self._api_key = api_key
        self._model = model
        self._fallback = fallback or TemplateExplainer()

    def explain_connection(self, connection) -> str:
        try:
            return self._call_llm(self._connection_prompt(connection))
        except Exception:
            return self._fallback.explain_connection(connection)

    def explain_opportunity(self, opportunity) -> str:
        try:
            return self._call_llm(self._opportunity_prompt(opportunity))
        except Exception:
            return self._fallback.explain_opportunity(opportunity)

    def _connection_prompt(self, connection) -> str:
        scored = connection.scored
        features = ", ".join(
            f"{FEATURE_LABELS.get(name, name)}={value:.2f}"
            for name, value, _ in connection.top_features
        )
        return (
            f"{GROUNDING_INSTRUCTION}\n\n"
            f"Entidad: {connection.entity.entity_id}\n"
            f"Tipo de relación: {RELATION_LABELS.get(scored.relation_type, scored.relation_type)}\n"
            f"Score: {scored.score:.2f}\n"
            f"Features que más pesaron: {features}"
        )

    def _opportunity_prompt(self, opportunity) -> str:
        chain = " -> ".join(f"{link.role}:{link.entity_id}({link.link_type})" for link in opportunity.links)
        return (
            f"{GROUNDING_INSTRUCTION}\n\n"
            f"Necesidad: {opportunity.need_id}\n"
            f"Tipo de oportunidad: {OPPORTUNITY_TYPE_LABELS.get(opportunity.opportunity_type, opportunity.opportunity_type)}\n"
            f"Prioridad: {opportunity.priority}\n"
            f"Cadena: {chain}\n"
            f"Score del antecedente: {opportunity.score:.2f}"
        )

    def _call_llm(self, prompt: str) -> str:
        response = httpx.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
