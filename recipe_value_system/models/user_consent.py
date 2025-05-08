"""User consent model for data privacy."""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    UniqueConstraint,
)

from recipe_value_system.models.base import Base, TimestampMixin


class ConsentType(Enum):
    """Types of consent a user can give."""

    RECIPE_PREFERENCES = "recipe_preferences"  # Share recipe preferences
    COOKING_HISTORY = "cooking_history"  # Share cooking history
    DIETARY_INFO = "dietary_info"  # Share dietary information
    USAGE_ANALYTICS = "usage_analytics"  # Share usage analytics


class UserConsent(Base, TimestampMixin):
    """Model for tracking user consent and privacy preferences.

    Stores user consent records and privacy settings.
    Used for GDPR compliance and data protection.

    Attributes:
        id: Unique identifier
        user_id: Associated user ID
        consent_type: Type of consent
        is_granted: Whether consent is granted
        last_updated: When consent was last updated
        consent_details: Detailed consent information
    """

    __tablename__ = "user_consents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consent_type = Column(Enum(ConsentType), nullable=False)
    is_granted = Column(Boolean, default=False)
    last_updated = Column(DateTime, nullable=False)

    # Additional metadata about the consent
    consent_details = Column(
        JSON
    )  # Store version of consent, specific allowances, etc.

    __table_args__ = (
        # Composite unique constraint
        UniqueConstraint("user_id", "consent_type", name="uix_user_consent_type"),
    )
