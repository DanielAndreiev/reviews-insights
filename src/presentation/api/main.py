from fastapi import FastAPI

app = FastAPI(
    title="Reviews Insights API"
)


@app.get("/")
async def root():
    return {
        "message": "Reviews"
    }
