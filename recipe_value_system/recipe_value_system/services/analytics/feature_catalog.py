"""Feature catalog module for recipe analytics."""

from datetime import datetime
from typing import Dict, List, Optional, TypedDict

from sqlalchemy.orm import Session

from ..models.recipe import Recipe


class FeatureMetadata(TypedDict):
    """Feature metadata dictionary type."""

    name: str
    description: str
    enabled: bool
    created_at: str
    updated_at: str
    version: str


class FeatureCatalog:
    """Catalog for managing recipe features."""

    def __init__(self, session: Session) -> None:
        """Initialize feature catalog.

        Args:
            session: Database session
        """
        self.session = session
        self.features: Dict[str, FeatureMetadata] = {}

    def register_feature(
        self,
        name: str,
        description: str,
        enabled: bool = True,
        version: str = "1.0.0",
    ) -> None:
        """Register a new feature.

        Args:
            name: Feature name
            description: Feature description
            enabled: Whether feature is enabled
            version: Feature version
        """
        self.features[name] = {
            "name": name,
            "description": description,
            "enabled": enabled,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "version": version,
        }

    def enable_feature(self, name: str) -> None:
        """Enable a feature.

        Args:
            name: Feature name
        """
        if name in self.features:
            self.features[name]["enabled"] = True
            self.features[name]["updated_at"] = datetime.utcnow().isoformat()

    def disable_feature(self, name: str) -> None:
        """Disable a feature.

        Args:
            name: Feature name
        """
        if name in self.features:
            self.features[name]["enabled"] = False
            self.features[name]["updated_at"] = datetime.utcnow().isoformat()

    def get_feature(self, name: str) -> Optional[FeatureMetadata]:
        """Get feature metadata.

        Args:
            name: Feature name

        Returns:
            Feature metadata if found
        """
        return self.features.get(name)

    def list_features(self, enabled_only: bool = False) -> List[FeatureMetadata]:
        """List all features.

        Args:
            enabled_only: Only return enabled features

        Returns:
            List of feature metadata
        """
        if enabled_only:
            return [feature for feature in self.features.values() if feature["enabled"]]
        return list(self.features.values())

    def get_enabled_features_for_recipe(self, recipe: Recipe) -> List[FeatureMetadata]:
        """Get enabled features for a recipe.

        Args:
            recipe: Recipe to check features for

        Returns:
            List of enabled feature metadata
        """
        enabled_features = []
        for feature in self.features.values():
            if feature["enabled"]:
                enabled_features.append(feature)
        return enabled_features

    def update_feature_version(self, name: str, version: str) -> None:
        """Update feature version.

        Args:
            name: Feature name
            version: New version
        """
        if name in self.features:
            self.features[name]["version"] = version
            self.features[name]["updated_at"] = datetime.utcnow().isoformat()

    def get_feature_history(self, name: str) -> List[Dict[str, str]]:
        """Get feature version history.

        Args:
            name: Feature name

        Returns:
            List of version history entries
        """
        if name not in self.features:
            return []

        feature = self.features[name]
        return [
            {
                "version": feature["version"],
                "updated_at": feature["updated_at"],
            }
        ]
