# Declaración de tecnologías y componentes externos — KNexus Engine

> Entregable técnico oficial (`GUIA_OFICIAL_PARTICIPANTES...md §8`, `DOCUMENTO_TECNICO.md §10`).
> Todo lo listado aquí corre en CPU, sin dependencia obligatoria de red (Regla R5 de `sdd/AGENTS.md`).

---

## 1. Modelo preentrenado

| Componente | Detalle |
|---|---|
| **`paraphrase-multilingual-MiniLM-L12-v2`** | Modelo de embeddings de [sentence-transformers](https://www.sbert.net/) (Hugging Face Hub). Genera los vectores del índice denso — es la única pieza de "IA" que participa en el *ranking* de las conexiones. |
| Rol | Texto → vector de 384 dimensiones. Multilingüe: el dataset mezcla ES/EN a propósito (verificado: coseno 0.82 entre "deserción estudiantil" y "student attrition") y este modelo lo resuelve sin traducción intermedia. |
| Tamaño / descarga | ~470 MB, se descarga una sola vez desde Hugging Face Hub en el primer arranque sin `--fast` (`~/.cache/huggingface`). Corridas siguientes son 100% offline. |
| Por qué no `bge-m3` | `TECH_STACK.md` documentaba `bge-m3` (~5 GB con `torch`) como opción inicial; se cambió a este modelo (~470 MB) para iterar rápido en el hackathon sin perder cobertura ES↔EN — es un swap de una línea detrás del puerto `EmbeddingProvider` (`src/ports/embedding_provider.py`) si hiciera falta más adelante. |
| Fine-tuning | Ninguno. Se usa el checkpoint público tal cual. |

## 2. Librerías / frameworks

| Librería | Rol | Fallback si falta (Regla A4) |
|---|---|---|
| `faiss-cpu` | Índice denso exacto (`IndexFlatIP` = coseno sobre vectores normalizados). | Búsqueda exacta con NumPy puro (`src/adapters/retrieval/dense_index.py`) — mismo resultado matemático. |
| `rank-bm25` | Índice léxico (BM25) para coincidencias por término/sigla. | Ninguno necesario: es una librería pura de Python, sin dependencia nativa. |
| `networkx` | Grafo de relaciones explícitas (7 tablas de relación del dataset → 3.536 aristas) y `spring_layout` para el mini-grafo SVG. | Ninguno; corre en memoria sin dependencia externa. |
| `pandas` | Ingesta de las 22 tablas CSV con provenance campo-por-campo. | — |
| `FastAPI` + `Jinja2` + `uvicorn` | Backend + interfaz web en un solo proceso (`/api/*` JSON y páginas HTML desde los mismos DTO). | — |
| `pytest` | 174 tests (166 rápidos + 8 con el modelo real, marcados `@slow`). | — |

Todas fijadas con versión exacta en `knexus/requirements.txt` — verificado con una instalación limpia
(`pip install -r requirements.txt` + `pytest -m "not slow"` → 166/166 verdes).

## 3. Tipografía vendorizada

**Montserrat** (`knexus/src/interface/static/fonts/montserrat-variable.woff2`, un único `.woff2`
variable, pesos 100-900) servida por el propio backend. Cero CDN de Google Fonts ni de terceros — la
interfaz corre sin red incluso para su estilo visual (Regla R5).

## 4. API externa (opcional, declarada)

| Componente | Detalle |
|---|---|
| **API de OpenRouter** (`anthropic/claude-3.5-haiku` por defecto) | Redacción en lenguaje natural de la explicación de una conexión, una oportunidad, o el comparador A-vs-B de `/audit` (`src/adapters/explain/llm_explainer.py`, método `explain_comparison`). Vía el endpoint REST de OpenRouter (compatible con OpenAI chat completions), llamado con `httpx` — sin SDK adicional. |
| Cómo se activa | Sólo si la variable de entorno `OPENROUTER_API_KEY` está presente (`src/adapters/explain/factory.py:build_explainer()`). Nunca hardcodeada. |
| Degradación | Si falta la key, o si la llamada falla por cualquier motivo (red, rate limit, error del proveedor), el sistema cae automáticamente a `TemplateExplainer` — determinista, sin red, con el mismo grounding estricto. **El sistema completo, incluida la generación de oportunidades, funciona sin esta API.** |
| Estado de verificación | **No probado contra la API real en este entorno** (sin key disponible durante el desarrollo) — se declara explícitamente como limitación conocida (ver `README.md`). El adapter tiene tests unitarios con un cliente falso; lo no verificado es la llamada de red real. |
| Grounding | El prompt enviado al LLM incluye **sólo** los datos ya verificados del `RankedConnection`/`Opportunity` (entity_id, tipo de relación, score, features) y pide explícitamente no inventar hechos ni cifras. Verificado por test que ningún identificador/cifra de la salida de `TemplateExplainer` puede faltar en su input — el mismo contrato de grounding aplica al prompt del LLM. |

## 5. Datasets

Sólo se usa **Data V1.0** (`dataset/`), provisto por la organización — 22 tablas CSV + 60 documentos
Markdown, 2.512 entidades, 3.536 aristas de relación explícita. **Ningún dataset externo** se mezcla
con estos datos ni se usa para inventar hechos sobre entidades del reto.

## 6. Cómo se distingue evidencia institucional de contenido generado (guía §6)

- Cada resultado (`RankedConnection`) carga su `Provenance` — `source_file`/`field_name`/`entity_id` —
  hasta la interfaz (Regla A3, `tests/interface/test_trazabilidad_ui.py`); la UI lo muestra literal en
  `/connection/{id}`.
- Cada eslabón de una cadena de oportunidad (`ChainLink`) declara `link_type` ∈
  `{retrieved, edge, inferred}` (ADR-012) — nunca se presentan un dato recuperado, una arista real de
  una tabla de relación y una inferencia como si fueran la misma clase de evidencia.
- La interfaz marca explícitamente el texto con procedencia institucional (`tag-evidence`, lavanda) vs.
  el texto redactado por el `Explainer` (`tag-generated`, gris — `src/interface/static/knexus.css`),
  incluida la explicación del comparador en `/audit`.
- Cuando el sistema corre sin LLM (por defecto, o por degradación de Regla A4), un banner ámbar visible
  en toda la interfaz lo declara: *"AI explainer is offline — showing template explanations instead"*
  (`_banner.html`, `service.explainer_degraded`).

## 7. Gestión de secretos

Ninguna API key hardcodeada en el repositorio. `OPENROUTER_API_KEY` se lee exclusivamente de variable de
entorno (`factory.py:14`); su ausencia es el camino feliz por defecto, no un caso de error.

## 8. Tecnologías explícitamente NO usadas

Vector DB cloud, Neo4j, microservicios, fine-tuning, entrenamiento con GPU — vetadas por sobre-ingeniería
frente a un dataset de ~2.500 entidades que cabe en memoria (`sdd/TECH_STACK.md §2`).
