"""Command-line interface for exporting recipe data."""

import os
from datetime import datetime
from pathlib import Path

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from recipe_value_system.config import SystemConfig
from recipe_value_system.services.export.data_exporter import DataExporter


@click.group()
def cli():
    """Recipe Value System Data Export CLI"""
    pass


def get_session():
    """Create database session."""
    config = SystemConfig()
    engine = create_engine(config.db.URL)
    Session = sessionmaker(bind=engine)
    return Session()


@cli.command()
@click.option("--cuisine", help="Filter by cuisine type")
@click.option("--min-rating", type=float, help="Filter by minimum rating")
@click.option("--max-difficulty", type=float, help="Filter by maximum difficulty")
@click.option(
    "--format",
    type=click.Choice(["all", "json", "csv", "parquet", "excel", "pickle"]),
    default="all",
    help="Export format",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default="exports",
    help="Output directory for exported files",
)
def export_recipes(cuisine, min_rating, max_difficulty, format, output_dir):
    """Export recipe data with optional filters."""
    try:
        session = get_session()
        exporter = DataExporter(session, Path(output_dir))

        filters = {}
        if cuisine:
            filters["cuisine_type"] = cuisine
        if min_rating:
            filters["community_rating"] = min_rating
        if max_difficulty:
            filters["difficulty_score"] = max_difficulty

        paths = exporter.export_recipes(filters)

        if format == "all":
            for fmt, path in paths.items():
                click.echo(f"Exported {fmt} to: {path}")
        else:
            click.echo(f"Exported {format} to: {paths[format]}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.option(
    "--start-date",
    type=click.DateTime(),
    help="Start date for interaction data (YYYY-MM-DD)",
)
@click.option(
    "--end-date",
    type=click.DateTime(),
    help="End date for interaction data (YYYY-MM-DD)",
)
@click.option(
    "--format",
    type=click.Choice(["all", "json", "csv", "parquet", "excel", "pickle"]),
    default="all",
    help="Export format",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default="exports",
    help="Output directory for exported files",
)
def export_interactions(start_date, end_date, format, output_dir):
    """Export user interaction data within date range."""
    try:
        session = get_session()
        exporter = DataExporter(session, Path(output_dir))

        paths = exporter.export_user_interactions(start_date, end_date)

        if format == "all":
            for fmt, path in paths.items():
                click.echo(f"Exported {fmt} to: {path}")
        else:
            click.echo(f"Exported {format} to: {paths[format]}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


@cli.command()
@click.option(
    "--output-dir",
    type=click.Path(),
    default="exports",
    help="Output directory for exported files",
)
def export_all(output_dir):
    """Export all data in all formats."""
    try:
        session = get_session()
        exporter = DataExporter(session, Path(output_dir))

        # Export recipes
        recipe_paths = exporter.export_recipes()
        click.echo("Recipe exports:")
        for fmt, path in recipe_paths.items():
            click.echo(f"  {fmt}: {path}")

        # Export interactions
        interaction_paths = exporter.export_user_interactions()
        click.echo("\nInteraction exports:")
        for fmt, path in interaction_paths.items():
            click.echo(f"  {fmt}: {path}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)


if __name__ == "__main__":
    cli()
