#### HACKATHON INTERNACIONAL - NIVEL AVANZADO

# KNOWLEDGE NEXUS LATAM

## Documento Tecnico Maestro V1

#### Especificacion de Data V1.0, contrato funcional, implementacion, entregables y orientacion tecnica para

#### participantes

Este documento complementa la Guia Oficial de Participantes. Define como interpretar el ecosistema de datos y que debe poder demostrar una solucion, sin imponer una arquitectura, algoritmo, proveedor o interfaz especifica. Documento Alcance Data oficial Knowledge Nexus LATAM - Data V1.0 Audiencia Participantes Naturaleza Contrato funcional y tecnico Evaluacion tecnica 100 puntos; pitch fuera de la metrica tecnica

Confidencialidad: este documento no contiene Gold Standard, rankings esperados, hard negatives, casos CORE ni respuestas oficiales de evaluacion.

## 1. Modelo tecnico del problema

La universidad ficticia posee informacion institucional abundante, pero distribuida entre estructura academica, personas, curriculo, investigacion, capacidades y necesidades. El reto no consiste en centralizar archivos: consiste en descubrir relaciones relevantes que no siempre estan expresadas mediante llaves directas y convertirlas en oportunidades verificables. Existen dos clases de relaciones: explicitas, disponibles mediante identificadores y tablas de relacion; e inferidas, cuya pertinencia debe ser descubierta por la solucion a partir de contenido, contexto, metodo, dominio, evidencia y otras señales.

