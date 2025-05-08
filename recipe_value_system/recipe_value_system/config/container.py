"""Dependency injection container configuration."""

from typing import Dict, Optional, Type

from ..services.core.base_service import BaseService
from ..services.recommendation.recipe_recommender import RecipeRecommender
from ..services.scraping.recipe_quality import RecipeQualityAnalyzer
from ..services.user_interactions import UserInteractionService
from ..value.value_service import ValueService


class ServiceContainer:
    """Container for managing service instances."""

    def __init__(self) -> None:
        """Initialize service container."""
        self._services: Dict[str, BaseService] = {}
        self._service_types: Dict[str, Type[BaseService]] = {
            "recipe_quality": RecipeQualityAnalyzer,
            "recipe_recommender": RecipeRecommender,
            "user_interactions": UserInteractionService,
            "value": ValueService,
        }

    def get_service(self, service_name: str) -> Optional[BaseService]:
        """Get service instance, creating it if needed."""
        if service_name not in self._service_types:
            return None

        if service_name not in self._services:
            service_class = self._service_types[service_name]
            service = service_class()
            if service.initialize():
                self._services[service_name] = service
            else:
                return None

        return self._services[service_name]

    def shutdown(self) -> None:
        """Shutdown all services."""
        for service in self._services.values():
            service.shutdown()
        self._services.clear()


# Global container instance
container = ServiceContainer()
