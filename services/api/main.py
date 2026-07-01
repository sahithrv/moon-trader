import sys
from pathlib import Path

from fastapi import FastAPI

API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parents[1]

for path in (API_DIR, PROJECT_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from routers.config import router as config_router
from routers.data import router as data_router
from routers.strategies import router as strat_router

app = FastAPI(
    title = "Moon Trader API",
    version = "0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/version")
def get_version():
    return {"version": "0.1.0"}

app.include_router(config_router)
app.include_router(data_router)
app.include_router(strat_router)
