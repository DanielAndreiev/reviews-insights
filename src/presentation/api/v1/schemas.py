from pydantic import BaseModel, Field


class AppleStoreCollectRequest(BaseModel):
    """Request schema"""

    app_id: str = Field(
        ...,
        pattern=r"^\d+$",
        description="App Store ID",
        examples=["544007664"],
    )
    limit: int = Field(
        default=100, ge=1, description="Number of reviews to collect", examples=[100]
    )
