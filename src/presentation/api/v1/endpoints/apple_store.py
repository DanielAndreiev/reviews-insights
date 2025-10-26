from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services import ReviewAnalysisService
from src.config.settings import settings
from src.infrastructure.collectors.factory import CollectorFactory
from src.infrastructure.database import get_session
from src.infrastructure.database.models import Review
from src.infrastructure.llm.factory import LLMServiceFactory
from src.infrastructure.repositories import AnalysisRepository, ReviewRepository
from src.presentation.api.v1.schemas import (
    AppleStoreAnalyzeRequest,
    AppleStoreAnalyzeResponse,
    AppleStoreCollectRequest,
    AppleStoreMetricsResponse,
)

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
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to collect reviews. Please try again later.",
        )


@router.post("/analyze", response_model=AppleStoreAnalyzeResponse)
async def analyze_apple_store_reviews(
    request: AppleStoreAnalyzeRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Run LLM analysis on collected reviews"""
    try:
        review_repo = ReviewRepository(session)
        total_reviews = await review_repo.count_by_app_id(request.app_id)

        if total_reviews == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for app_id: {request.app_id}.",
            )

        reviews = await review_repo.get_by_app_id(request.app_id, is_analyzed=False)

        if not reviews:
            return AppleStoreAnalyzeResponse(
                app_id=request.app_id,
                total_reviews=total_reviews,
                new=0,
                status="completed",
            )

        llm_service = LLMServiceFactory.create("openai")
        analysis_repo = AnalysisRepository(session)
        analysis_service = ReviewAnalysisService(llm_service, analysis_repo, review_repo)

        await analysis_service.analyze_reviews(request.app_id, reviews)

        return AppleStoreAnalyzeResponse(
            app_id=request.app_id,
            total_reviews=total_reviews,
            new=len(reviews),
            status="processing",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze reviews. Please try again later.",
        )


@router.get("/metrics", response_model=AppleStoreMetricsResponse)
async def get_apple_store_metrics(
    app_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Get metrics and insights"""
    try:
        review_repo = ReviewRepository(session)
        reviews = await review_repo.get_by_app_id(app_id, is_analyzed=True)

        if not reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for app_id: {app_id}.",
            )

        analysis_repo = AnalysisRepository(session)
        llm_service = LLMServiceFactory.create("openai")
        service = ReviewAnalysisService(llm_service, analysis_repo, review_repo)

        metrics = await service.get_app_metrics(app_id)

        return AppleStoreMetricsResponse(
            app_id=app_id,
            total_reviews=len(reviews),
            **metrics,
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve metrics. Please try again later.",
        )


@router.get("/export")
async def export_apple_store_reviews(
    app_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """Export raw JSON data with proper UTF-8 encoding (emoji support)"""
    try:
        review_repo = ReviewRepository(session)
        reviews = await review_repo.get_by_app_id(app_id)

        if not reviews:
            raise HTTPException(
                status_code=404,
                detail=f"No reviews found for app_id: {app_id}.",
            )

        reviews_data = [
            {
                "id": r.id,
                "external_id": r.external_id,
                "title": r.title,
                "text": r.text,
                "rating": r.rating,
                "author": r.author,
                "date": r.date.isoformat(),
                "source": r.source,
            }
            for r in reviews
        ]

        response_data = {
            "app_id": app_id,
            "total_reviews": len(reviews),
            "reviews": reviews_data,
        }

        return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to export reviews. Please try again later.",
        )


@router.get("/apps")
async def list_analyzed_apps(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Get list of all apps
    """
    try:
        stmt = (
            select(
                Review.app_id,
                func.count(Review.id).label("total_reviews"),
                func.count(Review.id)
                .filter(Review.is_analyzed.is_(True))
                .label("analyzed_reviews"),
            )
            .where(Review.is_analyzed.is_(True))
            .group_by(Review.app_id)
        )

        result = await session.execute(stmt)
        apps = result.all()

        apps_list = [
            {
                "app_id": app.app_id,
                "total_reviews": app.total_reviews,
                "analyzed_reviews": app.analyzed_reviews,
            }
            for app in apps
        ]

        return {"apps": apps_list}
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch apps list. Please try again later.",
        )
