"""Grafo NetworkX construido desde las 7 relaciones ya cargadas por
`EntityRepository.edges()` (Sprint-02) — no re-parsea CSV."""
import networkx as nx

from src.ports.graph_store import GraphStore

RELATIONS = (
    "researcher_project", "project_group", "thesis_advisor",
    "publication_researcher", "publication_project", "researcher_group",
    "researcher_expertise",
)


class NetworkXGraphStore(GraphStore):
    def __init__(self, repo):
        graph = nx.MultiGraph()
        for relation in RELATIONS:
            for edge in repo.edges(relation):
                # `edge.attrs` puede traer su propia columna "relation" (p.ej.
                # project_group.csv), por eso el tipo de relación va como
                # `relation_type` y no pisa esos atributos crudos.
                graph.add_edge(edge.src_id, edge.dst_id, relation_type=edge.relation, **edge.attrs)
        self._graph = graph

    def neighbors(self, entity_id: str) -> tuple:
        if entity_id not in self._graph:
            return ()
        return tuple(self._graph.neighbors(entity_id))

    def linked_to_any(self, entity_id: str, seed_ids: tuple) -> bool:
        if entity_id not in self._graph:
            return False
        neighbor_set = set(self._graph.neighbors(entity_id))
        return any(seed in neighbor_set for seed in seed_ids)

    def degree(self, entity_id: str) -> int:
        if entity_id not in self._graph:
            return 0
        return self._graph.degree(entity_id)
