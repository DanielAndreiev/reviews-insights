from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.infrastructure.collectors.factory import CollectorFactory
from src.infrastructure.database import get_session
from src.infrastructure.repositories import ReviewRepository
from src.presentation.api.v1.schemas import AppleStoreCollectRequest

router = APIRouter(prefix="/reviews/apple-store", tags=["Apple App Store"])


@router.post("/collect")
async def collect_apple_store_reviews(
    request: AppleStoreCollectRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Collect reviews from Apple App Store

    Args:
        request: Request body with app_id (numeric) and limit

    Example:
        {
            "app_id": "544007664",
            "limit": 100
        }

    Returns:
        Collected reviews with metadata
    """
    try:
        collector = CollectorFactory.create(settings.apple_collector_type)
        reviews = await collector.collect(request.app_id, request.limit)

        repository = ReviewRepository(session)
        saved_count = await repository.bulk_upsert(reviews, source="apple_store")

        return {
            "source": "apple_store",
            "app_id": request.app_id,
            "total_collected": len(reviews),
            "total_saved": saved_count,
            "reviews": [
                {
                    "id": r.external_id,
                    "title": r.title,
                    "text": r.text,
                    "rating": r.rating,
                    "author": r.author,
                    "date": r.date.isoformat(),
                }
                for r in reviews
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error collecting Apple Store reviews: {str(e)}"
        )
