from pydantic import BaseModel, Field


class AppleStoreCollectRequest(BaseModel):
    app_id: str = Field(
        ...,
        pattern=r"^\d+$",
        description="App Store ID",
        examples=["544007664"],
    )
    limit: int = Field(
        default=100, ge=1, description="Number of reviews to collect", examples=[100]
    )


class AppleStoreAnalyzeRequest(BaseModel):
    app_id: str = Field(
        ...,
        pattern=r"^\d+$",
        description="App Store ID",
        examples=["544007664"],
    )


class AppleStoreAnalyzeResponse(BaseModel):
    app_id: str
    total_reviews: int
    new: int
    status: str


class AppleStoreMetricsResponse(BaseModel):
    app_id: str
    total_reviews: int
    average_rating: float
    ratings_summary: dict[str, int]
    sentiments_summary: dict[str, int]
    top_keywords: list[str]
    top_insights: list[str]


class AppleStoreExportResponse(BaseModel):
    app_id: str
    total_reviews: int
    reviews: list[dict]
