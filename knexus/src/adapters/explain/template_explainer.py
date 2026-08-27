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
