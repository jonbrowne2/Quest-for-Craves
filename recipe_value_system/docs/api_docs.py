"""Type-safe API documentation generator."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class HttpMethod(Enum):
    """HTTP methods supported by the API."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class ParameterLocation(Enum):
    """Possible locations for API parameters."""

    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    BODY = "body"


@dataclass
class ApiParameter:
    """API parameter documentation."""

    name: str
    type: str
    location: ParameterLocation
    description: str
    required: bool = True
    default: Optional[Union[str, int, float, bool]] = None
    example: Optional[str] = None


@dataclass
class ApiResponse:
    """API response documentation."""

    status_code: int
    description: str
    schema: Optional[type] = None
    example: Optional[Dict] = None


@dataclass
class ApiEndpoint:
    """API endpoint documentation."""

    path: str
    method: HttpMethod
    summary: str
    description: str
    parameters: List[ApiParameter] = field(default_factory=list)
    responses: Dict[int, ApiResponse] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class ApiDocGenerator:
    """Type-safe API documentation generator."""

    def __init__(self) -> None:
        """Initialize API documentation generator."""
        self.endpoints: List[ApiEndpoint] = []

    def document_endpoint(self, endpoint: ApiEndpoint) -> None:
        """Add documentation for an API endpoint."""
        self.endpoints.append(endpoint)

    def generate_openapi_spec(self) -> Dict:
        """Generate OpenAPI specification."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Recipe Value System API",
                "version": "1.0.0",
                "description": "API for managing recipe values and analysis",
            },
            "paths": self._generate_paths(),
            "components": self._generate_components(),
        }

    def _generate_paths(self) -> Dict:
        """Generate OpenAPI paths specification."""
        paths: Dict[str, Dict] = {}

        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}

            paths[endpoint.path][endpoint.method.value.lower()] = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "tags": endpoint.tags,
                "parameters": [
                    self._parameter_to_openapi(param)
                    for param in endpoint.parameters
                    if param.location != ParameterLocation.BODY
                ],
                "responses": {
                    str(status): self._response_to_openapi(response)
                    for status, response in endpoint.responses.items()
                },
            }

            # Add request body if there are body parameters
            body_params = [
                p for p in endpoint.parameters if p.location == ParameterLocation.BODY
            ]
            if body_params:
                paths[endpoint.path][endpoint.method.value.lower()]["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": self._body_params_to_schema(body_params)
                        }
                    }
                }

        return paths

    def _generate_components(self) -> Dict:
        """Generate OpenAPI components specification."""
        components: Dict[str, Dict] = {"schemas": {}, "responses": {}, "parameters": {}}

        # Add Pydantic models to schemas
        for endpoint in self.endpoints:
            for response in endpoint.responses.values():
                if response.schema and issubclass(response.schema, BaseModel):
                    schema_name = response.schema.__name__
                    components["schemas"][schema_name] = response.schema.schema()

        return components

    def _parameter_to_openapi(self, param: ApiParameter) -> Dict:
        """Convert parameter to OpenAPI format."""
        return {
            "name": param.name,
            "in": param.location.value,
            "description": param.description,
            "required": param.required,
            "schema": {"type": param.type},
            **({"default": param.default} if param.default is not None else {}),
            **({"example": param.example} if param.example is not None else {}),
        }

    def _response_to_openapi(self, response: ApiResponse) -> Dict:
        """Convert response to OpenAPI format."""
        spec = {"description": response.description}

        if response.schema:
            if issubclass(response.schema, BaseModel):
                spec["content"] = {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{response.schema.__name__}"
                        }
                    }
                }
            else:
                spec["content"] = {
                    "application/json": {"schema": response.schema.schema()}
                }

        if response.example:
            if "content" not in spec:
                spec["content"] = {"application/json": {}}
            spec["content"]["application/json"]["example"] = response.example

        return spec

    def _body_params_to_schema(self, params: List[ApiParameter]) -> Dict:
        """Convert body parameters to OpenAPI schema."""
        return {
            "type": "object",
            "properties": {
                param.name: {
                    "type": param.type,
                    "description": param.description,
                    **({"default": param.default} if param.default is not None else {}),
                    **({"example": param.example} if param.example is not None else {}),
                }
                for param in params
            },
            "required": [param.name for param in params if param.required],
        }


# Example usage decorator
def document_api(
    path: str,
    method: HttpMethod,
    summary: str,
    description: str,
    parameters: List[ApiParameter] = None,
    responses: Dict[int, ApiResponse] = None,
    tags: List[str] = None,
):
    """Decorator to document API endpoints."""

    def decorator(func):
        endpoint = ApiEndpoint(
            path=path,
            method=method,
            summary=summary,
            description=description,
            parameters=parameters or [],
            responses=responses or {},
            tags=tags or [],
        )
        api_doc_generator.document_endpoint(endpoint)
        return func

    return decorator


# Global API documentation generator instance
api_doc_generator = ApiDocGenerator()
