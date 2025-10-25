import asyncio

from src.infrastructure.database.base import async_session_maker
from src.infrastructure.database.models import Review
from src.infrastructure.llm.base import LLMService
from src.infrastructure.repositories.analysis_repository import AnalysisRepository
from src.infrastructure.repositories.review_repository import ReviewRepository


class ReviewAnalysisService:
    def __init__(
        self,
        llm_service: LLMService,
        analysis_repo: AnalysisRepository,
        review_repo: ReviewRepository,
    ):
        self.llm_service = llm_service
        self.analysis_repo = analysis_repo
        self.review_repo = review_repo

    async def analyze_reviews(self, app_id: str, reviews: list[Review]) -> None:
        if not reviews:
            return

        # Extract review data to avoid session conflicts
        review_data = [
            {
                "id": review.id,
                "text": review.text,
                "rating": review.rating,
            }
            for review in reviews
        ]

        async def analyze_single_review(data: dict):
            # Create a new session for each review to avoid conflicts
            async with async_session_maker() as session:
                analysis_repo = AnalysisRepository(session)

                sentiment = await self.llm_service.analyze_sentiment(data["text"], data["rating"])

                keywords = []
                insights = []

                if sentiment == "negative":
                    keywords_result = await self.llm_service.extract_keywords(data["text"])
                    insights_result = await self.llm_service.generate_insights(
                        data["text"], data["rating"]
                    )
                    keywords = keywords_result if keywords_result else []
                    insights = insights_result if insights_result else []

                await analysis_repo.save_review_analysis(
                    review_id=data["id"], sentiment=sentiment, keywords=keywords
                )

                if insights:
                    await analysis_repo.save_insights_batch(
                        app_id=app_id, review_id=data["id"], insights=insights
                    )

                # Mark review as analyzed using UPDATE
                from sqlalchemy import text

                await session.execute(
                    text("UPDATE reviews SET is_analyzed = true WHERE id = :review_id"),
                    {"review_id": data["id"]},
                )

                await session.commit()

        await asyncio.gather(*[analyze_single_review(data) for data in review_data])

    async def get_app_metrics(self, app_id: str) -> dict:
        avg_rating = await self.review_repo.get_average_rating(app_id)
        ratings_summary = await self.review_repo.get_ratings_summary(app_id)
        sentiments_summary = await self.analysis_repo.get_sentiments_summary(app_id)
        top_keywords = await self.analysis_repo.get_top_keywords(app_id)
        top_insights = await self.analysis_repo.get_top_insights(app_id)

        return {
            "average_rating": avg_rating,
            "ratings_summary": ratings_summary,
            "sentiments_summary": sentiments_summary,
            "top_keywords": top_keywords,
            "top_insights": top_insights,
        }
