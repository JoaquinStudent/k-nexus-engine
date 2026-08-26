-- ============================================================
-- KNexus Engine — schema.sql
-- Modelado lógico de Data V1.0 (Knowledge Nexus LATAM)
-- Estilo: normalizado, orientado a trazabilidad (provenance).
--
-- CONVENCIÓN DE PRUEBA (innegociable):
--   Todo autor / mock / identificador de prueba usa el placeholder:
--   ChaparroVillavicencioJoaquin
-- ============================================================

-- ------------------------------------------------------------
-- METADATO DE PROVENANCE
-- Cada texto indexable arrastra su origen: archivo / registro / campo.
-- Es la columna vertebral de la trazabilidad del reto.
-- ------------------------------------------------------------
CREATE TABLE provenance (
    provenance_id   VARCHAR(64) PRIMARY KEY,
    source_file     VARCHAR(255) NOT NULL,   -- ej. project_profile_004.md
    entity_type     VARCHAR(64)  NOT NULL,   -- need | project | thesis | ...
    entity_id       VARCHAR(64)  NOT NULL,   -- ej. PRJ-004
    field_name      VARCHAR(64)  NOT NULL,   -- ej. methodology
    created_by      VARCHAR(64)  DEFAULT 'ChaparroVillavicencioJoaquin'
);

-- ============================================================
-- BLOQUE A — 01_institution
-- ============================================================
CREATE TABLE faculty (
    faculty_id      VARCHAR(64) PRIMARY KEY,
    faculty_name    VARCHAR(255),
    description     TEXT,
    strategic_focus TEXT,
    active          BOOLEAN
);

CREATE TABLE program (
    program_id        VARCHAR(64) PRIMARY KEY,
    faculty_id        VARCHAR(64) REFERENCES faculty(faculty_id),
    program_name      VARCHAR(255),
    academic_level    VARCHAR(64),
    description       TEXT,
    disciplinary_area VARCHAR(255),
    graduate_profile  TEXT,
    strategic_topics  TEXT,
    active            BOOLEAN
);

CREATE TABLE research_group (
    group_id          VARCHAR(64) PRIMARY KEY,
    group_name        VARCHAR(255),
    faculty_id        VARCHAR(64) REFERENCES faculty(faculty_id),
    description       TEXT,
    mission           TEXT,
    main_area         VARCHAR(255),
    interdisciplinary BOOLEAN,
    creation_year     INTEGER,
    status            VARCHAR(64)
);

CREATE TABLE research_line (
    line_id     VARCHAR(64) PRIMARY KEY,
    group_id    VARCHAR(64) REFERENCES research_group(group_id),
    line_name   VARCHAR(255),
    description TEXT,
    keywords    TEXT,
    active      BOOLEAN
);

CREATE TABLE institutional_capability (
    capability_id       VARCHAR(64) PRIMARY KEY,
    capability_name     VARCHAR(255),
    capability_type     VARCHAR(64),
    description         TEXT,
    responsible_unit    VARCHAR(255),
    available_resources TEXT,
    application_domains  TEXT,
    maturity_level      INTEGER,
    status              VARCHAR(64)
);

-- ============================================================
-- BLOQUE B — 02_people_curriculum
-- ============================================================
CREATE TABLE researcher (
    researcher_id           VARCHAR(64) PRIMARY KEY,
    full_name               VARCHAR(255),
    faculty_id              VARCHAR(64) REFERENCES faculty(faculty_id),
    primary_program_id      VARCHAR(64) REFERENCES program(program_id),
    academic_background     TEXT,
    profile_summary         TEXT,
    research_interests      TEXT,
    methodological_expertise TEXT,
    application_domains     TEXT,
    years_experience        INTEGER,
    active                  BOOLEAN
);

CREATE TABLE subject (
    subject_id        VARCHAR(64) PRIMARY KEY,
    program_id        VARCHAR(64) REFERENCES program(program_id),
    subject_name      VARCHAR(255),
    semester          INTEGER,
    credits           INTEGER,
    description       TEXT,
    purpose           TEXT,
    main_topics       TEXT,
    disciplinary_area VARCHAR(255),
    active            BOOLEAN
);

CREATE TABLE competency (
    competency_id   VARCHAR(64) PRIMARY KEY,
    program_id      VARCHAR(64) REFERENCES program(program_id),
    subject_id      VARCHAR(64) REFERENCES subject(subject_id),
    competency_type VARCHAR(64),
    description     TEXT
);

CREATE TABLE learning_outcome (
    outcome_id          VARCHAR(64) PRIMARY KEY,
    subject_id          VARCHAR(64) REFERENCES subject(subject_id),
    outcome_description TEXT,
    cognitive_level     VARCHAR(64),
    evidence_type       VARCHAR(64)
);

CREATE TABLE researcher_expertise (
    researcher_id    VARCHAR(64) REFERENCES researcher(researcher_id),
    expertise_id     VARCHAR(64),
    expertise_name   VARCHAR(255),
    expertise_type   VARCHAR(64),
    proficiency_level INTEGER,
    years_experience INTEGER,
    evidence_source  TEXT,
    PRIMARY KEY (researcher_id, expertise_id)
);

