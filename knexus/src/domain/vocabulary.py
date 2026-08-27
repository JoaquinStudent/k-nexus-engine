"""Vocabulario controlado frase→tag para el enriquecimiento (ADR-007).

Los tags que emite este módulo DEBEN ser subconjunto del universo que conoce
`src.domain.method_compat.TRANSFERABILITY` (problem_types como claves, methods
como claves internas). Un test de anti-drift (`test_ingestion.py`) lo exige.

Movido de `adapters/repository/` a `domain/` en Sprint-04 (Regla A2): es puro
(solo importa `method_compat`, sin librerías externas) y tanto la ingesta
(`adapters/repository/enrichment.py`) como una consulta en vivo
(`application/query_builder.py`) necesitan el mismo vocabulario — vivir en
`domain/` es lo único que evita que `application/` dependa de un adapter
concreto para algo que no es volátil ni swappeable.
"""
from src.domain.method_compat import TRANSFERABILITY

METHOD_TAGS = frozenset(
    method for table in TRANSFERABILITY.values() for method in table
)
PROBLEM_TYPE_TAGS = frozenset(TRANSFERABILITY.keys())

# Frase (en minúsculas, tal como aparece en el texto normalizado) -> tag de método.
# `_fold()` en text_matching.py quita acentos de ambos lados al comparar, así
# que una sola forma acentuada por frase basta (no hace falta duplicar sin acentos).
METHOD_PHRASES = {
    "clasificación supervisada": "clasificacion_supervisada",
    "clasificacion supervisada": "clasificacion_supervisada",
    "modelos longitudinales": "modelos_longitudinales",
    "modelo longitudinal": "modelos_longitudinales",
    "regresión": "regresion",
    "regresion": "regresion",
    "analítica educativa": "analitica_educativa",
    "analitica educativa": "analitica_educativa",
    "series temporales": "series_temporales",
    "estadística descriptiva": "estadistica_descriptiva",
    "estadistica descriptiva": "estadistica_descriptiva",
    "encuesta": "encuesta",
    "etnografía": "etnografia",
    "etnografia": "etnografia",
    "optimización lineal": "optimizacion_lineal",
    "optimizacion lineal": "optimizacion_lineal",
    "simulación": "simulacion",
    "simulacion": "simulacion",

    # Ampliación Sprint-03 (Hallazgo 2): metodologías reales medidas sobre
    # projects.csv/theses.csv, mapeadas a fragmento >= 6 apariciones.
    "clasificación de textos": "clasificacion_supervisada",
    "clasificación": "clasificacion_supervisada",
    "análisis estadístico": "estadistica_descriptiva",
    "estudio descriptivo": "estadistica_descriptiva",
    "análisis descriptivo": "estadistica_descriptiva",
    "investigación de operaciones": "optimizacion_lineal",
    "optimización combinatoria": "optimizacion_lineal",
    "optimización": "optimizacion_lineal",
    "sensores": "iot",
    "procesamiento de lenguaje natural": "nlp",

    "estudio de caso": "estudio_de_caso",
    "prototipo funcional": "prototipado",
    "diseño de prototipo": "prototipado",
    "modelamiento estadístico": "modelamiento_estadistico",
    "revisión aplicada": "revision_aplicada",
    "procesamiento de señales": "procesamiento_senales",
    "iot": "iot",
    "detección de anomalías": "deteccion_anomalias",
    "evaluación comparativa": "evaluacion_comparativa",
    "recuperación de información": "recuperacion_informacion",
    "nlp": "nlp",
    "ciberseguridad": "ciberseguridad",
    "modelos dinámicos": "modelos_dinamicos",
    "analítica de riesgo": "analitica_riesgo",
    "modelamiento de comportamiento": "modelamiento_comportamiento",
    "evaluación de impacto": "evaluacion_impacto",
    "modelamiento de riesgo": "modelamiento_riesgo",
    "sistemas recomendadores": "sistemas_recomendadores",
    "modelamiento de usuarios": "modelamiento_usuarios",
    "analítica curricular": "analitica_curricular",
    "representaciones semánticas": "representaciones_semanticas",
    "modelamiento probabilístico": "modelamiento_probabilistico",
    "análisis espacial": "analisis_espacial",
    "aprendizaje automático": "aprendizaje_automatico",
    "ia explicable": "ia_explicable",
    "grafos": "grafos",
    "análisis territorial": "analisis_territorial",
    "analítica interdisciplinaria": "analitica_interdisciplinaria",
    "modelamiento ambiental": "modelamiento_ambiental",
    "analítica socioeconómica": "analitica_socioeconomica",
}

