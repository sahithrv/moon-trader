from fastapi import FastAPI

from routers.config import router as config_router

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