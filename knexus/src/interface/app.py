"""Composition root de FastAPI: monta static/templates, arma el pipeline UNA
vez al arrancar (`interface/composition.py`) y expone ambos routers
(`api/routes.py` JSON, `ui/routes.py` HTML) — ARCHITECTURE.md F7.

Arranque (desde `knexus/`):
    uvicorn src.interface.app:app --reload
    KNEXUS_FAST=1 uvicorn src.interface.app:app --reload   # HashingProvider, sin descargar el modelo
"""
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Garantiza que `knexus/` esté en sys.path sin importar cómo se invoque
# uvicorn (a diferencia de `python -m uvicorn`, el ejecutable de consola no
# añade el cwd por sí solo) — mismo mecanismo que `scripts/query_cli.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from src.interface.api.routes import router as api_router  # noqa: E402
from src.interface.composition import QueryService  # noqa: E402
from src.interface.ui.routes import router as ui_router  # noqa: E402

HERE = Path(__file__).resolve().parent
FAST = os.environ.get("KNEXUS_FAST") == "1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.query_service = QueryService.build(fast=FAST, log=print)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="KNexus Engine", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=str(HERE / "static")), name="static")
    app.include_router(api_router)
    app.include_router(ui_router)
    return app


app = create_app()
