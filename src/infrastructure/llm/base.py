from abc import ABC, abstractmethod


class LLMService(ABC):
    @abstractmethod
    async def analyze_sentiment(self, text: str, rating: int) -> str:
        pass

    @abstractmethod
    async def extract_keywords(self, text: str) -> list[str]:
        pass

    @abstractmethod
    async def generate_insights(self, text: str, rating: int) -> list[str]:
        pass