INSTITUCION |-- FACULTAD -> PROGRAMA -> ASIGNATURA -> COMPETENCIA / RESULTADO |-- INVESTIGADOR -> EXPERTISE -> PROYECTO / PUBLICACION |-- GRUPO -> LINEA DE INVESTIGACION |-- CAPACIDAD INSTITUCIONAL \`-- NECESIDAD INSTITUCIONAL Nivel a descubrir: NECESIDAD -> ANTECEDENTES -> PROYECTOS/TESIS/PUBLICACIONES -> INVESTIGADORES/GRUPOS -> CAPACIDADES -> CURRICULO -> OPORTUNIDAD Los identificadores son canonicos y sirven para integracion y trazabilidad. Su numeracion no expresa similitud semantica ni cercania institucional.

## 2. Capas de Data V1.0

Capa Contenido Rol 01\_institution Facultades, programas, grupos, lineas, capacidades y Estructura y recursos de la universidad. catalogos institucionales. 02\_people\_curriculum Investigadores, expertise, grupos, asignaturas, Personas, conocimiento y formacion. competencias y resultados de aprendizaje. 03\_knowledge\_needs Necesidades, proyectos, tesis, publicaciones, relaciones y Problemas, antecedentes y productos de documentos complementarios. conocimiento. Los archivos originales deben considerarse fuente de verdad del reto. Los equipos pueden normalizar, indexar, vectorizar o migrar los datos a otras tecnologias, siempre que conserven la procedencia hacia Data V1.0.

## 3. Diccionario logico de entidades

El siguiente diccionario resume el significado funcional de las entidades principales. El esquema exacto de cada archivo debe leerse directamente desde Data V1.0; los campos textuales son evidencia util para descubrimiento semantico y no deben reducirse automaticamente a keywords.

| Entidad | ID canonico | Campos de mayor valor semantico | Relaciones / uso |
| --- | --- | --- | --- |
| Facultad | faculty_id | name, description, strategic_focus | Contenedor academico; no determina por si sola pertinencia. |
| Programa | program_id | description, disciplinary_area, graduate_profile, strategic_topics | Facultad, asignaturas, tesis; posible articulacion con investigacion. |
| Grupo | group_id | description, mission, main_area, interdisciplinary | Lineas, investigadores, proyectos; capacidad colectiva. |
| Linea | line_id | line_name, description, keywords | Especializacion del grupo. |
| Capacidad | capability_id | name, type, description, resources, application_domains, maturity | Soporte humano, tecnologico, metodologico, datos o infraestructura. |
| Investigador | researcher_id | profile_summary, research_interests, methodological_expertise, application_domains | Capacidad individual; tema, metodo y dominio deben distinguirse. |
| Expertise | expertise_id | expertise_name, expertise_type, proficiency, evidence_source | Evidencia estructurada de conocimiento. |
| Asignatura | subject_id | description, purpose, main_topics, disciplinary_area | Punto de articulacion investigacion-curriculo. |

| Entidad | ID canonico | Campos de mayor valor semantico | Relaciones / uso |
| --- | --- | --- | --- |
| Competencia | competency_id | competency_type, description | Capacidad formativa asociada a programa/asignatura. |
| Resultado aprendizaje | outcome_id | outcome_description, cognitive_level, evidence_type | Resultado formativo susceptible de articulacion. |
| Necesidad | need_id | title, description, context, expected_impact, priority | Problema institucional; no prescribe la solucion. |
| Proyecto | project_id | problem_statement, abstract, objective, methodology, expected_results, context | Antecedente, metodo, experiencia o continuidad. |
| Tesis | thesis_id | abstract, problem, objective, methodology, results, conclusions, context | Antecedente, evidencia, continuidad o articulacion. |
| Publicacion | publication_id | title, abstract, keywords, related_project | Evidencia de produccion y capacidad investigativa. |

Regla sobre nulos: un campo vacio significa que la informacion no esta disponible en esa fuente; no demuestra necesariamente que el atributo no exista en el mundo institucional. La heterogeneidad es intencional: pueden coexistir sinonimos, terminologia en español e ingles, diferentes niveles de detalle y señales distribuidas entre archivos. La robustez frente a esa diversidad forma parte del reto.

## 4. Relaciones explicitas e inferidas

Origen Destino Naturaleza orientativa Programa Facultad Explicita Asignatura Programa Explicita Linea Grupo Explicita Investigador Grupo / Proyecto / Publicacion Explicita mediante tablas de relacion cuando aplique Necesidad Proyecto / Tesis / Investigador / Grupo / Capacidad A descubrir Proyecto Tesis / Asignatura / Proyecto A descubrir Investigador Investigador Complementariedad a descubrir Grupo Grupo Colaboracion a descubrir Investigacion Curriculo Articulacion a descubrir Conjunto de entidades Oportunidad A construir No se impone una ontologia cerrada. Una relacion es valida cuando su significado es comprensible, su pertinencia es defendible y su evidencia puede verificarse.

## 5. Contrato conceptual de salida

Independientemente de la tecnologia, una conexion plenamente demostrable debe permitir identificar los siguientes componentes. Componente Obligatorio Pregunta Origen Si ¿Desde que entidad nace la relacion? Destino Si ¿Que entidad fue relacionada? Tipo de relacion Si ¿Que significa la conexion? Relevancia / prioridad Si ¿Que tan importante es y por que aparece en esa posicion? Explicacion Si ¿Por que existe la conexion? Evidencia Si ¿Que contenido la sustenta? Procedencia Si ¿De que archivo/registro/campo o documento provino? Oportunidad Cuando aplique ¿Que puede hacer la universidad con la conexion? "source": {"id": "NEED-XXX", "type": "institutional\_need"}, "target": {"id": "PRJ-XXX", "type": "project"}, "relation": "relevant\_antecedent", "relevance": "...", "explanation": "...", "evidence": [...], "sources": [...] El JSON anterior es conceptual. No se exige API ni formato JSON. Una interfaz grafica, grafo, dashboard, CLI, notebook o asistente conversacional puede cumplir el contrato si hace visible la misma informacion.

## 6. Relevancia, explicacion y evidencia

Similarity no equivale a relevance. Dos registros pueden compartir palabras o metodos y aun asi aportar poco al problema. La solucion debe poder justificar por que un resultado es mas pertinente que otro. La escala de relevancia es libre: score 0-1, porcentaje, High/Medium/Low, estrellas o posicion de ranking son validos si el equipo explica su significado. Lo obligatorio es poder responder: ¿por que A aparece antes que B?

Una puntuacion de similitud o confianza del modelo no constituye por si sola evidencia. La evidencia debe remitir a contenido institucional verificable: un campo, fragmento, relacion o documento. En sistemas generativos debe distinguirse claramente entre evidencia recuperada y sintesis generada. Resultado -> Explicacion -> Evidencia -> Fuente Ejemplo de procedencia: Data V1.0 / projects.csv / PRJ-081 / methodology

## 7. Contrato conceptual de oportunidad

Knowledge Nexus busca pasar de relaciones aisladas a posibilidades accionables. Una oportunidad puede combinar varias entidades y debe explicar su valor institucional. "opportunity": "...", "type": "COLLABORATION | RESEARCH\_CONTINUITY | CURRICULAR\_INTEGRATION | ...", "related\_entities": ["NEED-...", "INV-...", "PRJ-...", "CAP-..."], "reason": "...", "priority": "...", "evidence": [...] Categorias orientativas, no cerradas: nueva investigacion, colaboracion, continuidad, integracion curricular, activacion de capacidades, transferencia de conocimiento y oportunidad de trabajo de grado.

## 8. Ejemplos publicos didacticos

Los siguientes ejemplos son ficticios y no corresponden a casos oficiales, respuestas esperadas ni entidades del Gold Standard.

### Ejemplo A - Conexion

Consulta: la universidad desea identificar antecedentes y capacidades para mejorar la eficiencia en el uso de recursos de sus instalaciones. Origen: NEED-EXAMPLE-01 Destino: PRJ-EXAMPLE-12 Relacion: antecedente metodologico Relevancia: alta Explicacion: el proyecto usa adquisicion de variables operativas y analisis temporal, metodologia transferible al problema. Evidencia: project.methodology Fuente: projects.csv / PRJ-EXAMPLE-12

### Ejemplo B - Ranking

Un ranking de calidad puede colocar primero un resultado que combine metodo aplicable, dominio compatible, evidencia y capacidad disponible; despues uno tematicamente similar pero menos accionable; y relegar coincidencias textuales con poca utilidad. El equipo debe poder explicar esa diferencia.

### Ejemplo C - Oportunidad

NECESIDAD + PROYECTO con antecedente + INVESTIGADOR con expertise + CAPACIDAD disponible + ASIGNATURA relacionada -> OPORTUNIDAD interdisciplinaria -> evidencia + prioridad + trazabilidad Una respuesta como PRJ-081 - similarity 0.92 es insuficiente si no define relacion, explicacion, evidencia y fuente.

## 9. Requisitos de implementacion

Requisito Regla Prototipo Debe existir un flujo funcional end-to-end sobre Data V1.0. Datos originales Conservar sin sobrescribir; se permiten capas processed, embeddings, indices, grafos o caches. Arquitectura Libre; el diagrama principal debe representar lo realmente implementado. Interfaz Web, desktop, notebook, CLI, API, grafo, dashboard o conversacional. Cloud / Internet Permitidos. El equipo asume disponibilidad y contingencia razonable. Modelos preentrenados Permitidos; no se exige entrenamiento desde cero. Fine-tuning Permitido y debe documentarse si se usa. APIs / servicios externos Permitidos y declarados; no deben confundirse con evidencia institucional. Datasets externos Complementarios y declarados; no pueden inventar hechos sobre entidades de Data V1.0. Secretos No hardcodear API keys; usar variables de entorno u otra gestion segura. Preprocesamiento Permitido: normalizacion, NER, traduccion, embeddings, clustering, indexacion, etc. Indices precalculados Permitidos si el equipo explica como fueron construidos. Resultados precargados No sustituyen procesamiento real; la solucion debe responder a entradas nuevas. Reproducibilidad README suficiente para comprender instalacion, ejecucion y decisiones principales.

## 10. Entregables tecnicos obligatorios

Entregable Contenido minimo 1. Prototipo funcional Solucion ejecutable y demostrable. 2. Codigo fuente Repositorio o paquete organizado. 3. README tecnico Solucion, stack, instalacion, ejecucion, datos, descubrimiento, ranking, evidencia, oportunidades, metricas, limitaciones y externos. 4. Diagrama de arquitectura Fuentes -> procesamiento -> representacion -> recuperacion/razonamiento -> ranking -> explicacion -> interfaz. 5. Evidencia de desempeño Metricas o pruebas coherentes con el enfoque y metodologia de calculo. 6. Casos demostrables Conexiones y oportunidades con evidencia y trazabilidad. 7. Declaracion tecnologica Modelos, APIs, servicios, cloud, datasets complementarios y herramientas generativas. No se exige informe academico extenso. El valor principal debe estar en el prototipo, la calidad de las conexiones y la evidencia.

## 11. Criterio minimo de funcionamiento

Una solucion se considera funcional cuando puede procesar Data V1.0 y, ante una consulta o entidad de entrada, generar dinamicamente una o mas conexiones identificables con algun mecanismo de priorizacion y evidencia verificable. Para considerarse integral, ademas debe generar o identificar una oportunidad y permitir rastrear el resultado hasta sus fuentes. Fallas tecnicas graves: no utilizar Data V1.0; resultados completamente precargados; prototipo no ejecutable; entidades inventadas presentadas como institucionales; imposibilidad total de mostrar evidencia; dependencias esenciales no disponibles durante la evaluacion.

## 12. Evaluacion tecnica y metricas

Los equipos pueden reportar metricas apropiadas para su enfoque: precision, recall, F1, Precision@K, Recall@K, NDCG, MRR, cobertura, latencia, confianza u otras justificadas. No es obligatorio reportarlas todas. Toda metrica debe indicar contra que se evaluo y como se calculo. La organizacion utilizara adicionalmente mecanismos internos de validacion. Sus casos, relaciones de referencia y rankings no son publicos. Las metricas internas sirven como evidencia para la rubrica; no existe una conversion automatica del tipo NDCG = nota final. Concepto Interpretacion publica Precision@K Proporcion de resultados relevantes dentro de los primeros K. Recall@K Cobertura de resultados relevantes dentro de los primeros K. NDCG@K Calidad del orden cuando existen distintos grados de relevancia. MRR Que tan pronto aparece un primer resultado relevante. Cobertura de evidencia Proporcion de resultados sustentados. Trazabilidad Proporcion de resultados que pueden regresar a su fuente. Latencia Tiempo de respuesta; secundaria frente a la calidad salvo que impida el uso. Los hallazgos nuevos no son automaticamente incorrectos. Una conexion emergente puede ser valida si las entidades existen, la evidencia es verificable, la interpretacion es coherente y existe utilidad institucional potencial.

## 13. Metrica tecnica oficial

Criterio Puntos Arquitectura y calidad tecnica 20 Funcionamiento del prototipo 20 Innovacion 15 Impacto y escalabilidad 10 Calidad y pertinencia de conexiones 8 Representacion e integracion del conocimiento 6 Generacion de oportunidades y valor academico 7 Priorizacion y calidad de recomendaciones 5 Explicabilidad y trazabilidad 4 Validacion tecnica durante la revision 5 TOTAL 100 El pitch final no forma parte de esta metrica tecnica. No suma, resta ni modifica los 100 puntos tecnicos. Durante las revisiones, los evaluadores pueden solicitar una entrada nueva y auditar un resultado para comprobar funcionamiento, pertinencia y trazabilidad.

## 14. Preguntas frecuentes

### ¿Podemos usar ChatGPT, OpenAI u otros modelos de IA?

Si. Tambien otros LLM, embeddings, rerankers o servicios. Deben declararlos y separar claramente evidencia institucional de contenido generado.

### ¿Podemos agregar fuentes externas?

Si, como complemento declarado. Las afirmaciones sobre entidades de la universidad ficticia deben seguir sustentadas por Data V1.0.

### ¿Podemos modificar los CSV?

No sobrescriban los originales. Si pueden crear copias normalizadas, tablas derivadas, indices, embeddings, grafos o cualquier representacion procesada.

### ¿Debemos usar todos los archivos?

No necesariamente todos en cada consulta. Pero la solucion debe demostrar integracion real de varias fuentes y aprovechar las que sean pertinentes al problema.

### ¿Hay que entrenar un modelo?

No. Se permiten modelos preentrenados, reglas, recuperacion de informacion, grafos, ML, NLP o enfoques hibridos.

### ¿Es obligatorio construir un grafo?

No. Un grafo es una alternativa, no un requisito.

### ¿Es obligatorio tener frontend?

No. La interaccion puede ser web, API, CLI, notebook, dashboard, grafo o conversacional, siempre que sea demostrable.

### ¿Debemos descubrir todas las conexiones posibles?

No. Se valora especialmente la calidad, priorizacion, cobertura razonable y utilidad; devolver mas resultados no implica mejor solucion.

### ¿Como sabemos si una recomendacion es correcta?

Debe poder defenderse con evidencia verificable de Data V1.0, una explicacion coherente y una relacion util para el contexto.

### ¿Que pasa si encontramos una conexion que no estaba prevista?

Puede ser un descubrimiento emergente valido si existe evidencia, coherencia y utilidad. El conjunto interno de referencia no limita la innovacion.

### ¿Podemos usar scores propios?

Si. Deben explicar su escala, significado y por que un resultado se prioriza sobre otro.

### ¿Que revisara el evaluador?

Funcionamiento real, arquitectura, integracion, calidad de conexiones, ranking, oportunidades, explicacion, evidencia, trazabilidad y respuesta ante una solicitud nueva.

### ¿El pitch entra en la nota tecnica?

No. La metrica tecnica oficial suma 100 puntos y el pitch esta fuera de ella.

### ¿Necesitamos estar offline?

No. Pueden depender de cloud o Internet, pero el equipo es responsable de que la solucion pueda demostrarse.

### ¿Que ocurre si una API externa falla?

La dependencia es responsabilidad del equipo. Se recomienda una contingencia razonable sin convertirla en resultados precargados.

## 15. Checklist oficial antes de la evaluacion

n Nuestra solucion procesa realmente Data V1.0. n Podemos demostrar una conexion no trivial entre fuentes diferentes. n Podemos explicar por que una conexion es relevante y por que otra puede no serlo. n Existe ranking, prioridad o valoracion interpretable. n Podemos ir desde una recomendacion hasta el archivo/registro/campo o documento que la sustenta. n Las oportunidades se derivan de evidencia institucional. n Podemos responder a una consulta nueva sin depender de respuestas precargadas. n El diagrama de arquitectura corresponde a lo implementado. n El README permite comprender y ejecutar la solucion. n Declaramos modelos, APIs, servicios cloud, datasets complementarios y herramientas generativas. n Las credenciales no estan hardcodeadas. n Podemos explicar nuestras metricas, limitaciones e incertidumbre. n Podemos distinguir contenido institucional, externo y generado. n Tenemos una contingencia razonable para dependencias criticas.

## 16. Reglas tecnicas de interpretacion

(cid:127) Misma facultad no significa mayor pertinencia. (cid:127) Mas keywords iguales no significa mejor conexion. (cid:127) Mismo metodo no significa mismo problema. (cid:127) Misma tematica no significa misma oportunidad. (cid:127) Score alto no significa verdad. (cid:127) Contenido generado no significa evidencia. (cid:127) Mas resultados no significa mejor solucion. (cid:127) Una arquitectura sofisticada no sustituye un resultado verificable.

## 17. Principio de cierre

La solucion debe poder responder siete preguntas: ¿que conecto?, ¿como se relaciona?, ¿que tan relevante es?, ¿por que?, ¿con que evidencia?, ¿de donde proviene? y ¿para que sirve? Knowledge Nexus LATAM busca transformar informacion dispersa -> conocimiento estructurado -> conexiones relevantes -> oportunidades priorizadas -> decisiones mejor informadas .

#### Fin del Documento Tecnico Maestro V1
