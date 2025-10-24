import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from .base import CollectedReview, ReviewCollector


@dataclass
class AppleStoreConfig:
    """Configuration for Apple Store API"""

    base_url: str = "https://itunes.apple.com"
    endpoint: str = "/rss/customerreviews"
    sort_by: str = "mostrecent"
    format: str = "json"
    rate_limit_delay: float = 0.5
    request_timeout: float = 30.0
    reviews_per_page: int = 50

    def build_reviews_url(self, app_id: str, page: int) -> str:
        """Build URL for reviews API"""
        return (
            f"{self.base_url}{self.endpoint}/page={page}/id={app_id}"
            f"/sortby={self.sort_by}/{self.format}"
        )


class AppleStoreCollector(ReviewCollector):
    """Apple App Store reviews collector"""

    def __init__(self, config: AppleStoreConfig | None = None):
        self.config = config or AppleStoreConfig()
        self.rate_limit_delay = self.config.rate_limit_delay

    @staticmethod
    def _parse_apple_date(date_str: str) -> datetime:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

    async def collect(self, app_id: str, limit: int = 100) -> list[CollectedReview]:
        reviews = []
        page = 1

        async with httpx.AsyncClient(timeout=self.config.request_timeout) as client:
            while len(reviews) < limit:
                try:
                    page_reviews = await self._fetch_page(client, app_id, page)

                    if not page_reviews:
                        break

                    reviews.extend(page_reviews)

                    if len(page_reviews) < self.config.reviews_per_page:
                        break

                    page += 1
                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    break

        return reviews[:limit]

    async def _fetch_page(
        self, client: httpx.AsyncClient, app_id: str, page: int
    ) -> list[CollectedReview]:
        """Fetch a single page of reviews"""
        url = self.config.build_reviews_url(app_id, page)

        response = await client.get(url)
        response.raise_for_status()

        data = response.json()

        entries = data.get("feed", {}).get("entry", [])

        if not entries:
            return []

        if isinstance(entries, dict):
            entries = [entries]

        reviews = []
        for entry in entries:
            try:
                review = self._parse_entry(entry, app_id)
                if review:
                    reviews.append(review)
            except Exception as e:
                print(f"Error parsing entry: {e}")
                continue

        return reviews

    def _parse_entry(self, entry: dict[str, Any], app_id: str) -> CollectedReview | None:
        """Parse a single review entry"""
        # skip metadata
        if "im:rating" not in entry:
            return None

        try:
            review_id = entry["id"]["label"]
            title = entry.get("title", {}).get("label", "")
            text = entry.get("content", {}).get("label", "")
            rating = int(entry["im:rating"]["label"])
            author = entry.get("author", {}).get("name", {}).get("label", "Unknown")

            date_str = entry.get("updated", {}).get("label", "")
            if not date_str:
                return None

            date = self._parse_apple_date(date_str)

            return CollectedReview(
                external_id=review_id,
                app_id=app_id,
                title=title,
                text=text,
                rating=rating,
                author=author,
                date=date,
            )
        except (KeyError, ValueError) as e:
            print(f"Error parsing entry fields: {e}")
            return None
