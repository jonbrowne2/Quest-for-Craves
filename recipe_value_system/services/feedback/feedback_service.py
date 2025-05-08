"""Service for managing user feedback and rewards."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from recipe_value_system.config import SystemConfig
from recipe_value_system.models.feedback import (
    FeedbackReward,
    FeedbackStatus,
    FeedbackType,
    RewardTier,
    UserFeedback,
    UserWallet,
    WalletTransaction,
)


@dataclass
class RewardConfig:
    """Reward tier configuration."""

    min_quality: float
    points: int
    credit: Decimal


@dataclass
class FeedbackData:
    """Feedback submission data."""

    type: FeedbackType = FeedbackType.BASIC_REVIEW
    rating: Optional[int] = None
    comment: Optional[str] = None
    would_make_again: Optional[bool] = None
    cooking_date: Optional[datetime] = None
    prep_time_actual: Optional[int] = None
    cook_time_actual: Optional[int] = None
    serving_size_made: Optional[int] = None
    modifications: Optional[Dict] = None
    substitutions: Optional[Dict] = None
    taste_rating: Optional[int] = None
    texture_rating: Optional[int] = None
    appearance_rating: Optional[int] = None
    difficulty_rating: Optional[int] = None
    accuracy_rating: Optional[int] = None
    photo_urls: Optional[List[str]] = None
    ingredient_cost: Optional[Decimal] = None
    cost_per_serving: Optional[Decimal] = None
    nutrition_accuracy: Optional[float] = None
    calories_actual: Optional[int] = None


class FeedbackService:
    """Service for handling feedback operations."""

    def __init__(self, session: Session, config: SystemConfig) -> None:
        """Initialize feedback service."""
        self.session = session
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.reward_tiers: Dict[RewardTier, RewardConfig] = {
            RewardTier.BRONZE: RewardConfig(
                min_quality=0.3,
                points=50,
                credit=Decimal("1.00"),
            ),
            RewardTier.SILVER: RewardConfig(
                min_quality=0.5,
                points=100,
                credit=Decimal("2.00"),
            ),
            RewardTier.GOLD: RewardConfig(
                min_quality=0.7,
                points=200,
                credit=Decimal("5.00"),
            ),
            RewardTier.PLATINUM: RewardConfig(
                min_quality=0.9,
                points=500,
                credit=Decimal("10.00"),
            ),
        }

    def submit_feedback(
        self, user_id: int, recipe_id: int, feedback_data: Dict
    ) -> UserFeedback:
        """Submit new feedback for a recipe."""
        try:
            data = FeedbackData(**feedback_data)

            feedback = UserFeedback(
                user_id=user_id,
                recipe_id=recipe_id,
                feedback_type=data.type,
                rating=data.rating,
                comment=data.comment,
                would_make_again=data.would_make_again,
                cooking_date=data.cooking_date,
                prep_time_actual=data.prep_time_actual,
                cook_time_actual=data.cook_time_actual,
                serving_size_made=data.serving_size_made,
                modifications=data.modifications,
                substitutions=data.substitutions,
                taste_rating=data.taste_rating,
                texture_rating=data.texture_rating,
                appearance_rating=data.appearance_rating,
                difficulty_rating=data.difficulty_rating,
                accuracy_rating=data.accuracy_rating,
                photo_urls=data.photo_urls,
                ingredient_cost=data.ingredient_cost,
                cost_per_serving=data.cost_per_serving,
                nutrition_accuracy=data.nutrition_accuracy,
                calories_actual=data.calories_actual,
            )

            feedback.quality_score = feedback.calculate_quality_score()
            self.session.add(feedback)
            self.session.flush()

            self._process_feedback_reward(feedback)
            self.session.commit()

            self.logger.info(f"Feedback submitted successfully: {feedback.id}")
            return feedback

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error submitting feedback: {str(e)}")
            raise

    def _process_feedback_reward(self, feedback: UserFeedback) -> None:
        """Process rewards for submitted feedback."""
        tier = self._determine_reward_tier(feedback.quality_score)
        if not tier:
            return

        reward_config = self.reward_tiers[tier]

        reward = FeedbackReward(
            feedback_id=feedback.id,
            tier=tier,
            points_earned=reward_config.points,
            credit_amount=reward_config.credit,
        )
        self.session.add(reward)

        wallet = self._get_or_create_wallet(feedback.user_id)
        wallet.total_points += reward_config.points
        wallet.available_points += reward_config.points
        wallet.lifetime_points += reward_config.points
        wallet.pending_credit += reward_config.credit

        self._create_wallet_transaction(
            wallet.id,
            reward_config.points,
            reward_config.credit,
            f"Feedback reward for recipe {feedback.recipe_id}",
            str(feedback.id),
        )

        wallet.feedback_count += 1
        if feedback.photo_urls:
            wallet.photo_count += len(feedback.photo_urls)

    def _determine_reward_tier(self, quality_score: float) -> Optional[RewardTier]:
        """Determine reward tier based on feedback quality score."""
        for tier in reversed(list(RewardTier)):
            if quality_score >= self.reward_tiers[tier].min_quality:
                return tier
        return None

    def _get_or_create_wallet(self, user_id: int) -> UserWallet:
        """Get or create user wallet."""
        wallet = self.session.query(UserWallet).filter_by(user_id=user_id).first()
        if not wallet:
            wallet = UserWallet(user_id=user_id)
            self.session.add(wallet)
        return wallet

    def _create_wallet_transaction(
        self,
        wallet_id: int,
        points: int,
        credit: Decimal,
        description: str,
        reference: str,
    ) -> WalletTransaction:
        """Create a new wallet transaction."""
        transaction = WalletTransaction(
            wallet_id=wallet_id,
            points=points,
            amount=credit,
            description=description,
            reference_id=reference,
        )
        self.session.add(transaction)
        return transaction

    def verify_feedback(self, feedback_id: int, verified: bool = True) -> None:
        """Verify feedback and release rewards."""
        try:
            feedback = self.session.query(UserFeedback).get(feedback_id)
            if not feedback:
                raise ValueError(f"Feedback not found: {feedback_id}")

            if verified:
                feedback.status = FeedbackStatus.VERIFIED

                wallet = self._get_or_create_wallet(feedback.user_id)
                reward = feedback.reward
                if reward and not reward.redeemed:
                    wallet.available_credit += reward.credit_amount
                    wallet.pending_credit -= reward.credit_amount

            else:
                feedback.status = FeedbackStatus.REJECTED

                wallet = self._get_or_create_wallet(feedback.user_id)
                reward = feedback.reward
                if reward and not reward.redeemed:
                    wallet.total_points -= reward.points_earned
                    wallet.available_points -= reward.points_earned
                    wallet.pending_credit -= reward.credit_amount

            self.session.commit()
            self.logger.info(f"Feedback {feedback_id} verified: {verified}")

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error verifying feedback: {str(e)}")
            raise

    def get_user_rewards_summary(self, user_id: int) -> Dict[str, float]:
        """Get summary of user's rewards and credits."""
        wallet = self._get_or_create_wallet(user_id)

        return {
            "points": {
                "available": wallet.available_points,
                "total": wallet.total_points,
                "lifetime": wallet.lifetime_points,
            },
            "credits": {
                "available": float(wallet.available_credit),
                "pending": float(wallet.pending_credit),
                "lifetime": float(wallet.lifetime_credit),
            },
            "achievements": {
                "feedback_count": wallet.feedback_count,
                "featured_count": wallet.featured_count,
                "photo_count": wallet.photo_count,
            },
        }

    def get_recent_transactions(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, float]]:
        """Get user's recent wallet transactions."""
        wallet = self._get_or_create_wallet(user_id)

        transactions = (
            self.session.query(WalletTransaction)
            .filter(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "date": tx.created_at,
                "points": tx.points,
                "amount": float(tx.amount),
                "description": tx.description,
            }
            for tx in transactions
        ]
