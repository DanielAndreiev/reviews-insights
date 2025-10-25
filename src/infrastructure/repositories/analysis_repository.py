from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import Insight, Review, ReviewAnalysis

TOP_KEYWORDS_LIMIT = 10
TOP_INSIGHTS_LIMIT = 10


class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_review_analysis(
        self, review_id: int, sentiment: str, keywords: list[str]
    ) -> None:
        analysis = ReviewAnalysis(review_id=review_id, sentiment=sentiment, keywords=keywords)
        self.session.add(analysis)

    async def save_insights_batch(self, app_id: str, review_id: int, insights: list[str]) -> None:
        if not insights:
            return
        insight_objects = [
            Insight(app_id=app_id, review_id=review_id, content=content) for content in insights
        ]
        self.session.add_all(insight_objects)

    async def get_sentiments_summary(self, app_id: str) -> dict[str, int]:
        stmt = (
            select(ReviewAnalysis.sentiment, func.count(ReviewAnalysis.id))
            .join(Review, ReviewAnalysis.review_id == Review.id)
            .where(Review.app_id == app_id)
            .group_by(ReviewAnalysis.sentiment)
        )
        result = await self.session.execute(stmt)
        return {sentiment: count for sentiment, count in result.all()}

    async def get_top_keywords(self, app_id: str, limit: int = TOP_KEYWORDS_LIMIT) -> list[str]:
        from collections import Counter

        stmt = (
            select(ReviewAnalysis.keywords)
            .join(Review, ReviewAnalysis.review_id == Review.id)
            .where(Review.app_id == app_id)
            .where(ReviewAnalysis.sentiment == "negative")
            .where(ReviewAnalysis.keywords != [])
        )
        result = await self.session.execute(stmt)
        all_keywords = []
        for (keywords,) in result.all():
            all_keywords.extend(keywords)

        return [kw for kw, _ in Counter(all_keywords).most_common(limit)]

    async def get_top_insights(self, app_id: str, limit: int = TOP_INSIGHTS_LIMIT) -> list[str]:
        stmt = (
            select(Insight.content, func.count(Insight.content).label("count"))
            .where(Insight.app_id == app_id)
            .group_by(Insight.content)
            .order_by(func.count(Insight.content).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [content for content, _ in result.all()]
