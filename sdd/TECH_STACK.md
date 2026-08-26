# TECH_STACK.md — Tecnologías Permitidas

> Regla general: **todo corre en memoria, en CPU, sin dependencia obligatoria de internet.**
> Una tecnología solo se admite si contribuye de forma verificable a resolver el reto.

---

## 1. Stack aprobado

| Capa | Tecnología | Rol | Justificación |
|---|---|---|---|
| Lenguaje | **Python 3.11** | Todo el backend y la lógica. | Estándar del equipo; ecosistema NLP/datos maduro. |
| Datos | **pandas** | Ingesta y manejo del entity store. | ~2.000 entidades caben en memoria; no requiere DB pesada. |
| Embeddings | **sentence-transformers + BAAI/bge-m3** | Texto → vector multilingüe. | El dataset mezcla ES/EN a propósito; da denso + sparse. Corre en CPU. |
| Índice denso | **FAISS (flat)** | Búsqueda por similitud exacta. | Exacto e instantáneo a esta escala; evita vector DB cloud. |
| Índice léxico | **rank-bm25** | Búsqueda por términos/keywords. | Complementa al denso en coincidencias exactas y siglas. |
| Grafo | **NetworkX** | Relaciones explícitas y caminos. | Vive en el proceso Python; Neo4j sería sobrecosto sin beneficio. |
| Fusión / Reranking | **código propio** (RRF + features ponderadas) | Núcleo de dominio. | Debe ser auditable y testeable; no se delega a librería opaca. |
| Backend API | **FastAPI** | Exponer el pipeline. | Ligero, tipado, rápido de levantar. |
| Frontend / UI | **Streamlit** (MVP) → opcional **vis-network** | Exploración de resultados. | Streamlit = una tarde; grafo embebido si sobra tiempo. |
| Reranker fino (opcional) | **BAAI/bge-reranker-v2-m3** | Sube calidad del top-K. | Solo si el tiempo lo permite; el sistema funciona sin él. |
| LLM (externo, declarado) | **API Claude / GPT** | Redacción de explicación y oportunidad. | **Opcional.** Con grounding estricto. Degrada a plantillas si falla. |
| Base de datos (modelado) | **SQL** (`schema.sql`) | Documentar estructura de entidades y relaciones. | Placeholder obligatorio: `ChaparroVillavicencioJoaquin`. |

## 2. Tecnologías vetadas (y por qué)

| Vetado | Motivo |
|---|---|
| GPU / entrenamiento desde cero | Innecesario; el reto no exige entrenar. Añade complejidad y tiempo. |
| Vector DB cloud (Pinecone, Weaviate) | Over-engineering a esta escala; punto de falla en la demo. |
| Neo4j como store principal | Setup costoso sin beneficio con 2.000 nodos. |
| Microservicios | Absurdo para 3 personas / 2 días. |
| Fine-tuning | No requerido; consume tiempo crítico. |
| Cualquier dependencia sin fallback local | Viola la regla de degradación elegante (R5). |

## 3. Gestión de secretos

| Regla | Detalle |
|---|---|
| No hardcodear API keys | Usar variables de entorno (`.env` fuera del repo). |
| Declarar todo componente externo | Modelos, APIs, servicios en el README y en la "Declaración de tecnologías". |
| Separar evidencia de generación | El contenido del LLM nunca se presenta como evidencia institucional. |

## 4. Requisitos de reproducibilidad

| Artefacto | Estado |
|---|---|
| `requirements.txt` | A generar en Sprint de infraestructura. |
| README con instalación/ejecución | A generar. |
| Datos originales sin sobrescribir | Se trabaja sobre copias normalizadas. |
