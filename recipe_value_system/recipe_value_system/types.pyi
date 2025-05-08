"""Type stubs for Recipe Value System."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Set, TypedDict, Union

# Common types
RecipeId = int
UserId = int
Timestamp = datetime
Value = Decimal

# Database types
class RecipeDict(TypedDict):
    recipe_id: RecipeId
    title: str
    author: Optional[str]
    created_at: Timestamp
    updated_at: Timestamp
    difficulty_level: Optional[str]
    cuisine_type: Optional[str]
    diet_categories: List[str]

class UserDict(TypedDict):
    user_id: UserId
    username: str
    email: str
    created_at: Timestamp
    last_active: Timestamp
    preferences: Dict[str, str]

# Service types
class ServiceResult(TypedDict):
    success: bool
    error: Optional[str]
    data: Optional[Dict[str, Union[str, int, float, List[str]]]]

# Analytics types
class MetricsDict(TypedDict):
    metric_name: str
    value: Union[int, float, str]
    timestamp: Timestamp
    metadata: Dict[str, str]

# Value types
class ValueDict(TypedDict):
    recipe_id: RecipeId
    current_value: Value
    calculated_at: Timestamp
    multipliers: Dict[str, float]
