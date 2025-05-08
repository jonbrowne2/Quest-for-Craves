"""Scheduler module for analytics jobs."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ...config.analytics_config import AnalyticsConfig
from ...models.recipe import Recipe
from ..analytics_service import AnalyticsService


class JobScheduler:
    """Scheduler for analytics jobs."""

    def __init__(
        self,
        session: Session,
        config: Optional[AnalyticsConfig] = None,
    ) -> None:
        """Initialize job scheduler.

        Args:
            session: Database session
            config: Optional analytics configuration

        Raises:
            TypeError: If session or config is of incorrect type
        """
        if not isinstance(session, Session):
            raise TypeError("Session must be of type Session")
        if config and not isinstance(config, AnalyticsConfig):
            raise TypeError("Config must be of type AnalyticsConfig or None")

        self.session = session
        self.config = config or AnalyticsConfig()
        self.analytics_service = AnalyticsService(session, config)
        self.jobs: Dict[str, datetime] = {}

    def schedule_job(
        self,
        job_id: str,
        interval: timedelta,
        recipes: Optional[List[Recipe]] = None,
    ) -> None:
        """Schedule an analytics job.

        Args:
            job_id: Unique identifier for the job
            interval: Time interval between job runs
            recipes: Optional list of recipes to analyze

        Raises:
            TypeError: If job_id is not str or interval is not timedelta
            ValueError: If job_id is empty or interval is negative
        """
        if not isinstance(job_id, str):
            raise TypeError("Job ID must be a string")
        if not isinstance(interval, timedelta):
            raise TypeError("Interval must be a timedelta")
        if not job_id:
            raise ValueError("Job ID cannot be empty")
        if interval.total_seconds() <= 0:
            raise ValueError("Interval must be positive")

        self.jobs[job_id] = datetime.now() + interval

    def get_pending_jobs(self) -> List[str]:
        """Get list of jobs that are due to run.

        Returns:
            List of job IDs that are due to run
        """
        now = datetime.now()
        return [job_id for job_id, due in self.jobs.items() if due <= now]

    def run_pending_jobs(self) -> Dict[str, Dict[str, float]]:
        """Run all pending jobs.

        Returns:
            Dictionary mapping job IDs to their results
        """
        pending = self.get_pending_jobs()
        results: Dict[str, Dict[str, float]] = {}

        for job_id in pending:
            recipes = self.session.query(Recipe).all()
            metrics: Dict[str, float] = {
                "total_recipes": len(recipes),
                "avg_quality": 0.0,
                "avg_complexity": 0.0,
                "avg_time_value": 0.0,
                "last_run": datetime.now().timestamp(),
            }

            for recipe in recipes:
                recipe_metrics = self.analytics_service.generate_value_metrics(recipe)
                metrics["avg_quality"] += recipe_metrics["quality_score"]
                metrics["avg_complexity"] += recipe_metrics["complexity_score"]
                metrics["avg_time_value"] += recipe_metrics["time_value_score"]

            if recipes:
                metrics["avg_quality"] /= len(recipes)
                metrics["avg_complexity"] /= len(recipes)
                metrics["avg_time_value"] /= len(recipes)

            results[job_id] = metrics

        return results
