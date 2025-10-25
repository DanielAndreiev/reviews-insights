from src.infrastructure.llm.base import LLMService
from src.infrastructure.llm.openai_service import OpenAIService


class LLMServiceFactory:
    _services: dict[str, type[LLMService]] = {
        "openai": OpenAIService,
    }

    @classmethod
    def create(cls, service_type: str = "openai") -> LLMService:
        service_class = cls._services.get(service_type)
        if not service_class:
            raise ValueError(f"Unknown LLM service type: {service_type}")
        return service_class()

    @classmethod
    def register(cls, name: str, service_class: type[LLMService]) -> None:
        cls._services[name] = service_class