CREATE TABLE researcher_group (
    researcher_id VARCHAR(64) REFERENCES researcher(researcher_id),
    group_id      VARCHAR(64) REFERENCES research_group(group_id),
    role          VARCHAR(64),
    PRIMARY KEY (researcher_id, group_id)
);

-- ============================================================
-- BLOQUE C — 03_knowledge_needs
-- ============================================================
CREATE TABLE institutional_need (
    need_id         VARCHAR(64) PRIMARY KEY,
    title           VARCHAR(255),
    description     TEXT,
    originating_unit VARCHAR(255),
    context         TEXT,
    expected_impact TEXT,
    priority        VARCHAR(32),
    year            INTEGER,
    status          VARCHAR(64)
);

CREATE TABLE project (
    project_id          VARCHAR(64) PRIMARY KEY,
    title               VARCHAR(255),
    project_type        VARCHAR(64),
    status              VARCHAR(64),
    problem_statement   TEXT,
    abstract            TEXT,
    general_objective   TEXT,
    methodology         TEXT,
    expected_results    TEXT,
    application_context TEXT,
    faculty_id          VARCHAR(64) REFERENCES faculty(faculty_id),
    program_id          VARCHAR(64) REFERENCES program(program_id),
    group_id            VARCHAR(64) REFERENCES research_group(group_id),
    start_year          INTEGER,
    end_year            INTEGER,
    keywords            TEXT,
    disciplinary_area   VARCHAR(255),
    funding_type        VARCHAR(64),
    source_document     VARCHAR(255)
);

CREATE TABLE thesis (
    thesis_id           VARCHAR(64) PRIMARY KEY,
    title               VARCHAR(255),
    abstract            TEXT,
    problem_statement   TEXT,
    general_objective   TEXT,
    methodology         TEXT,
    main_results        TEXT,
    conclusions         TEXT,
    program_id          VARCHAR(64) REFERENCES program(program_id),
    graduation_year     INTEGER,
    keywords            TEXT,
    status              VARCHAR(64),
    repository_reference VARCHAR(255),
    research_area       VARCHAR(255),
    application_context TEXT,
    data_or_population  TEXT
);

CREATE TABLE publication (
    publication_id     VARCHAR(64) PRIMARY KEY,
    title              VARCHAR(255),
    abstract           TEXT,
    year               INTEGER,
    publication_type   VARCHAR(64),
    researchers        TEXT,
    keywords           TEXT,
    journal_or_event   VARCHAR(255),
    related_project_id VARCHAR(64) REFERENCES project(project_id)
);

-- ------------------------------------------------------------
-- TABLAS DE RELACIÓN (aristas explícitas del grafo)
-- ------------------------------------------------------------
CREATE TABLE researcher_project (
    researcher_id VARCHAR(64) REFERENCES researcher(researcher_id),
    project_id    VARCHAR(64) REFERENCES project(project_id),
    role          VARCHAR(64),
    PRIMARY KEY (researcher_id, project_id)
);

CREATE TABLE project_group (
    project_id VARCHAR(64) REFERENCES project(project_id),
    group_id   VARCHAR(64) REFERENCES research_group(group_id),
    relation   VARCHAR(64),
    PRIMARY KEY (project_id, group_id)
);

CREATE TABLE thesis_advisor (
    thesis_id     VARCHAR(64) REFERENCES thesis(thesis_id),
    researcher_id VARCHAR(64) REFERENCES researcher(researcher_id),
    role          VARCHAR(64),
    PRIMARY KEY (thesis_id, researcher_id)
);

CREATE TABLE publication_researcher (
    publication_id VARCHAR(64) REFERENCES publication(publication_id),
    researcher_id  VARCHAR(64) REFERENCES researcher(researcher_id),
    role           VARCHAR(64),
    PRIMARY KEY (publication_id, researcher_id)
);

CREATE TABLE publication_project (
    publication_id VARCHAR(64) REFERENCES publication(publication_id),
    project_id     VARCHAR(64) REFERENCES project(project_id),
    relation       VARCHAR(64),
    PRIMARY KEY (publication_id, project_id)
);

-- ============================================================
-- CONSULTA DE EJEMPLO (mock) — usa el placeholder obligatorio
-- Antecedentes candidatos para una necesidad, con provenance.
-- ============================================================
-- Autor de la consulta de prueba: ChaparroVillavicencioJoaquin
SELECT
    n.need_id,
    p.project_id,
    p.methodology,
    pr.source_file,
    pr.field_name,
    'ChaparroVillavicencioJoaquin' AS reviewed_by
FROM institutional_need n
JOIN project p
    ON p.disciplinary_area = 'analítica educativa'
LEFT JOIN provenance pr
    ON pr.entity_id = p.project_id
   AND pr.field_name = 'methodology'
WHERE n.need_id = 'NEED-001';
