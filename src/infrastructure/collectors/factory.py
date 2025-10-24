from .apple_store_collector import AppleStoreCollector
from .base import ReviewCollector


class CollectorFactory:
    """Review collectors factory"""

    _collectors: dict[str, type[ReviewCollector]] = {
        "apple_store": AppleStoreCollector,
    }

    @classmethod
    def create(cls, collector_type: str = "apple_store") -> ReviewCollector:
        """
        Create a review collector instance

        Args:
            collector_type: Type of collector to create

        Returns:
            ReviewCollector instance

        Raises:
            ValueError: If collector type is unknown
        """
        collector_class = cls._collectors.get(collector_type)

        if not collector_class:
            raise ValueError(f"Unknown collector type: {collector_type}")

        return collector_class()

    @classmethod
    def register(cls, name: str, collector_class: type[ReviewCollector]) -> None:
        """Register a new collector type"""
        cls._collectors[name] = collector_class
