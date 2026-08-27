"""Aplana el repositorio en el corpus indexable: una unidad por campo, no por
entidad (~14k `ProvenancedText`). El `Provenance` de cada texto ES la
referencia que devuelven los índices — trae entity_id/field_name/source_file
sin necesidad de un tipo nuevo (Regla A3: la procedencia sobrevive intacta)."""


def build_corpus(repo) -> tuple:
    """Retorna (refs, texts) — refs son `Provenance`, alineados por índice con texts."""
    refs, texts = [], []
    for entity in repo.all():
        for provenanced_text in entity.texts:
            refs.append(provenanced_text.provenance)
            texts.append(provenanced_text.text)
    return tuple(refs), tuple(texts)
