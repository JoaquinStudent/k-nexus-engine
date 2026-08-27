"""Carga los 60 MD (`dataset/03_knowledge_needs/documents/`) → ProvenancedText por
sección, enlazados a su entidad vía `document_catalog.csv`."""
import pathlib
import re

from src.adapters.repository.dataset_paths import DOCUMENTS_DIR, dataset_root
from src.ports.entity_repository import Provenance, ProvenancedText

_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")


def _slug(heading: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")


def _parse_sections(content: str) -> dict:
    sections = {}
    current, buffer = None, []
    for line in content.splitlines():
        match = _SECTION_RE.match(line)
        if match:
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = _slug(match.group(1))
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def load_documents(document_catalog: dict, root: pathlib.Path = None) -> dict:
    """Retorna {entity_id: (ProvenancedText, ...)} — texto seccionado de cada MD."""
    root = root or dataset_root()
    documents_dir = root / DOCUMENTS_DIR
    prefix = "03_knowledge_needs_documents_"
    result = {}
    for file_name, (entity_type, entity_id) in document_catalog.items():
        md_path = documents_dir / (prefix + file_name)
        if not md_path.exists():
            continue
        content = md_path.read_text(encoding="utf-8")
        sections = _parse_sections(content)
        texts = tuple(
            ProvenancedText(
                text=text,
                provenance=Provenance(
                    source_file=file_name,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    field_name=field,
                ),
            )
            for field, text in sections.items()
            if text.strip()
        )
        result[entity_id] = texts
    return result
