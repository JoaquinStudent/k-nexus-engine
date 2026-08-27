"""Localización de `dataset/` y mapa declarativo de las tablas fuente."""
import pathlib


def dataset_root() -> pathlib.Path:
    """Sube desde este archivo hasta encontrar la carpeta `dataset/` del repo."""
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "dataset"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("No se encontró 'dataset/' subiendo desde " + str(here))


# Tablas de ENTIDAD: archivo -> (entity_type, columna_id, columnas de texto indexable)
ENTITY_TABLES = {
    "01_institution/01_institution_faculties.csv": (
        "FACULTY", "faculty_id", ("faculty_name", "description", "strategic_focus"),
    ),
    "01_institution/01_institution_programs.csv": (
        "PROGRAM", "program_id",
        ("program_name", "description", "disciplinary_area", "graduate_profile", "strategic_topics"),
    ),
    "01_institution/01_institution_research_groups.csv": (
        "RESEARCH_GROUP", "group_id", ("group_name", "description", "mission", "main_area"),
    ),
    "01_institution/01_institution_research_lines.csv": (
        "RESEARCH_LINE", "line_id", ("line_name", "description", "keywords"),
    ),
    "01_institution/01_institution_institutional_capabilities.csv": (
        "CAPABILITY", "capability_id",
        ("capability_name", "description", "available_resources", "application_domains"),
    ),
    "02_people_curriculum/02_people_curriculum_researchers.csv": (
        "RESEARCHER", "researcher_id",
        ("full_name", "academic_background", "profile_summary", "research_interests",
         "methodological_expertise", "application_domains"),
    ),
    "02_people_curriculum/02_people_curriculum_subjects.csv": (
        "SUBJECT", "subject_id",
        ("subject_name", "description", "purpose", "main_topics", "disciplinary_area"),
    ),
    "02_people_curriculum/02_people_curriculum_competencies.csv": (
        "COMPETENCY", "competency_id", ("description",),
    ),
    "02_people_curriculum/02_people_curriculum_learning_outcomes.csv": (
        "LEARNING_OUTCOME", "outcome_id", ("outcome_description",),
    ),
    "03_knowledge_needs/03_knowledge_needs_institutional_needs.csv": (
        "NEED", "need_id", ("title", "description", "context", "expected_impact"),
    ),
    "03_knowledge_needs/03_knowledge_needs_projects.csv": (
        "PROJECT", "project_id",
        ("title", "problem_statement", "abstract", "general_objective", "methodology",
         "expected_results", "application_context", "keywords", "disciplinary_area"),
    ),
    "03_knowledge_needs/03_knowledge_needs_theses.csv": (
        "THESIS", "thesis_id",
        ("title", "abstract", "problem_statement", "general_objective", "methodology",
         "main_results", "conclusions", "keywords", "research_area", "application_context"),
    ),
    "03_knowledge_needs/03_knowledge_needs_publications.csv": (
        "PUBLICATION", "publication_id", ("title", "abstract", "keywords"),
    ),
}

# Tablas de RELACIÓN (aristas del grafo): archivo -> (relation, col_src, col_dst)
RELATION_TABLES = {
    "03_knowledge_needs/03_knowledge_needs_researcher_project.csv": (
        "researcher_project", "researcher_id", "project_id",
    ),
    "03_knowledge_needs/03_knowledge_needs_project_group.csv": (
        "project_group", "project_id", "group_id",
    ),
    "03_knowledge_needs/03_knowledge_needs_thesis_advisor.csv": (
        "thesis_advisor", "thesis_id", "researcher_id",
    ),
    "03_knowledge_needs/03_knowledge_needs_publication_researcher.csv": (
        "publication_researcher", "publication_id", "researcher_id",
    ),
    "03_knowledge_needs/03_knowledge_needs_publication_project.csv": (
        "publication_project", "publication_id", "project_id",
    ),
    "02_people_curriculum/02_people_curriculum_researcher_group.csv": (
        "researcher_group", "researcher_id", "group_id",
    ),
    "02_people_curriculum/02_people_curriculum_researcher_expertise.csv": (
        "researcher_expertise", "researcher_id", "expertise_id",
    ),
}

DOCUMENT_CATALOG = "03_knowledge_needs/03_knowledge_needs_document_catalog.csv"
DOCUMENTS_DIR = "03_knowledge_needs/documents"

# Columnas fuente de las que se derivan keywords/domains/methods por tipo de entidad.
KEYWORDS_COLUMNS = ("keywords",)
DOMAIN_COLUMNS = ("disciplinary_area", "application_domains", "research_area")
METHOD_SOURCE_COLUMNS = ("methodology", "keywords")
PROBLEM_TYPE_SOURCE_COLUMNS = ("description", "context", "title")

# Nº de secciones "## " que trae CADA MD de ese tipo (verificado: consistente
# entre documentos del mismo tipo). Es un total FIJO por tipo, no dinámico —
# el denominador de `densidad_evidencia` no debe inflarse con lo que la propia
# entidad ya trajo (eso saturaría la ratio en 1.0 por construcción). Los tipos
# sin documento MD no suman nada aquí.
MD_SECTION_COUNTS = {
    "NEED": 3,       # institutional_need_*.md: Description, Context, Expected impact
    "PROJECT": 6,    # project_profile_*.md: Problem, Summary, Objective, Methodology, Results, Context
    "THESIS": 6,     # thesis_summary_*.md: Abstract, Problem, Objective, Methodology, Results, Conclusions
}
