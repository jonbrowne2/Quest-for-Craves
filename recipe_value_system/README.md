# Recipe Value System

A sophisticated system for managing recipes, calculating their value based on user preferences, and analyzing cooking trends. Features a Billboard Hot 100-style ranking system for recipes, showing what's trending and popular in the cooking community.

## Features

### Free Community Features
- Recipe management with comprehensive metadata
- User preference tracking and dietary restriction handling
- Two value calculation methods:
  1. Taste Rating: Simple rating based purely on taste preferences (Hate to Crave scale)
  2. Simple Value Rating: Balanced equation considering taste, health, time, effort, and cost
- Nutritional tracking and targeting
- Recipe rankings and trending analysis
- Community feedback and recipe sharing
- Redis caching for improved performance
- Comprehensive analytics system based on "Simplicity Through Usage" philosophy

### Premium Custom Features
- Personal AI agent for recipe customization
- Individual preference learning and adaptation
- Advanced pattern recognition tailored to you:
  - Your time patterns (daily, weekly, seasonal)
  - Your mood-based preferences
  - Your taste evolution tracking
  - Your success rate optimization
- Personalized recipe modifications
- Custom weight optimization for your preferences
- Detailed analytics of your cooking journey
- AI-generated companion content (videos, audio guides, cookbooks)

### Recipe Rankings
- Billboard Hot 100-style recipe rankings
- Multiple time periods:
  - Today's Top Recipes
  - This Week's Hot 100
  - This Month's Favorites
  - This Year's Best
  - All-Time Classics
- Different ranking types:
  - Overall Popularity
  - Value Rankings (cost-benefit analysis)
  - Taste Rankings

### Recipe Variations & Modifications
- Smart recipe clustering
- Modification tracking and success rates
- Ingredient substitution analysis
- Impact tracking (taste, texture, cost, etc.)
- User segment performance analysis

### Trend Analysis
- Category popularity tracking
- Trending ingredients
- Successful modifications
- Seasonal trends
- Regional popularity
- Demographic insights

## Analytics System

The Recipe Value System includes a comprehensive analytics framework based on our "Simplicity Through Usage" philosophy. This system helps us continuously improve the user experience by tracking feature usage and making data-driven decisions.

### Core Philosophy: "Simplicity Through Usage"

Our analytics system is built around a core philosophy that prioritizes simplicity and user value:

1. **Feature Tracking Metrics**
   - Usage Frequency (times accessed, time spent, completion rates)
   - Value Metrics (satisfaction scores, NPS, direct feedback)

2. **Simplification Process**
   - Monthly Feature Review (analyze data, identify friction, calculate ROI)
   - Feature Categories (core, growth, legacy, premium)

3. **Optimization Rules**
   - Remove features with low engagement, high abandonment, or poor satisfaction
   - Enhance features with high engagement, completion rates, and strong feedback

### AI-Generated Content Strategy

Our analytics system also supports our AI-generated content strategy:

- "Make with Me" Videos: AI-generated cooking companion videos at human-paced speed
- AI Cookbook Publishing: Annual compilation of top recipes
- Multiple Format Distribution (audio, video, print, digital)

### Technical Implementation

The analytics system consists of:

1. **Frontend Tracking**
   - TypeScript services for event tracking
   - React hooks for easy component integration
   - Comprehensive event categorization

2. **Backend Services**
   - FastAPI endpoints for data collection
   - SQLAlchemy models for data storage
   - Analysis tools for generating insights

3. **Dashboard**
   - Feature value visualization
   - ROI analysis and recommendations
   - User journey mapping

### Getting Started with Analytics

To run the analytics demo:

```bash
cd analytics
python run_demo.py
```

This will set up the database, register features, generate sample data, and start the API server.

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/recipe-value-system.git
cd recipe-value-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (see Configuration section)

## Configuration

The system supports multiple configuration methods:

1. **Environment Variables**:
   Create a `.env` file in the root directory with the following variables:

```env
DB_URL=postgresql://user:password@localhost:5432/recipe_db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=optional_password
LOG_LEVEL=INFO
ML_MODEL_PATH=/path/to/models
```

2. **YAML Configuration**:
   You can also use YAML configuration files in the `config` directory:

```yaml
# config/development.yaml
database:
  url: postgresql://user:password@localhost:5432/recipe_db
  pool_size: 10
  max_overflow: 20

redis:
  host: localhost
  port: 6379
  password: optional_password

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

value:
  default_mode: standard
  confidence_threshold: 0.6
  cache_ttl_hours: 1
```

3. **Configuration API**:
   The `SystemConfig` class provides a programmatic interface for accessing configuration:

```python
from config import SystemConfig

config = SystemConfig()
db_url = config.get("database", "url")
log_level = config.get("logging", "level", "INFO")  # With default value
```

The configuration system supports different environments (development, testing, production) and will automatically load the appropriate settings based on the `ENVIRONMENT` variable.

## Usage

### Web Interface

Run the web server:
```bash
uvicorn recipe_value_system.web.app:app --reload
```

Visit `http://localhost:8000/rankings` to see the recipe rankings.

### API Usage

Basic API usage example:

```python
from recipe_value_system import RecipeValueSystem

# Initialize the system
system = RecipeValueSystem()

# Get trending recipes
trending = system.get_trending_recipes(
    time_period="week",
    ranking_type="overall"
)

# Submit recipe feedback
feedback = {
    "rating": 4.5,
    "comment": "Great recipe!",
    "modifications": {
        "ingredients": {...},
        "instructions": [...]
    },
    "cooking_details": {
        "prep_time_actual": 20,
        "cook_time_actual": 35,
        "serving_size": 4
    }
}
system.submit_feedback(user_id=1, recipe_id=1, feedback=feedback)
```

## Project Structure

- `analytics/`: Trend analysis and data processing
- `config/`: Configuration management
- `models/`: Database models and data structures
- `services/`: Core business logic services
  - `feedback/`: User feedback and reward system
  - `variations/`: Recipe variations and trends
  - `export/`: Data export functionality
- `value/`: Value calculation components
- `web/`: Web interface and API endpoints
- `tests/`: Unit and integration tests

## Recent Improvements

### Type Safety and Code Quality Enhancements

The codebase has undergone significant improvements to enhance type safety, code quality, and maintainability:

1. **Type Annotations**
   - Added comprehensive type annotations to all modules
   - Implemented proper numpy type annotations using NDArray[np.float64]
   - Added TYPE_CHECKING imports for forward references
   - Fixed circular import issues

2. **Documentation**
   - Enhanced module, class, and method docstrings
   - Ensured all docstrings follow PEP 257 guidelines
   - Added detailed parameter and return type documentation
   - Improved code readability with consistent formatting

3. **Import Structure**
   - Implemented a robust three-tier import strategy with fallbacks
   - Added relative imports with proper error handling
   - Fixed circular dependencies
   - Created testing-friendly import structure

4. **Testing Infrastructure**
   - Added comprehensive type safety tests
   - Implemented mock classes for external dependencies
   - Created flexible parameter handling for testing
   - Ensured all files pass mypy type checking

5. **Code Organization**
   - Improved module structure and organization
   - Enhanced error handling
   - Added placeholder implementations for optional dependencies
   - Implemented consistent naming conventions

These improvements ensure the codebase is more maintainable, easier to understand, and less prone to type-related bugs.

## Testing

Run tests using pytest:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
