"""Feed."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
)
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from recipe_value_system.models.base import Base, SoftDeleteMixin, TimestampMixin


class FeedbackType(str, Enum):
    """Type.

    Key:
        R: ★
        N: ✎
        D: ⚡
        T: ⌛
        F: ⚜
        V: ✧
    """

    RATING = "rating"
    COMMENT = "comment"
    DIFFICULTY = "difficulty"
    TIME = "time"
    TASTE = "taste"
    PRESENTATION = "presentation"


class Feedback(Base, TimestampMixin, SoftDeleteMixin):
    """Log.

    Data.

    Col:
        id: #
        by: @
        on: &
        is: ?
        r: ★
        d: ⚡
        p: ⌛
        c: ⌚
        n: ✎
        t: ⏰
        u: ⌚
    """

    __tablename__ = "user_feedback"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id: int = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    type: FeedbackType = Column(SQLAEnum(FeedbackType), nullable=False)

    # Ratings and metrics
    rating: float = Column(Float)
    difficulty_rating: float = Column(Float)
    prep_time: float = Column(Numeric(10, 2))
    cook_time: float = Column(Numeric(10, 2))

    # Additional feedback
    comment: str = Column(Text)
    metadata: Dict[str, Any] = Column(JSON)
    metrics: Dict[str, Any] = Column(JSON)

    # Relationships
    user = relationship("User", back_populates="feedback")
    recipe = relationship("Recipe", back_populates="feedback")

    def __repr__(self) -> str:
        """Get string representation of the feedback.

        Returns:
            String representation including user, recipe, and rating.
        """
        return (
            f"<Feedback(user_id={self.user_id}, "
            f"recipe_id={self.recipe_id}, rating={self.rating})>"
        )


class FeedbackReward(Base, TimestampMixin):
    """Model for tracking feedback rewards.

    This model stores information about rewards earned by users for providing feedback.

    Attributes:
        id: Unique identifier for the reward
        feedback_id: ID of the feedback that earned the reward
        tier: Tier of the reward
        points_earned: Points earned by the user
        credit_amount: Amount in USD earned by the user
        redeemed: Whether the reward has been redeemed
        redeemed_at: Date the reward was redeemed
    """

    __tablename__ = "feedback_rewards"

    id: int = Column(Integer, primary_key=True)
    feedback_id: int = Column(Integer, ForeignKey("user_feedback.id"), nullable=False)
    tier: str = Column(String(50), nullable=False)
    points_earned: int = Column(Integer, nullable=False)
    credit_amount: float = Column(Numeric(10, 2), nullable=False)  # Amount in USD
    redeemed: bool = Column(Boolean, default=False)
    redeemed_at: datetime = Column(DateTime)

    # Relationships
    feedback = relationship("Feedback", back_populates="reward")


class UserWallet(Base, TimestampMixin):
    """Model for tracking user rewards and credits.

    This model stores information about user rewards and credits.

    Attributes:
        id: Unique identifier for the wallet
        user_id: ID of the user who owns the wallet
        total_points: Total points earned by the user
        available_points: Points available for redemption
        lifetime_points: Total points earned by the user in their lifetime
        available_credit: Amount in USD available for redemption
        pending_credit: Amount in USD pending redemption
        lifetime_credit: Total amount in USD earned by the user in their lifetime
        feedback_count: Number of feedback provided by the user
        featured_count: Number of feedback featured on the site
        photo_count: Number of photos uploaded by the user
    """

    __tablename__ = "user_wallets"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Point system
    total_points: int = Column(Integer, default=0)
    available_points: int = Column(Integer, default=0)
    lifetime_points: int = Column(Integer, default=0)

    # Credit system
    available_credit: float = Column(Numeric(10, 2), default=0)  # Amount in USD
    pending_credit: float = Column(
        Numeric(10, 2), default=0
    )  # Rewards not yet redeemable
    lifetime_credit: float = Column(Numeric(10, 2), default=0)

    # Achievement tracking
    feedback_count: int = Column(Integer, default=0)
    featured_count: int = Column(Integer, default=0)
    photo_count: int = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base, TimestampMixin):
    """Model for tracking wallet transactions.

    This model stores information about transactions made on the user's wallet.

    Attributes:
        id: Unique identifier for the transaction
        wallet_id: ID of the wallet that the transaction was made on
        amount: Amount in USD of the transaction
        points: Points involved in the transaction
        description: Description of the transaction
        reference_id: Reference to the related entity (e.g., feedback_id)
    """

    __tablename__ = "wallet_transactions"

    id: int = Column(Integer, primary_key=True)
    wallet_id: int = Column(Integer, ForeignKey("user_wallets.id"), nullable=False)

    # Transaction details
    amount: float = Column(
        Numeric(10, 2), nullable=False
    )  # Can be positive or negative
    points: int = Column(Integer)  # Points involved in transaction
    description: str = Column(String(200))
    reference_id: str = Column(
        String(50)
    )  # Reference to related entity (e.g., feedback_id)

    # Relationships
    wallet = relationship("UserWallet", back_populates="transactions")
