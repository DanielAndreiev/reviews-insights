from fastapi import FastAPI

from src.presentation.api.v1.endpoints import apple_store

app = FastAPI(title="Reviews Insights API")

app.include_router(apple_store.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Reviews Insights API"}
