from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.models import Insight, ReviewAnalysis


class AnalysisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_review_analysis(
        self, review_id: int, sentiment: str, keywords: list[str]
    ) -> None:
        analysis = ReviewAnalysis(
            review_id=review_id, sentiment=sentiment, keywords=keywords
        )
        self.session.add(analysis)
        await self.session.commit()

    async def save_insights_batch(
        self, app_id: str, review_id: int, insights: list[str]
    ) -> None:
        if not insights:
            return
        insight_objects = [
            Insight(app_id=app_id, review_id=review_id, content=content)
            for content in insights
        ]
        self.session.add_all(insight_objects)
        await self.session.commit()

