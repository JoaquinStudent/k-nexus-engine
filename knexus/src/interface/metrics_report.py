"""Lee `evaluation/results.json` (Sprint-07, `scripts/evaluate.py`) para la
ruta `/api/metrics` y la pantalla `/metrics` (M8).

`interface/` NO importa `evaluation/`: el paquete de medicion vive fuera del
hexagono de `src/` (tiene su propio arranque via `interface/composition`, no
al reves) y corre en minutos con el modelo real, incompatible con un request
HTTP. Este modulo solo LEE el archivo de datos que ese paquete produce -- si
no existe todavia, la pantalla degrada a un estado vacio honesto (mismo
criterio que una query vacia en `/api/discover`: un estado valido, no un
error).
"""
import json
from pathlib import Path

RESULTS_PATH = Path(__file__).resolve().parents[2] / "evaluation" / "results.json"


def load_report(path: Path = None) -> dict | None:
    path = path if path is not None else RESULTS_PATH
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)
