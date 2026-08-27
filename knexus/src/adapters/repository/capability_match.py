"""ADR-008: regla explícita de `has_capability_support`.

No existe tabla que enlace `institutional_capability` con proyectos/necesidades.
Primer diseño (por `capability_type`) se descartó tras medirlo: `capability_type`
rota entre las 7 categorías de forma prácticamente decorrelacionada del tema
real de la capacidad (cada uno de los 12 temas de `capability_name` aparece con
los 7 `capability_type` casi por igual) — usarlo daba `True` a 313/320 proyectos
(97.8%), el error espejo del `False` constante que había antes de Sprint-03.

La señal real y auditable es el **tema** de `capability_name` (12 valores fijos:
"Internet de las Cosas", "Analítica y Ciencia de Datos", ... cada uno cruzado
1:1 con los 8 sectores → 96 filas). Es el mismo patrón que ADR-007
(`method_compat.TRANSFERABILITY`): una tabla explícita método→tema.

La regla cruza TRES ejes:
  1. Sector: dominio fino del candidato → sector institucional.
  2. Tema: el método real del candidato → tema(s) de capacidad compatibles.
  3. Madurez: `maturity_level >= 4` (readiness real, no capacidad incipiente).

Con esto, sector+tema aíslan como máximo una fila de `institutional_capabilities`
(cada combinación tema×sector es única), y la madurez decide sobre ESA fila —
señal genuinamente binaria, no casi-constante. Ver
`test_feature_discrimination.py` para la verificación.
"""
import unicodedata

from src.adapters.repository.vocabulary import SECTORS

MIN_MATURITY = 4

# Dominio fino (disciplinary_area / research_area) -> sector institucional.
SECTOR_BY_DOMAIN = {
    "psicologia": "educacion",
    "ciencias de la educacion": "educacion",
    "licenciatura en tecnologia e informatica": "software",
    "fisica": "industria",
    "ciencia de datos": "software",
    "matematicas aplicadas": "software",
    "enfermeria": "salud",
    "seguridad y salud en el trabajo": "salud",
    "medicina": "salud",
    "civil": "territorio",
    "gestion ambiental": "ambiente",
    "ambiental": "ambiente",
    "economia": "finanzas",
    "administracion de empresas": "industria",
    "financiera": "finanzas",
    "de sistemas": "software",
    "electronica": "energia",
    "industrial": "industria",
}

# Tag de método -> tema(s) de `capability_name` que lo soportarían.
_ANALITICA = ("Analítica y Ciencia de Datos",)
METHOD_TO_CAPABILITY_TOPICS = {
    **{tag: _ANALITICA for tag in (
        "clasificacion_supervisada", "aprendizaje_automatico", "deteccion_anomalias",
        "modelamiento_estadistico", "regresion", "modelamiento_probabilistico",
        "ia_explicable", "sistemas_recomendadores", "recuperacion_informacion", "nlp",
        "representaciones_semanticas", "grafos", "modelamiento_comportamiento",
        "modelamiento_usuarios",
    )},
    "procesamiento_senales": ("Internet de las Cosas", "Bioinstrumentación"),
    "iot": ("Internet de las Cosas", "Bioinstrumentación"),
    "ciberseguridad": ("Seguridad Digital",),
    "simulacion": ("Simulación Clínica",),
    "optimizacion_lineal": ("Desarrollo Regional",),
    "prototipado": ("Infraestructura Inteligente", "Instrumentación Física"),
    **{tag: ("Cómputo de Alto Rendimiento",) for tag in (
        "modelos_longitudinales", "modelos_dinamicos", "series_temporales",
        "modelamiento_riesgo", "analitica_riesgo",
    )},
    **{tag: ("Analítica Académica",) for tag in (
        "estadistica_descriptiva", "analitica_educativa", "analitica_curricular",
        "evaluacion_impacto", "evaluacion_comparativa",
    )},
    **{tag: ("Innovación Educativa",) for tag in (
        "etnografia", "encuesta", "estudio_de_caso", "revision_aplicada",
    )},
    **{tag: ("Desarrollo Regional",) for tag in (
        "modelamiento_ambiental", "analisis_espacial", "analisis_territorial",
        "analitica_socioeconomica", "analitica_interdisciplinaria",
    )},
}


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def domain_sector(domain: str) -> str:
    folded = _fold(domain)
    if folded in SECTORS:
        return folded
    return SECTOR_BY_DOMAIN.get(folded, "")


def _capability_topic(capability_name: str) -> str:
    return capability_name.split("—")[0].strip()


def find_matching_capability(domains: tuple, methods: tuple, capabilities: tuple):
    """La PRIMERA `StoredEntity` de tipo CAPABILITY que satisface sector + tema
    + madurez, o `None`. `has_capability_support` es un caso particular de esto
    (Sprint-05: la cadena de oportunidad necesita saber CUÁL capacidad, no sólo
    si existe alguna — mismo criterio, sin duplicar la regla)."""
    sectors = {domain_sector(d) for d in domains} - {""}
    required_topics = set()
    for method in methods:
        required_topics |= set(METHOD_TO_CAPABILITY_TOPICS.get(method, ()))
    if not sectors or not required_topics:
        return None

    for cap in capabilities:
        raw = cap.raw
        if raw.get("status") != "ACTIVE":
            continue
        if _capability_topic(raw.get("capability_name", "")) not in required_topics:
            continue
        try:
            maturity = int(raw.get("maturity_level", 0))
        except ValueError:
            continue
        if maturity < MIN_MATURITY:
            continue
        cap_sectors = {_fold(s) for s in raw.get("application_domains", "").split(";")}
        if sectors & cap_sectors:
            return cap
    return None


def has_capability_support(domains: tuple, methods: tuple, capabilities: tuple) -> bool:
    return find_matching_capability(domains, methods, capabilities) is not None
