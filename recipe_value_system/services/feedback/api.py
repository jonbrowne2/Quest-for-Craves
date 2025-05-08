"""API endpoints for feedback and reward system."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from recipe_value_system.config import SystemConfig
from recipe_value_system.models.feedback import FeedbackStatus, FeedbackType, RewardTier
from recipe_value_system.services.feedback.feedback_service import FeedbackService
from recipe_value_system.utils.auth import (
    get_config,
    get_current_user,
    get_db,
    is_admin,
)
from recipe_value_system.utils.storage import upload_to_storage

router = APIRouter(prefix="/api/v1/feedback")


# Pydantic models for request/response
class FeedbackBase(BaseModel):
    """Base model for feedback submission.

    Attributes:
    - type (FeedbackType): Type of feedback.
    - rating (float): Rating given by the user.
    - comment (Optional[str]): Comment provided by the user.
    - would_make_again (Optional[bool]): Whether the user would make the recipe again.
    - cooking_date (Optional[datetime]): Date when the recipe was cooked.
    - prep_time_actual (Optional[int]): Actual preparation time.
    - cook_time_actual (Optional[int]): Actual cooking time.
    - serving_size_made (Optional[int]): Serving size made by the user.
    - modifications (Optional[Dict[str, Any]]): Modifications made to the recipe.
    - substitutions (Optional[Dict[str, Any]]): Substitutions made to the recipe.
    - taste_rating (Optional[float]): Rating given for the taste.
    - texture_rating (Optional[float]): Rating given for the texture.
    - appearance_rating (Optional[float]): Rating given for the appearance.
    - difficulty_rating (Optional[float]): Rating given for the difficulty.
    - accuracy_rating (Optional[float]): Rating given for the accuracy.
    - ingredient_cost (Optional[float]): Cost of the ingredients.
    - cost_per_serving (Optional[float]): Cost per serving.
    - nutrition_accuracy (Optional[float]): Accuracy of the nutrition information.
    - calories_actual (Optional[int]): Actual calories in the recipe.
    """

    type: FeedbackType = Field(default=FeedbackType.BASIC_REVIEW)
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    would_make_again: Optional[bool] = None
    cooking_date: Optional[datetime] = None
    prep_time_actual: Optional[int] = Field(None, ge=0)
    cook_time_actual: Optional[int] = Field(None, ge=0)
    serving_size_made: Optional[int] = Field(None, ge=1)
    modifications: Optional[Dict[str, Any]] = None
    substitutions: Optional[Dict[str, Any]] = None
    taste_rating: Optional[float] = Field(None, ge=1, le=5)
    texture_rating: Optional[float] = Field(None, ge=1, le=5)
    appearance_rating: Optional[float] = Field(None, ge=1, le=5)
    difficulty_rating: Optional[float] = Field(None, ge=1, le=5)
    accuracy_rating: Optional[float] = Field(None, ge=1, le=5)
    ingredient_cost: Optional[float] = Field(None, ge=0)
    cost_per_serving: Optional[float] = Field(None, ge=0)
    nutrition_accuracy: Optional[float] = Field(None, ge=1, le=5)
    calories_actual: Optional[int] = Field(None, ge=0)


class FeedbackResponse(BaseModel):
    """Response model for feedback submission.

    Attributes:
    - id (int): ID of the feedback.
    - status (FeedbackStatus): Status of the feedback.
    - quality_score (float): Quality score of the feedback.
    - reward_tier (Optional[RewardTier]): Reward tier earned by the user.
    - points_earned (Optional[int]): Points earned by the user.
    - credit_earned (Optional[float]): Credit earned by the user.
    """

    id: int
    status: FeedbackStatus
    quality_score: float
    reward_tier: Optional[RewardTier]
    points_earned: Optional[int]
    credit_earned: Optional[float]


class RewardsSummary(BaseModel):
    """Model for user rewards summary.

    Attributes:
    - points (Dict[str, int]): Points earned by the user.
    - credits (Dict[str, float]): Credits earned by the user.
    - achievements (Dict[str, int]): Achievements unlocked by the user.
    """

    points: Dict[str, int]
    credits: Dict[str, float]
    achievements: Dict[str, int]


class Transaction(BaseModel):
    """Model for wallet transaction.

    Attributes:
    - date (datetime): Date of the transaction.
    - points (Optional[int]): Points involved in the transaction.
    - amount (float): Amount involved in the transaction.
    - description (str): Description of the transaction.
    """

    date: datetime
    points: Optional[int]
    amount: float
    description: str


# API endpoints
@router.post("/{recipe_id}", response_model=FeedbackResponse)
async def submit_feedback(
    recipe_id: int,
    feedback: FeedbackBase,
    user_id: int,  # Would come from auth middleware
    session: Session = Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Submit feedback for a recipe.

    Args:
    - recipe_id (int): ID of the recipe being reviewed.
    - feedback (FeedbackBase): Feedback data.
    - user_id (int): ID of the user submitting feedback.
    - session (Session): Database session.
    - config (SystemConfig): System configuration.

    Returns:
    - FeedbackResponse: Response containing feedback ID, status, quality score, reward tier, points earned, and credit earned.
    """
    service = FeedbackService(session, config)

    try:
        feedback_obj = service.submit_feedback(
            user_id=user_id, recipe_id=recipe_id, feedback_data=feedback.dict()
        )

        reward = feedback_obj.reward
        return {
            "id": feedback_obj.id,
            "status": feedback_obj.status,
            "quality_score": feedback_obj.quality_score,
            "reward_tier": reward.tier if reward else None,
            "points_earned": reward.points_earned if reward else None,
            "credit_earned": float(reward.credit_amount) if reward else None,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{feedback_id}/photos")
async def upload_photos(
    feedback_id: int,
    files: List[UploadFile] = File(...),
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Upload photos for feedback.

    Args:
    - feedback_id (int): ID of the feedback being updated.
    - files (List[UploadFile]): List of photo files to upload.
    - user_id (int): ID of the user uploading photos.
    - session (Session): Database session.
    - config (SystemConfig): System configuration.

    Returns:
    - dict: Response containing a success message.
    """
    service = FeedbackService(session, config)

    try:
        # Verify user owns the feedback
        feedback = service.get_feedback(feedback_id)
        if feedback.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        photo_urls = []
        for file in files:
            if not file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail=f"File {file.filename} is not an image"
                )

            # Upload to storage (implementation needed)
            photo_url = await upload_to_storage(file)
            photo_urls.append(photo_url)

        # Update feedback with photo URLs
        service.add_photos(feedback_id, photo_urls)

        return {"message": "Photos uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rewards", response_model=RewardsSummary)
async def get_rewards(
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Get user's rewards summary.

    Args:
    - user_id (int): ID of the user.
    - session (Session): Database session.
    - config (SystemConfig): System configuration.

    Returns:
    - RewardsSummary: User's rewards summary.
    """
    service = FeedbackService(session, config)
    return service.get_user_rewards_summary(user_id)


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    limit: int = 10,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Get user's recent transactions.

    Args:
    - limit (int): Number of transactions to retrieve.
    - user_id (int): ID of the user.
    - session (Session): Database session.
    - config (SystemConfig): System configuration.

    Returns:
    - List[Transaction]: List of user's recent transactions.
    """
    service = FeedbackService(session, config)
    return service.get_recent_transactions(user_id, limit)


@router.post("/{feedback_id}/verify")
async def verify_feedback(
    feedback_id: int,
    verified: bool,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_db),
    config: SystemConfig = Depends(get_config),
):
    """
    Verify feedback (admin only).

    Args:
    - feedback_id (int): ID of the feedback being verified.
    - verified (bool): Verification status.
    - user_id (int): ID of the user verifying feedback.
    - session (Session): Database session.
    - config (SystemConfig): System configuration.

    Returns:
    - dict: Response containing a success message.
    """
    if not is_admin(user_id):
        raise HTTPException(status_code=403, detail="Admin access required")

    service = FeedbackService(session, config)
    service.verify_feedback(feedback_id, verified)
    return {"message": "Feedback verification updated"}
