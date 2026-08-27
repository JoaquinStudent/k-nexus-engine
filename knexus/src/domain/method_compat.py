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
        "modelos_longitudinales": 0.80,
        "regresion": 0.75,
        "analitica_educativa": 0.70,
        "series_temporales": 0.70,
        "estadistica_descriptiva": 0.35,
        "encuesta": 0.30,
        "etnografia": 0.10,
    },
    # Necesidades de caracterizar/diagnosticar el estado actual.
    "caracterizacion": {
        "estadistica_descriptiva": 0.85,
        "analitica_educativa": 0.80,
        "encuesta": 0.70,
        "etnografia": 0.60,
        "clasificacion_supervisada": 0.40,
    },
    # Necesidades de optimizar/asignar recursos o procesos.
    "optimizacion": {
        "optimizacion_lineal": 0.90,
        "simulacion": 0.80,
        "modelos_longitudinales": 0.45,
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
