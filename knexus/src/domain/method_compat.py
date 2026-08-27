"""Transferabilidad problema→método. PURO — sin imports externos (Regla A1).

Cuando la consulta no prescribe un método (los NEED lo declaran a propósito:
"does not prescribe an algorithm, model, or technology"), no hay conjunto de
métodos que solapar. En su lugar se infiere el *tipo de problema* del texto de la
necesidad (en ingesta) y se puntúa si el método REAL y documentado del candidato
es transferible a ese problema. Al NEED nunca se le asigna un método: la señal es
transferabilidad inferida, y esta tabla la hace auditable de un vistazo.

Rango de cada score: 0..1 (mismo rango que el Jaccard simétrico al que sustituye).
"""

TRANSFERABILITY = {
    # Necesidades de predecir/prevenir (p.ej. deserción): favorecen métodos
    # predictivos; una encuesta describe pero no predice → transferabilidad baja.
    "prediccion": {
        "clasificacion_supervisada": 0.90,
        "aprendizaje_automatico": 0.85,
        "deteccion_anomalias": 0.85,
        "modelos_longitudinales": 0.80,
        "analitica_riesgo": 0.80,
        "modelamiento_riesgo": 0.80,
        "modelamiento_estadistico": 0.80,
        "regresion": 0.75,
        "modelos_dinamicos": 0.75,
        "modelamiento_probabilistico": 0.75,
        "analitica_educativa": 0.70,
        "series_temporales": 0.70,
        "procesamiento_senales": 0.65,
        "ciberseguridad": 0.60,
        "modelamiento_comportamiento": 0.55,
        "modelamiento_ambiental": 0.55,
        "ia_explicable": 0.55,
        "iot": 0.55,
        "nlp": 0.50,
        "estadistica_descriptiva": 0.35,
        "encuesta": 0.30,
        "revision_aplicada": 0.25,
        "estudio_de_caso": 0.20,
        "etnografia": 0.10,
    },
    # Necesidades de caracterizar/diagnosticar el estado actual.
    "caracterizacion": {
        "estadistica_descriptiva": 0.85,
        "analitica_educativa": 0.80,
        "estudio_de_caso": 0.75,
        "evaluacion_comparativa": 0.75,
        "evaluacion_impacto": 0.70,
        "analitica_curricular": 0.70,
        "encuesta": 0.70,
        "iot": 0.70,
        "modelamiento_usuarios": 0.65,
        "analisis_espacial": 0.65,
        "analisis_territorial": 0.65,
        "analitica_socioeconomica": 0.65,
        "modelamiento_comportamiento": 0.65,
        "modelamiento_ambiental": 0.65,
        "revision_aplicada": 0.65,
        "etnografia": 0.60,
        "recuperacion_informacion": 0.60,
        "ia_explicable": 0.60,
        "procesamiento_senales": 0.55,
        "ciberseguridad": 0.55,
        "nlp": 0.55,
        "sistemas_recomendadores": 0.55,
        "representaciones_semanticas": 0.50,
        "grafos": 0.55,
        "analitica_interdisciplinaria": 0.55,
        "modelamiento_estadistico": 0.50,
        "modelamiento_riesgo": 0.50,
        "modelamiento_probabilistico": 0.45,
        "analitica_riesgo": 0.50,
        "deteccion_anomalias": 0.50,
        "clasificacion_supervisada": 0.40,
        "aprendizaje_automatico": 0.45,
        "prototipado": 0.30,
    },
    # Necesidades de optimizar/asignar recursos o procesos.
    "optimizacion": {
        "optimizacion_lineal": 0.90,
        "prototipado": 0.80,
        "simulacion": 0.80,
        "evaluacion_comparativa": 0.35,
        "sistemas_recomendadores": 0.45,
        "modelos_longitudinales": 0.45,
        "modelos_dinamicos": 0.40,
        "analitica_educativa": 0.40,
    },
}


def transferability(problem_types: tuple, candidate_methods: tuple) -> float:
    """Mejor transferabilidad entre los tipos de problema de la consulta y los
    métodos del candidato. 0.0 si no hay ningún par en la tabla."""
    best = 0.0
    for pt in problem_types:
        table = TRANSFERABILITY.get(pt)
        if not table:
            continue
        for method in candidate_methods:
            best = max(best, table.get(method, 0.0))
    return best
