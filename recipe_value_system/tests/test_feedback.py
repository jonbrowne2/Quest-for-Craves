"""Tests for feedback and reward system."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from recipe_value_system.models.feedback import (
    FeedbackReward,
    FeedbackStatus,
    FeedbackType,
    RewardTier,
    UserFeedback,
    UserWallet,
    WalletTransaction,
)
from recipe_value_system.services.feedback.feedback_service import FeedbackService


@pytest.fixture
def feedback_service(db_session, config):
    """Create feedback service instance."""
    return FeedbackService(db_session, config)


@pytest.fixture
def basic_feedback_data():
    """Create basic feedback data."""
    return {
        "type": FeedbackType.BASIC_REVIEW,
        "rating": 4.5,
        "comment": "Great recipe!",
        "would_make_again": True,
    }


@pytest.fixture
def detailed_feedback_data():
    """Create detailed feedback data with photos."""
    return {
        "type": FeedbackType.DETAILED_REVIEW,
        "rating": 4.5,
        "comment": "This recipe was amazing! I made it for dinner and everyone loved it.",
        "would_make_again": True,
        "cooking_date": datetime.utcnow(),
        "prep_time_actual": 20,
        "cook_time_actual": 35,
        "serving_size_made": 4,
        "taste_rating": 5.0,
        "texture_rating": 4.5,
        "appearance_rating": 4.0,
        "difficulty_rating": 3.0,
        "accuracy_rating": 4.5,
        "photo_urls": [
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg",
        ],
        "ingredient_cost": 25.50,
        "cost_per_serving": 6.38,
    }


def test_submit_basic_feedback(feedback_service, sample_recipe, basic_feedback_data):
    """Test submitting basic feedback."""
    feedback = feedback_service.submit_feedback(
        user_id=1, recipe_id=sample_recipe.id, feedback_data=basic_feedback_data
    )

    assert feedback.id is not None
    assert feedback.rating == 4.5
    assert feedback.status == FeedbackStatus.PENDING
    assert feedback.quality_score > 0

    # Check reward
    assert feedback.reward is not None
    assert feedback.reward.tier == RewardTier.BRONZE
    assert feedback.reward.points_earned == 50
    assert feedback.reward.credit_amount == Decimal("1.00")


def test_submit_detailed_feedback(
    feedback_service, sample_recipe, detailed_feedback_data
):
    """Test submitting detailed feedback with photos."""
    feedback = feedback_service.submit_feedback(
        user_id=1, recipe_id=sample_recipe.id, feedback_data=detailed_feedback_data
    )

    assert feedback.id is not None
    assert feedback.quality_score > 0.7  # Should be Gold tier or higher

    # Check reward
    assert feedback.reward is not None
    assert feedback.reward.tier in [RewardTier.GOLD, RewardTier.PLATINUM]
    assert feedback.reward.points_earned >= 200
    assert feedback.reward.credit_amount >= Decimal("5.00")


def test_wallet_creation(feedback_service, sample_recipe, basic_feedback_data):
    """Test wallet creation and update."""
    # Submit feedback
    feedback = feedback_service.submit_feedback(
        user_id=1, recipe_id=sample_recipe.id, feedback_data=basic_feedback_data
    )

    # Check wallet
    wallet = feedback_service._get_or_create_wallet(1)
    assert wallet.total_points == feedback.reward.points_earned
    assert wallet.available_points == feedback.reward.points_earned
    assert wallet.pending_credit == feedback.reward.credit_amount
    assert wallet.available_credit == 0  # Credit pending verification
    assert wallet.feedback_count == 1


def test_feedback_verification(feedback_service, sample_recipe, basic_feedback_data):
    """Test feedback verification process."""
    # Submit feedback
    feedback = feedback_service.submit_feedback(
        user_id=1, recipe_id=sample_recipe.id, feedback_data=basic_feedback_data
    )

    initial_wallet = feedback_service._get_or_create_wallet(1)
    initial_pending = initial_wallet.pending_credit

    # Verify feedback
    feedback_service.verify_feedback(feedback.id, verified=True)

    # Check wallet updates
    wallet = feedback_service._get_or_create_wallet(1)
    assert wallet.available_credit == initial_pending
    assert wallet.pending_credit == 0


def test_feedback_rejection(feedback_service, sample_recipe, basic_feedback_data):
    """Test feedback rejection process."""
    # Submit feedback
    feedback = feedback_service.submit_feedback(
        user_id=1, recipe_id=sample_recipe.id, feedback_data=basic_feedback_data
    )

    initial_wallet = feedback_service._get_or_create_wallet(1)
    initial_points = initial_wallet.total_points

    # Reject feedback
    feedback_service.verify_feedback(feedback.id, verified=False)

    # Check wallet updates
    wallet = feedback_service._get_or_create_wallet(1)
    assert wallet.total_points == 0
    assert wallet.available_points == 0
    assert wallet.pending_credit == 0
    assert feedback.status == FeedbackStatus.REJECTED


def test_multiple_feedback_rewards(feedback_service, sample_recipe):
    """Test accumulating rewards from multiple feedback submissions."""
    user_id = 1

    # Submit basic feedback
    feedback1 = feedback_service.submit_feedback(
        user_id=user_id,
        recipe_id=sample_recipe.id,
        feedback_data={"rating": 4.0, "comment": "Good"},
    )

    # Submit detailed feedback
    feedback2 = feedback_service.submit_feedback(
        user_id=user_id,
        recipe_id=sample_recipe.id + 1,
        feedback_data=detailed_feedback_data(),
    )

    # Check wallet totals
    wallet = feedback_service._get_or_create_wallet(user_id)
    assert wallet.total_points == (
        feedback1.reward.points_earned + feedback2.reward.points_earned
    )
    assert wallet.pending_credit == (
        feedback1.reward.credit_amount + feedback2.reward.credit_amount
    )
    assert wallet.feedback_count == 2


def test_reward_tiers(feedback_service, sample_recipe):
    """Test different reward tiers based on feedback quality."""
    test_cases = [
        # Basic feedback (Bronze)
        {"data": {"rating": 4.0}, "expected_tier": RewardTier.BRONZE},
        # Better feedback (Silver)
        {
            "data": {
                "rating": 4.0,
                "comment": "Detailed comment about the recipe...",
                "would_make_again": True,
            },
            "expected_tier": RewardTier.SILVER,
        },
        # Detailed feedback (Gold)
        {"data": detailed_feedback_data(), "expected_tier": RewardTier.GOLD},
    ]

    for case in test_cases:
        feedback = feedback_service.submit_feedback(
            user_id=1, recipe_id=sample_recipe.id, feedback_data=case["data"]
        )
        assert feedback.reward.tier == case["expected_tier"]


def test_transaction_history(feedback_service, sample_recipe, detailed_feedback_data):
    """Test transaction history recording."""
    user_id = 1

    # Submit feedback
    feedback = feedback_service.submit_feedback(
        user_id=user_id,
        recipe_id=sample_recipe.id,
        feedback_data=detailed_feedback_data,
    )

    # Get transactions
    transactions = feedback_service.get_recent_transactions(user_id)
    assert len(transactions) == 1
    assert transactions[0]["points"] == feedback.reward.points_earned
    assert transactions[0]["amount"] == float(feedback.reward.credit_amount)
