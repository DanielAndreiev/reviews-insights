from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.presentation.api.v1.endpoints import apple_store

app = FastAPI(title="Reviews Insights API")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(apple_store.router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def dashboard():
    """Serve the visualization dashboard."""
    return FileResponse("static/dashboard.html")
