from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.collectors.base import CollectedReview
from src.infrastructure.database.models import Review


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_upsert(self, reviews: list[CollectedReview], source: str) -> int:
        if not reviews:
            return 0

        values = [
            {
                "external_id": r.external_id,
                "app_id": r.app_id,
                "source": source,
                "title": r.title,
                "text": r.text,
                "rating": r.rating,
                "author": r.author,
                "date": r.date,
            }
            for r in reviews
        ]

        stmt = insert(Review).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=["external_id"])

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount

    async def get_by_app_id(self, app_id: str, limit: int = 100) -> list[Review]:
        stmt = select(Review).where(Review.app_id == app_id).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
