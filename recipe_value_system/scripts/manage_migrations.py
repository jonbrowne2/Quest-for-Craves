"""Type-safe migration management script."""

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import alembic.config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, text

from ..config.settings import settings


@dataclass
class MigrationStatus:
    """Migration status information."""

    revision: str
    is_head: bool
    is_applied: bool
    applied_at: Optional[datetime] = None


@dataclass
class MigrationResult:
    """Migration operation result."""

    success: bool
    revision: str
    operation: str
    error: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class MigrationManager:
    """Type-safe migration management."""

    def __init__(self) -> None:
        """Initialize migration manager."""
        self.engine = create_engine(str(settings.database.url))
        self.migrations_dir = Path(__file__).parent.parent / "migrations"

    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        with self.engine.connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()

    def get_migration_status(self) -> List[MigrationStatus]:
        """Get status of all migrations."""
        from alembic.script import ScriptDirectory

        # Get migration script directory
        config = alembic.config.Config()
        config.set_main_option("script_location", str(self.migrations_dir))
        script = ScriptDirectory.from_config(config)

        # Get current revision
        current = self.get_current_revision()

        # Get all revisions
        statuses: List[MigrationStatus] = []
        for rev in script.walk_revisions():
            status = MigrationStatus(
                revision=rev.revision,
                is_head=rev.is_head,
                is_applied=current and rev.revision <= current,
            )

            # Get applied timestamp if available
            if status.is_applied:
                with self.engine.connect() as conn:
                    result = conn.execute(
                        text(
                            "SELECT applied_at FROM alembic_version_history "
                            "WHERE version_num = :version"
                        ),
                        {"version": rev.revision},
                    ).first()
                    if result:
                        status.applied_at = result[0]

            statuses.append(status)

        return statuses

    def create_migration(self, message: str) -> MigrationResult:
        """Create new migration."""
        try:
            # Create alembic config
            config = alembic.config.Config()
            config.set_main_option("script_location", str(self.migrations_dir))

            # Create revision
            from alembic.command import revision

            revision(config, message, autogenerate=True)

            return MigrationResult(success=True, revision="head", operation="create")
        except Exception as e:
            return MigrationResult(
                success=False, revision="head", operation="create", error=str(e)
            )

    def upgrade(self, target: str = "head") -> MigrationResult:
        """Upgrade database to target revision."""
        try:
            # Create alembic config
            config = alembic.config.Config()
            config.set_main_option("script_location", str(self.migrations_dir))

            # Run upgrade
            from alembic.command import upgrade

            upgrade(config, target)

            return MigrationResult(success=True, revision=target, operation="upgrade")
        except Exception as e:
            return MigrationResult(
                success=False, revision=target, operation="upgrade", error=str(e)
            )

    def downgrade(self, target: str) -> MigrationResult:
        """Downgrade database to target revision."""
        try:
            # Create alembic config
            config = alembic.config.Config()
            config.set_main_option("script_location", str(self.migrations_dir))

            # Run downgrade
            from alembic.command import downgrade

            downgrade(config, target)

            return MigrationResult(success=True, revision=target, operation="downgrade")
        except Exception as e:
            return MigrationResult(
                success=False, revision=target, operation="downgrade", error=str(e)
            )


def main() -> None:
    """Main entry point for migration management."""
    parser = argparse.ArgumentParser(description="Manage database migrations")
    parser.add_argument(
        "action",
        choices=["create", "status", "upgrade", "downgrade"],
        help="Action to perform",
    )
    parser.add_argument("--message", "-m", help="Migration message (for create)")
    parser.add_argument(
        "--revision",
        "-r",
        default="head",
        help="Target revision (for upgrade/downgrade)",
    )

    args = parser.parse_args()
    manager = MigrationManager()

    if args.action == "create":
        if not args.message:
            print("Error: Message required for create")
            return
        result = manager.create_migration(args.message)
        if result.success:
            print(f"Created migration {result.revision}")
        else:
            print(f"Error creating migration: {result.error}")

    elif args.action == "status":
        current = manager.get_current_revision()
        print(f"Current revision: {current}")

        statuses = manager.get_migration_status()
        for status in statuses:
            applied = "✓" if status.is_applied else " "
            head = "HEAD" if status.is_head else "    "
            date = (
                status.applied_at.strftime("%Y-%m-%d %H:%M:%S")
                if status.applied_at
                else "Not applied"
            )
            print(f"[{applied}] {status.revision} {head} - {date}")

    elif args.action == "upgrade":
        result = manager.upgrade(args.revision)
        if result.success:
            print(f"Upgraded to {result.revision}")
        else:
            print(f"Error upgrading: {result.error}")

    elif args.action == "downgrade":
        result = manager.downgrade(args.revision)
        if result.success:
            print(f"Downgraded to {result.revision}")
        else:
            print(f"Error downgrading: {result.error}")


if __name__ == "__main__":
    main()
