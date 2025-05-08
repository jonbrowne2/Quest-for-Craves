"""Data exporter for various formats.

This module handles the exporting of data to different formats.

Classes:
    DataExporter: Service for exporting recipe and user interaction data in various formats.

Functions:
    export_all_formats: Export data in all supported formats.
    export_recipes: Export recipe data with optional filters.
    export_user_interactions: Export user interaction data within date range.

FastAPI Endpoints:
    /api/export/recipes: Export recipes with optional filters.
    /api/export/interactions: Export user interactions within date range.
"""

import csv
import json
import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    TypedDict,
    Union,
    cast,
)

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import xlsxwriter
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session


class DataExporter:
    """Service for exporting recipe and user interaction data in various formats.

    Attributes:
        session: SQLAlchemy session for database access
        export_dir: Directory where exported files will be saved
        logger: Logger instance for logging events
        csv_dir: Directory for CSV exports
        json_dir: Directory for JSON exports
        parquet_dir: Directory for Parquet exports
        excel_dir: Directory for Excel exports
        pickle_dir: Directory for Pickle exports
    """

    def __init__(self, session: Session, export_dir: Union[str, Path]):
        """
        Initialize the DataExporter service.

        Args:
            session: SQLAlchemy session for database access
            export_dir: Directory where exported files will be saved
        """
        self.session = session
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Create subdirectories for different export types
        self.csv_dir: Path = self.export_dir / "csv"
        self.json_dir: Path = self.export_dir / "json"
        self.parquet_dir: Path = self.export_dir / "parquet"
        self.excel_dir: Path = self.export_dir / "excel"
        self.pickle_dir: Path = self.export_dir / "pickle"

        for dir_path in [
            self.csv_dir,
            self.json_dir,
            self.parquet_dir,
            self.excel_dir,
            self.pickle_dir,
        ]:
            dir_path.mkdir(exist_ok=True)

    def export_all_formats(
        self, dataset_name: str, data: List[Dict[str, Any]]
    ) -> Dict[str, Path]:
        """
        Export data in all supported formats.

        Args:
            dataset_name: Name of the dataset being exported
            data: List of dictionaries containing the data to export

        Returns:
            Dict[str, Path]: Dictionary mapping format names to export file paths

        Raises:
            Exception: If any export operation fails
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            export_paths: Dict[str, Path] = {}

            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(data)

            # Export to CSV
            csv_path = self.csv_dir / f"{dataset_name}_{timestamp}.csv"
            df.to_csv(csv_path, index=False)
            export_paths["csv"] = csv_path

            # Export to JSON
            json_path = self.json_dir / f"{dataset_name}_{timestamp}.json"
            with open(json_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
            export_paths["json"] = json_path

            # Export to Parquet
            parquet_path = self.parquet_dir / f"{dataset_name}_{timestamp}.parquet"
            table = pa.Table.from_pandas(df)
            pq.write_table(table, parquet_path)
            export_paths["parquet"] = parquet_path

            # Export to Excel with formatting
            excel_path = self.excel_dir / f"{dataset_name}_{timestamp}.xlsx"
            self._export_to_excel(df, excel_path, dataset_name)
            export_paths["excel"] = excel_path

            # Export to Pickle
            pickle_path = self.pickle_dir / f"{dataset_name}_{timestamp}.pkl"
            with open(pickle_path, "wb") as f:
                pickle.dump(data, f)
            export_paths["pickle"] = pickle_path

            self.logger.info(f"Successfully exported {dataset_name} to all formats")
            return export_paths

        except Exception as e:
            self.logger.error(f"Error exporting {dataset_name}: {str(e)}")
            raise

    def _export_to_excel(self, df: pd.DataFrame, path: Path, sheet_name: str) -> None:
        """
        Export to Excel with formatting and multiple sheets.

        Args:
            df: DataFrame to export
            path: Path where the Excel file will be saved
            sheet_name: Name of the main sheet
        """
        with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
            # Write main data
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Get workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Add formats
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "bg_color": "#D9EAD3",
                    "border": 1,
                }
            )

            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(str(col)))
                worksheet.set_column(i, i, min(max_length + 2, 50))

            # Add filters
            worksheet.autofilter(0, 0, len(df), len(df.columns) - 1)

            # Freeze top row
            worksheet.freeze_panes(1, 0)

            # Add summary sheet
            summary_df = pd.DataFrame(
                [
                    {"Metric": "Total Rows", "Value": len(df)},
                    {"Metric": "Total Columns", "Value": len(df.columns)},
                    {
                        "Metric": "Export Date",
                        "Value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    {"Metric": "File Path", "Value": str(path)},
                ]
            )
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

    def export_recipes(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Path]:
        """
        Export recipe data with optional filters.

        Args:
            filters: Optional dictionary of column:value filters

        Returns:
            Dict[str, Path]: Dictionary mapping format names to export file paths
        """
        query = """
            SELECT
                r.id,
                r.title,
                r.slug,
                r.source_url,
                r.cuisine_type,
                r.ingredients,
                r.instructions,
                r.serving_size,
                r.prep_time,
                r.cook_time,
                r.total_time,
                r.calories_per_serving,
                r.macronutrients,
                r.micronutrients,
                r.difficulty_score,
                r.complexity_score,
                r.estimated_cost,
                r.seasonal_score,
                r.sustainability_score,
                r.community_rating,
                r.review_count,
                r.favorite_count,
                r.created_at,
                r.updated_at
            FROM recipes r
            WHERE r.is_deleted = FALSE
        """

        if filters:
            conditions = []
            params = {}
            for key, value in filters.items():
                conditions.append(f"r.{key} = :{key}")
                params[key] = value
            if conditions:
                query += " AND " + " AND ".join(conditions)

            result = self.session.execute(text(query), params)
        else:
            result = self.session.execute(text(query))

        recipes = [dict(row) for row in result]
        return self.export_all_formats("recipes", recipes)

    def export_user_interactions(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Path]:
        """
        Export user interaction data within date range.

        Args:
            start_date: Optional start date for filtering interactions
            end_date: Optional end date for filtering interactions

        Returns:
            Dict[str, Path]: Dictionary mapping format names to export file paths
        """
        query = """
            SELECT
                ui.id,
                ui.user_id,
                ui.recipe_id,
                ui.interaction_type,
                ui.rating,
                ui.cooking_time_actual,
                ui.difficulty_reported,
                ui.notes,
                ui.created_at
            FROM user_interactions ui
            WHERE 1=1
        """

        params: Dict[str, Any] = {}
        if start_date:
            query += " AND ui.created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND ui.created_at <= :end_date"
            params["end_date"] = end_date

        result = self.session.execute(text(query), params)
        interactions = [dict(row) for row in result]
        return self.export_all_formats("user_interactions", interactions)


# FastAPI endpoints for data export
app = FastAPI(title="Recipe Data Export API")


@app.get("/api/export/recipes")
async def export_recipes_api(
    cuisine_type: Optional[str] = Query(None, description="Filter by cuisine type"),
    min_rating: Optional[float] = Query(None, description="Filter by minimum rating"),
    max_difficulty: Optional[float] = Query(
        None, description="Filter by maximum difficulty"
    ),
    format: str = Query(
        "json", description="Export format (json, csv, parquet, excel, pickle)"
    ),
    session: Session = Depends(),
) -> Dict[str, str]:
    """
    Export recipes with optional filters.

    Args:
        cuisine_type: Optional cuisine type filter
        min_rating: Optional minimum rating filter
        max_difficulty: Optional maximum difficulty filter
        format: Export format
        session: Database session (injected by FastAPI)

    Returns:
        Dict[str, str]: Response with export file path

    Raises:
        HTTPException: If export fails
    """
    try:
        filters = {}
        if cuisine_type:
            filters["cuisine_type"] = cuisine_type
        if min_rating is not None:
            filters["community_rating"] = min_rating
        if max_difficulty is not None:
            filters["difficulty_score"] = max_difficulty

        exporter = DataExporter(session, "exports")
        result = exporter.export_recipes(filters)

        return {"status": "success", "file_path": str(result[format])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/interactions")
async def export_interactions_api(
    start_date: Optional[datetime] = Query(
        None, description="Start date for interaction data"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for interaction data"
    ),
    format: str = Query(
        "json", description="Export format (json, csv, parquet, excel, pickle)"
    ),
    session: Session = Depends(),
) -> Dict[str, str]:
    """
    Export user interactions within date range.

    Args:
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        format: Export format
        session: Database session (injected by FastAPI)

    Returns:
        Dict[str, str]: Response with export file path

    Raises:
        HTTPException: If export fails
    """
    try:
        exporter = DataExporter(session, "exports")
        result = exporter.export_user_interactions(start_date, end_date)

        return {"status": "success", "file_path": str(result[format])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
