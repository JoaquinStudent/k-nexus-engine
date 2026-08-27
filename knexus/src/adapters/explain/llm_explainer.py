"""Adapter opcional: redacción vía LLM externo (TECH_STACK.md: "API Claude /
GPT", declarado y opcional). Grounding estricto — el prompt incluye SOLO los
datos ya verificados del `RankedConnection`/`Opportunity` y pide
explícitamente no inventar hechos ni cifras.

Si la llamada falla por CUALQUIER motivo (sin API key, sin red, SDK no
instalado, error del proveedor), degrada a `TemplateExplainer` — la cadena y
los scores siguen siendo válidos sin el LLM (Regla A4 / R5 de MEMORY.md:
"si cae la red en la demo, se cae el sistema" es justo lo que esto evita).
"""
from src.adapters.explain.template_explainer import (
    FEATURE_LABELS, OPPORTUNITY_TYPE_LABELS, RELATION_LABELS, TemplateExplainer,
)
from src.ports.explainer import Explainer

GROUNDING_INSTRUCTION = (
    "Redacta en español, en una o dos frases, SOLO a partir de los datos "
    "provistos abajo. No inventes entidades, cifras ni afirmaciones que no "
    "estén explícitas en los datos. Marca tu respuesta como una explicación "
    "generada, no como un hecho institucional adicional."
)


class LlmExplainer(Explainer):
    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022", fallback: Explainer = None):
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
        from anthropic import Anthropic  # import perezoso: SDK opcional (Regla A4)

        client = Anthropic(api_key=self._api_key)
        response = client.messages.create(
            model=self._model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
