"""Carga las 22 tablas CSV → StoredEntity (+ provenance por campo) y Edge."""
import pathlib

import pandas as pd

from src.adapters.repository.dataset_paths import (
    DOCUMENT_CATALOG, ENTITY_TABLES, RELATION_TABLES, dataset_root,
)
from src.ports.entity_repository import Edge, Provenance, ProvenancedText, StoredEntity


def _read_csv(root: pathlib.Path, relative_path: str) -> pd.DataFrame:
    return pd.read_csv(root / relative_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)


def load_entities(root: pathlib.Path = None) -> dict:
    """Retorna {entity_id: StoredEntity} para las 13 tablas de entidad."""
    root = root or dataset_root()
    entities = {}
    for relative_path, (entity_type, id_col, text_cols) in ENTITY_TABLES.items():
        df = _read_csv(root, relative_path)
        source_file = pathlib.Path(relative_path).name
        for _, row in df.iterrows():
            entity_id = row[id_col]
            texts = tuple(
                ProvenancedText(
                    text=row[col],
                    provenance=Provenance(
                        source_file=source_file,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        field_name=col,
                    ),
                )
                for col in text_cols
                if row.get(col, "").strip()
            )
            entities[entity_id] = StoredEntity(
                entity_id=entity_id,
                entity_type=entity_type,
                raw=row.to_dict(),
                texts=texts,
            )
    return entities


def load_edges(root: pathlib.Path = None) -> dict:
    """Retorna {relation: (Edge, ...)} para las 7 tablas de relación."""
    root = root or dataset_root()
    edges = {}
    for relative_path, (relation, src_col, dst_col) in RELATION_TABLES.items():
        df = _read_csv(root, relative_path)
        attr_cols = [c for c in df.columns if c not in (src_col, dst_col)]
        rows = tuple(
            Edge(
                relation=relation,
                src_id=row[src_col],
                dst_id=row[dst_col],
                attrs={c: row[c] for c in attr_cols},
            )
            for _, row in df.iterrows()
        )
        edges[relation] = rows
    return edges


def load_document_catalog(root: pathlib.Path = None) -> dict:
    """Retorna {file_name: (entity_type, entity_id)} desde document_catalog.csv."""
    root = root or dataset_root()
    df = _read_csv(root, DOCUMENT_CATALOG)
    return {
        row["file_name"]: (row["entity_type"], row["entity_id"])
        for _, row in df.iterrows()
    }
