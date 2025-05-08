# Recipe Value System Data Export Service

The Data Export Service provides flexible tools for exporting recipe and user interaction data in multiple formats, designed to meet the needs of different stakeholders in the organization.

## Supported Export Formats

1. **CSV** (`.csv`)
   - Universal format for spreadsheet applications
   - Easy to import into analysis tools
   - Human-readable

2. **JSON** (`.json`)
   - Web-friendly format
   - Preserves nested data structures
   - Ideal for API integrations

3. **Parquet** (`.parquet`)
   - Optimized for big data processing
   - Efficient columnar storage
   - Preferred by Data Engineers

4. **Excel** (`.xlsx`)
   - Formatted spreadsheets with multiple sheets
   - Includes data summaries
   - Preferred by Product Managers

5. **Pickle** (`.pkl`)
   - Native Python serialization
   - Preserves complex objects
   - Used by Data Scientists

## Usage

### Command Line Interface

Export data using the CLI tool:

```bash
# Export all recipes in all formats
python scripts/export_data.py export-recipes

# Export recipes with filters
python scripts/export_data.py export-recipes --cuisine italian --min-rating 4.0 --format json

# Export user interactions within a date range
python scripts/export_data.py export-interactions --start-date 2024-01-01 --end-date 2024-12-31

# Export everything
python scripts/export_data.py export-all
```

### REST API

Access data exports through the REST API:

```bash
# Export recipes (JSON)
GET /api/v1/export/recipes?format=json

# Export filtered recipes
GET /api/v1/export/recipes?cuisine_type=italian&min_rating=4.0&format=json

# Export user interactions
GET /api/v1/export/interactions?start_date=2024-01-01&end_date=2024-12-31&format=json
```

### Python API

Use the DataExporter class in your Python code:

```python
from recipe_value_system.services.export.data_exporter import DataExporter
from pathlib import Path

# Initialize exporter
exporter = DataExporter(session, Path("exports"))

# Export recipes
paths = exporter.export_recipes(
    filters={
        "cuisine_type": "italian",
        "community_rating": 4.0
    }
)

# Export user interactions
paths = exporter.export_user_interactions(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)
```

## Export Directory Structure

```
exports/
├── csv/
│   ├── recipes_20240206_205527.csv
│   └── user_interactions_20240206_205527.csv
├── json/
│   ├── recipes_20240206_205527.json
│   └── user_interactions_20240206_205527.json
├── parquet/
│   ├── recipes_20240206_205527.parquet
│   └── user_interactions_20240206_205527.parquet
├── excel/
│   ├── recipes_20240206_205527.xlsx
│   └── user_interactions_20240206_205527.xlsx
└── pickle/
    ├── recipes_20240206_205527.pkl
    └── user_interactions_20240206_205527.pkl
```

## Excel Export Features

The Excel exports include additional features:

- Formatted headers with background colors
- Auto-filtered columns
- Frozen header row
- Auto-adjusted column widths
- Summary sheet with metadata
- Data validation where applicable

## Data Security

- Exports are stored in a dedicated directory
- Each export is timestamped
- No sensitive user data is included
- Access controls should be implemented at the application level

## Best Practices

1. **Regular Cleanup**: Implement a cleanup policy for old exports
2. **Monitoring**: Track export sizes and frequencies
3. **Optimization**: Use appropriate formats for large datasets
4. **Security**: Control access to export endpoints
5. **Documentation**: Keep format specifications updated
