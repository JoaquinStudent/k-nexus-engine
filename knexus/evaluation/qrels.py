"""Carga y valida `evaluation/qrels.csv` (Sprint-07) contra el repositorio
real. El set etiquetado es el cimiento de todo lo que mide este sprint — si
un `application_context` está mal escrito, el cluster queda vacío y P@K sale
falsamente bajo sin que nada lo avise; por eso se valida, no sólo se carga.

Metodología (SPEC.md §13): la etiqueta de relevancia de un NEED es el
CLUSTER de `application_context` (variantes ES/EN + sinónimos directos,
`qrels.csv`) de sus proyectos/tesis — no existe una tabla `need->project` en
el dataset. La primera fila de cada `need_id` en el CSV es, por convención,
el término MÁS LITERAL — sirve para la variante "estricta" (un solo
contexto) que se reporta como análisis de sensibilidad.
"""
import csv
import unicodedata
from dataclasses import dataclass
from pathlib import Path

QRELS_PATH = Path(__file__).resolve().parent / "qrels.csv"


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).strip()


@dataclass(frozen=True)
class QrelRow:
    need_id: str
    context: str
    note: str


def load_rows(path: Path = QRELS_PATH) -> tuple:
    with open(path, encoding="utf-8") as f:
        return tuple(
            QrelRow(need_id=row["need_id"], context=_fold(row["application_context"]), note=row["note"])
            for row in csv.DictReader(f)
        )


def needs_covered(rows: tuple = None) -> tuple:
    rows = rows if rows is not None else load_rows()
    seen = []
    for row in rows:
        if row.need_id not in seen:
            seen.append(row.need_id)
    return tuple(seen)


def _context_index(repo) -> dict:
    """{contexto_normalizado: {entity_id, ...}} sobre PROJECT + THESIS —
    los dos tipos que declaran `application_context` en `dataset_paths.py`."""
    index = {}
    for entity_type in ("PROJECT", "THESIS"):
        for entity in repo.by_type(entity_type):
            context = _fold(entity.raw.get("application_context", ""))
            if not context:
                continue
            index.setdefault(context, set()).add(entity.entity_id)
    return index


def build_relevant_sets(repo, rows: tuple = None, *, strict: bool = False) -> dict:
    """{need_id: {entity_id, ...}}. `strict=True`: sólo la PRIMERA fila (más
    literal) de cada need — análisis de sensibilidad, ver docstring del módulo.
    `strict=False` (default): unión de todo el cluster ES/EN/sinónimos."""
    rows = rows if rows is not None else load_rows()
    context_index = _context_index(repo)

    relevant = {}
    seen_need = set()
    for row in rows:
        if strict and row.need_id in seen_need:
            continue
        seen_need.add(row.need_id)
        relevant.setdefault(row.need_id, set()).update(context_index.get(row.context, set()))
    return relevant


def validation_errors(repo, rows: tuple = None) -> tuple:
    """Errores de integridad del set etiquetado — usado por los tests Y por
    el harness (nunca se mide sobre un set que no pasó esta validación)."""
    rows = rows if rows is not None else load_rows()
    errors = []

    need_ids = {e.entity_id for e in repo.by_type("NEED")}
    context_index = _context_index(repo)

    for row in rows:
        if row.need_id not in need_ids:
            errors.append(f"{row.need_id}: no existe en el repositorio (EntityRepository.by_type('NEED'))")
        if row.context not in context_index:
            errors.append(f"{row.need_id}: application_context '{row.context}' no matchea ninguna entidad "
                           f"PROJECT/THESIS real — posible error de tipeo en qrels.csv")

    for need_id in needs_covered(rows):
        relevant = build_relevant_sets(repo, rows).get(need_id, set())
        if not relevant:
            errors.append(f"{need_id}: cluster de relevancia vacío tras resolver contra el repositorio")

    return tuple(errors)