# Frase -> tipo de problema inferido del texto de una necesidad (NEED) o de
# una consulta en texto libre (Sprint-04: mismo mecanismo, `query_builder.py`).
PROBLEM_TYPE_PHRASES = {
    "predicción": "prediccion",
    "prediccion": "prediccion",
    "predictivo": "prediccion",
    "prevención": "prediccion",
    "prevencion": "prediccion",
    "detección temprana": "prediccion",
    "deteccion temprana": "prediccion",
    "anticipar": "prediccion",
    "caracterización": "caracterizacion",
    "caracterizacion": "caracterizacion",
    "diagnóstico": "caracterizacion",
    "diagnostico": "caracterizacion",
    "monitoreo": "caracterizacion",
    "evaluación": "caracterizacion",
    "evaluacion": "caracterizacion",
    "análisis de": "caracterizacion",
    "analisis de": "caracterizacion",
    "optimización": "optimizacion",
    "optimizacion": "optimizacion",
    "uso eficiente": "optimizacion",
    "priorización": "optimizacion",
    "priorizacion": "optimizacion",

    # Ampliación Sprint-03 (Hallazgo 2): 42 títulos/descripciones reales
    # auditados; estas frases cubren necesidades de caracterización que no
    # decían literalmente "análisis de" ni "evaluación". Deliberadamente NO se
    # añaden anclas genéricas ("riesgo", "seguridad", "gestión", "mapa") que
    # dispararían falsos positivos — esas necesidades quedan N/A a propósito.
    "análisis": "caracterizacion",
    "identificación": "caracterizacion",
    "identificacion": "caracterizacion",
    "seguimiento": "caracterizacion",
    "personalización": "caracterizacion",
    "personalizacion": "caracterizacion",
    "detección": "caracterizacion",
    "deteccion": "caracterizacion",
    "fortalecimiento": "caracterizacion",
    "articulación": "caracterizacion",
    "articulacion": "caracterizacion",
}

assert set(METHOD_PHRASES.values()) <= METHOD_TAGS, "vocabulario de método fuera de TRANSFERABILITY"
assert set(PROBLEM_TYPE_PHRASES.values()) <= PROBLEM_TYPE_TAGS, "problem_type fuera de TRANSFERABILITY"

# ---------------------------------------------------------------------------
# ADR-009 (Sprint-03): compat_dominio (peso 0.20, el más alto junto a
# compat_metodo) estaba muerto para TODO NEED — institutional_needs.csv no
# tiene ninguna columna de dominio (disciplinary_area/application_domains/
# research_area), así que QueryEntity.domains era siempre (). Mismo patrón que
# ADR-007: se infiere un SECTOR del texto del NEED (vocabulario controlado) y
# se cruza contra el sector del candidato — ver capability_match.domain_sector,
# que ya usa estos mismos 8 sectores para ADR-008.
# ---------------------------------------------------------------------------
SECTORS = frozenset({
    "salud", "ambiente", "educacion", "finanzas", "industria",
    "territorio", "energia", "software",
})

# Frase del texto de un NEED (o de una consulta libre) -> sector inferido.
NEED_SECTOR_PHRASES = {
    "estudiantil": "educacion",
    "aprendizaje": "educacion",
    "competencias": "educacion",
    "curricular": "educacion",
    "docencia": "educacion",
    "electivas": "educacion",
    "acreditación": "educacion",
    "trabajos de grado": "educacion",
    "semilleros": "educacion",

    "cardiovascular": "salud",
    "epidemiológica": "salud",
    "epidemiologica": "salud",
    "clínica": "salud",
    "clinica": "salud",
    "paciente": "salud",

    "ambiental": "ambiente",
    "ambientales": "ambiente",
    "climático": "ambiente",
    "climatico": "ambiente",
    "calidad del agua": "ambiente",

    "financiero": "finanzas",
    "crediticio": "finanzas",

    "industrial": "industria",
    "logística": "industria",
    "logistica": "industria",

    "urbana": "territorio",
    "urbano": "territorio",
    "territorial": "territorio",
    "territoriales": "territorio",

    "energética": "energia",
    "energetica": "energia",

    "ciberseguridad": "software",
    "digital": "software",
    "tecnológicas": "software",
    "tecnologicas": "software",
    "informática": "software",
    "informatica": "software",
    "interoperabilidad": "software",
}

assert set(NEED_SECTOR_PHRASES.values()) <= SECTORS, "sector fuera del vocabulario de 8 sectores"
