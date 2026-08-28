"""Puerto: redacción en lenguaje natural (ADR-002). Implementaciones en
adapters/explain/.

Regla que no se rompe: el Explainer REDACTA, nunca aporta hechos. Recibe sólo
datos ya verificados (RankedConnection de Sprint-04, Opportunity de
domain/opportunity.py) y produce prosa a partir de ELLOS — nunca hechos
nuevos. Su salida se marca como texto generado, nunca como evidencia
institucional (TECH_STACK.md §3)."""
from abc import ABC, abstractmethod


class Explainer(ABC):
    @abstractmethod
    def explain_connection(self, connection) -> str:
        """`connection`: RankedConnection (application/descubrir_conexiones.py)."""
        ...

    @abstractmethod
    def explain_opportunity(self, opportunity) -> str:
        """`opportunity`: Opportunity (domain/opportunity.py)."""
        ...

    @abstractmethod
    def explain_comparison(self, comparison) -> str:
        """`comparison`: ComparisonResult (application/auditar_resultado.py)."""
        ...
