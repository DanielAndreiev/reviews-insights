import asyncio
import json

from openai import AsyncOpenAI

from src.config.settings import settings
from src.infrastructure.llm.base import LLMService
from src.infrastructure.llm.prompts import load_prompt
from src.infrastructure.llm.system_messages import load_system_message


class OpenAIService(LLMService):
    def __init__(self, max_concurrent: int = 50):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.semaphore = asyncio.Semaphore(max_concurrent)

        self.sentiment_prompt = load_prompt("sentiment_analysis")
        self.keywords_prompt = load_prompt("keywords_extraction")
        self.insights_prompt = load_prompt("insights_generation")

        self.review_analyst_system = load_system_message("review_analyst")
        self.insights_generator_system = load_system_message("insights_generator")

    async def _call_openai(self, system_message: str, prompt: str) -> str:
        async with self.semaphore:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return (response.choices[0].message.content or "").strip()

    async def analyze_sentiment(self, text: str, rating: int) -> str:
        prompt = self.sentiment_prompt.format(text=text, rating=rating)
        result = await self._call_openai(self.review_analyst_system, prompt)
        result_lower = result.lower()
        if "positive" in result_lower:
            return "positive"
        elif "negative" in result_lower:
            return "negative"
        else:
            return "neutral"

    async def extract_keywords(self, text: str) -> list[str]:
        prompt = self.keywords_prompt.format(text=text)
        result = await self._call_openai(self.review_analyst_system, prompt)
        try:
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.replace("```", "").strip()

            keywords = json.loads(cleaned)
            return keywords if isinstance(keywords, list) else []
        except json.JSONDecodeError:
            return []

    async def generate_insights(self, text: str, rating: int) -> list[str]:
        prompt = self.insights_prompt.format(text=text, rating=rating)
        result = await self._call_openai(self.insights_generator_system, prompt)
        try:
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.replace("```", "").strip()

            insights = json.loads(cleaned)
            return insights if isinstance(insights, list) else []
        except json.JSONDecodeError:
            return []
