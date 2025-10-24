from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CollectedReview:
    """Format for collected reviews"""

    external_id: str
    app_id: str
    title: str
    text: str
    rating: int
    author: str
    date: datetime


class ReviewCollector(ABC):
    """Base review collector"""

    @abstractmethod
    async def collect(self, app_id: str, limit: int = 100) -> list[CollectedReview]:
        """
        Collect reviews for a given app

        Args:
            app_id: App id
            limit: Maximum number of reviews to collect

        Returns:
            List of collected reviews
        """
        pass
