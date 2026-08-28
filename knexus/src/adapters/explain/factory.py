"""Composition root del `Explainer`: decide qué adapter concreto instanciar.
`application/` nunca instancia `TemplateExplainer`/`LlmExplainer` directamente
(Regla A2) — llama a `build_explainer()`.

Sin `OPENROUTER_API_KEY` en el entorno, degrada automáticamente a
`TemplateExplainer` (Regla A4): la demo nunca depende de la red por defecto.
"""
import os

from src.adapters.explain.llm_explainer import LlmExplainer
from src.adapters.explain.template_explainer import TemplateExplainer
from src.ports.explainer import Explainer

API_KEY_ENV_VAR = "OPENROUTER_API_KEY"


def build_explainer() -> Explainer:
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if api_key:
        return LlmExplainer(api_key=api_key)
    return TemplateExplainer()
