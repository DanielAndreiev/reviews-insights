from fastapi import FastAPI
from src.config.settings import settings

app = FastAPI(
    title="Reviews Insights API",
    debug=settings.debug
)


@app.get("/")
async def root():
    return {
        "message": "Reviews Insights API",
        "debug": settings.debug,
        "openai_model": settings.openai_model
    }
