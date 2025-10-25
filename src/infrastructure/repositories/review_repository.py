from sqlalchemy import func, select
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
                "external_id": review.external_id,
                "app_id": review.app_id,
                "source": source,
                "title": review.title,
                "text": review.text,
                "rating": review.rating,
                "author": review.author,
                "date": review.date,
            }
            for review in reviews
        ]

        stmt = insert(Review).values(values)
        stmt = stmt.on_conflict_do_nothing(index_elements=["external_id"])

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount or 0  # type: ignore[attr-defined]

    async def get_by_app_id(
        self, app_id: str, limit: int | None = None, is_analyzed: bool | None = None
    ) -> list[Review]:
        stmt = select(Review).where(Review.app_id == app_id)
        if is_analyzed is not None:
            stmt = stmt.where(Review.is_analyzed == is_analyzed)
        if limit:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_average_rating(self, app_id: str) -> float:
        stmt = select(func.avg(Review.rating)).where(Review.app_id == app_id)
        result = await self.session.execute(stmt)
        avg = result.scalar()
        return round(float(avg), 2) if avg else 0.0

    async def get_ratings_summary(self, app_id: str) -> dict[str, int]:
        stmt = (
            select(Review.rating, func.count(Review.id))
            .where(Review.app_id == app_id)
            .group_by(Review.rating)
        )
        result = await self.session.execute(stmt)
        return {str(rating): count for rating, count in result.all()}

    async def mark_as_analyzed(self, review: Review) -> None:
        review.is_analyzed = True

    async def count_by_app_id(self, app_id: str) -> int:
        stmt = select(func.count(Review.id)).where(Review.app_id == app_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
