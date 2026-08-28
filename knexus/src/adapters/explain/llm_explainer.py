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
    FEATURE_HELP, FEATURE_LABELS, LINK_TYPE_LABELS, OPPORTUNITY_TYPE_HELP, OPPORTUNITY_TYPE_LABELS,
    RELATION_HELP, RELATION_LABELS, ROLE_LABELS, TemplateExplainer,
)
from src.ports.explainer import Explainer

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LlmExplainer(Explainer):
    def __init__(self, api_key: str, model: str = "anthropic/claude-haiku-4.5", fallback: Explainer = None):
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

    def explain_comparison(self, comparison) -> str:
        try:
            return self._call_llm(self._comparison_prompt(comparison))
        except Exception:
            return self._fallback.explain_comparison(comparison)

    def _connection_prompt(self, connection) -> str:
        scored = connection.scored
        relation_label = RELATION_LABELS.get(scored.relation_type, scored.relation_type)
        relation_meaning = RELATION_HELP.get(scored.relation_type, "")
        features = "\n".join(
            f"- {FEATURE_LABELS.get(name, name)} = {value:.2f} ({FEATURE_HELP.get(name, '')})"
            for name, value, _ in connection.top_features
        )
        return (
            "El score y el tipo de relación de esta conexión YA se muestran en pantalla — "
            "no los repitas ni los reformules. Tu tarea es otra: en español, 2 o 3 frases, "
            "lenguaje cotidiano pero analítico (nada de jerga de sistema de puntuación), dale "
            "a alguien de la universidad una RECOMENDACIÓN práctica sobre qué hacer con esta "
            "conexión y por qué — apóyate en el significado de las features dominantes de "
            "abajo, no en repetir sus números. No inventes entidades, cifras ni datos fuera de "
            "los provistos. Marca tu respuesta como una explicación generada, no como un hecho "
            "institucional adicional.\n\n"
            f"Entidad: {connection.entity.entity_id}\n"
            f"Tipo de relación: {relation_label} ({relation_meaning})\n"
            f"Features dominantes:\n{features}"
        )

    def _opportunity_prompt(self, opportunity) -> str:
        type_label = OPPORTUNITY_TYPE_LABELS.get(opportunity.opportunity_type, opportunity.opportunity_type)
        type_meaning = OPPORTUNITY_TYPE_HELP.get(opportunity.opportunity_type, "")
        chain = "\n".join(
            f"- {ROLE_LABELS.get(link.role, link.role)} {link.entity_id} "
            f"({LINK_TYPE_LABELS.get(link.link_type, link.link_type)})"
            for link in opportunity.links
        )
        return (
            "El tipo de oportunidad, la prioridad y la cadena de eslabones YA se muestran en "
            "pantalla — no los repitas ni los reformules. Tu tarea es otra: en español, 2 o 3 "
            "frases, lenguaje cotidiano pero analítico, dale una RECOMENDACIÓN práctica sobre "
            "el siguiente paso concreto con esta oportunidad — apóyate en qué tan firme es cada "
            "eslabón (su tipo de vínculo, abajo) y en el significado del tipo de oportunidad, no "
            "en repetir los datos. No inventes entidades, personas ni datos fuera de los "
            "provistos. Marca tu respuesta como una explicación generada, no como un hecho "
            "institucional adicional.\n\n"
            f"Necesidad: {opportunity.need_id}\n"
            f"Tipo de oportunidad: {type_label} ({type_meaning})\n"
            f"Cadena:\n{chain}"
        )

    def _comparison_prompt(self, comparison) -> str:
        a_id = comparison.connection_a.entity.entity_id
        b_id = comparison.connection_b.entity.entity_id
        winner_id, loser_id = (a_id, b_id) if comparison.score_delta >= 0 else (b_id, a_id)

        def _winner_of(f) -> str:
            # Mismo criterio que `presenters._display_favors`: si redondeado a
            # 2 decimales ambos valores se ven iguales, no hay ganador que
            # explicar — evita que el LLM invente un motivo para 0.63 vs 0.63.
            if f.value_a is not None and f.value_b is not None and round(f.value_a, 2) == round(f.value_b, 2):
                return "ninguno, empate"
            return a_id if f.favors == "A" else b_id if f.favors == "B" else "ninguno, empate"

        rows = "\n".join(
            f"- {FEATURE_LABELS.get(f.name, f.name)} ({FEATURE_HELP.get(f.name, '')}): {a_id}="
            f"{'N/A' if f.value_a is None else f'{f.value_a:.2f}'}, {b_id}="
            f"{'N/A' if f.value_b is None else f'{f.value_b:.2f}'}"
            f" (gana {_winner_of(f)})"
            for f in comparison.features
        )
        dominant_label = FEATURE_LABELS.get(comparison.dominant_feature, comparison.dominant_feature)
        dominant_meaning = FEATURE_HELP.get(comparison.dominant_feature, "")
        return (
            "Vas a explicarle el resultado de una auditoría de ranking a alguien SIN "
            "ningún conocimiento técnico — nunca vio un score, un peso ni una 'feature' "
            "en su vida. Redacta en español, en 2 o 3 frases, usando SOLO los datos "
            "provistos abajo (no inventes entidades, cifras ni afirmaciones fuera de "
            "ellos). PROHIBIDO: repetir la frase 'rankea más alto' o reformular el "
            "número de la diferencia de puntos — eso ya se muestra arriba en pantalla, "
            "tu trabajo es explicar el PORQUÉ en términos prácticos y cotidianos "
            "(qué tiene uno que al otro le falta, en la vida real, no en el sistema de "
            "puntuación). Apóyate en el significado de la feature decisiva, que va entre "
            "paréntesis abajo. Marca tu respuesta como una explicación generada, no como "
            "un hecho institucional adicional.\n\n"
            f"Ganador: {winner_id} — Perdedor: {loser_id}\n"
            f"Feature decisiva: {dominant_label} ({dominant_meaning})\n"
            f"Detalle por feature (nombre, qué mide, valor de cada uno, quién gana esa fila):\n{rows}"
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
