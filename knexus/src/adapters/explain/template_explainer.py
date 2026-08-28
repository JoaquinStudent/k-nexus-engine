"""Adapter de degradación (Regla A4) y explainer POR DEFECTO: determinista,
sin red, sin dependencias. Redacta EXCLUSIVAMENTE a partir de los campos del
`RankedConnection`/`Opportunity` recibidos — cualquier identificador o valor
numérico en la salida debe poder trazarse al input (test de grounding).
"""
from src.ports.explainer import Explainer

FEATURE_LABELS = {
    "sim_semantica": "similitud semántica",
    "sim_lexica": "coincidencia léxica",
    "compat_metodo": "método transferible",
    "compat_dominio": "dominio compatible",
    "densidad_evidencia": "evidencia documental",
    "soporte_capacidad": "capacidad institucional disponible",
    "enlace_estructural": "vínculo con investigadores",
}

RELATION_LABELS = {
    "antecedente_metodologico": "antecedente metodológico",
    "antecedente_relevante": "antecedente relevante",
    "activacion_capacidad": "activación de capacidad",
    "investigador_complementario": "investigador complementario",
    "integracion_curricular": "integración curricular",
    "coincidencia_superficial": "coincidencia superficial",
}

ROLE_LABELS = {
    "necesidad": "necesidad",
    "antecedente": "antecedente",
    "investigador": "investigador",
    "capacidad": "capacidad institucional",
    "curriculo": "componente curricular",
}

LINK_TYPE_LABELS = {
    "retrieved": "recuperado por búsqueda y puntuado",
    "edge": "vínculo verificado en los datos",
    "inferred": "inferido por reglas explícitas",
}

OPPORTUNITY_TYPE_LABELS = {
    "continuidad_investigativa": "continuidad investigativa",
    "activacion_capacidad": "activación de capacidad",
    "integracion_curricular": "integración curricular",
    "colaboracion_interdisciplinaria": "colaboración interdisciplinaria",
    "exploratoria": "exploratoria",
}

OPPORTUNITY_TYPE_HELP = {
    "continuidad_investigativa": "hay un antecedente metodológico fuerte y un investigador conectado — conviene seguir esa línea con esa persona.",
    "activacion_capacidad": "hay una capacidad institucional instalada que coincide, aunque el método del antecedente no sea el mismo.",
    "integracion_curricular": "la conexión llega hasta un componente curricular — puede alimentar formación, no sólo investigación.",
    "colaboracion_interdisciplinaria": "el investigador conectado es de otra facultad — el valor está en el cruce entre áreas.",
    "exploratoria": "la conexión existe pero aún no tiene un eslabón fuerte (capacidad, currículo o investigador) que la respalde.",
}

# Glosario para el usuario nuevo (M9/UX): una línea por concepto, sin jerga de
# implementación. Fuente única — la UI (`presenters.py`) lo reusa en vez de
# duplicar texto en las plantillas Jinja.
FEATURE_HELP = {
    "sim_semantica": "qué tan parecido es el significado del texto, más allá de las palabras exactas.",
    "sim_lexica": "coincidencia de palabras literales — la señal más débil, para no premiar la trampa léxica.",
    "compat_metodo": "si el método de investigación es el mismo o transferible entre ambos.",
    "compat_dominio": "si pertenecen al mismo sector o dominio institucional.",
    "densidad_evidencia": "cuánta documentación verificable respalda a este candidato.",
    "soporte_capacidad": "si existe una capacidad institucional real que activar.",
    "enlace_estructural": "si hay un vínculo directo con investigadores en los datos.",
}

RELATION_HELP = {
    "antecedente_metodologico": "usa un método que se puede transferir directamente a la necesidad.",
    "antecedente_relevante": "aborda el mismo tema, sin que el método coincida.",
    "activacion_capacidad": "activa una capacidad institucional ya instalada.",
    "investigador_complementario": "aporta un investigador con experiencia afín.",
    "integracion_curricular": "conecta con un componente curricular existente.",
    "coincidencia_superficial": "comparte vocabulario, pero sin respaldo metodológico o de capacidad — la trampa que este sistema evita premiar.",
}

ARM_HELP = {
    "full": "busca de varias formas a la vez y decide el orden con 7 criterios explicables (método, capacidad institucional, evidencia...), no solo por parecido de texto.",
    "cosine": "los mismos resultados encontrados, pero ordenados solo por qué tan parecido es el significado del texto — sin mirar método, capacidad ni evidencia.",
    "dense": "resultados directos de buscar por significado, sin ninguna regla encima — la forma más simple y común de buscar con IA.",
}


class TemplateExplainer(Explainer):
    def explain_connection(self, connection) -> str:
        scored = connection.scored
        relation_label = RELATION_LABELS.get(scored.relation_type, scored.relation_type)
        reasons = ", ".join(
            f"{FEATURE_LABELS.get(name, name)} ({value:.2f})"
            for name, value, _contribution in connection.top_features
        )
        entity_id = connection.entity.entity_id
        base = f"{entity_id} se tipa como {relation_label} (score {scored.score:.2f})"
        if reasons:
            return f"{base} — principalmente por {reasons}."
        return f"{base}."

    def explain_opportunity(self, opportunity) -> str:
        chain = " -> ".join(
            f"{ROLE_LABELS.get(link.role, link.role)} {link.entity_id} "
            f"[{LINK_TYPE_LABELS.get(link.link_type, link.link_type)}]"
            for link in opportunity.links
        )
        type_label = OPPORTUNITY_TYPE_LABELS.get(opportunity.opportunity_type, opportunity.opportunity_type)
        return (
            f"Oportunidad de {type_label} para {opportunity.need_id} "
            f"(prioridad {opportunity.priority}, score del antecedente {opportunity.score:.2f}): "
            f"{chain}."
        )

    def explain_comparison(self, comparison) -> str:
        a_id = comparison.connection_a.entity.entity_id
        b_id = comparison.connection_b.entity.entity_id
        winner_id, loser_id = (a_id, b_id) if comparison.score_delta >= 0 else (b_id, a_id)
        dominant_label = FEATURE_LABELS.get(comparison.dominant_feature, comparison.dominant_feature)
        meaning = FEATURE_HELP.get(comparison.dominant_feature, "")
        base = (
            f"{winner_id} rankea más alto que {loser_id} — la diferencia decisiva es "
            f"{dominant_label} (diferencia de {abs(comparison.score_delta):.2f} puntos de relevancia)"
        )
        if meaning:
            return f"{base}: {meaning}"
        return f"{base}."
