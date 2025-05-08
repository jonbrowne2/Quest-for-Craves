# Recipe API Documentation

## Overview

The Recipe API provides endpoints for managing recipes in the FoodieFix application. It follows REST principles and includes comprehensive validation, caching, and error handling.

## Authentication

All endpoints require authentication. Include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

## Rate Limiting

Each endpoint has its own rate limiting rules:
- POST/PUT: 10 requests per minute
- GET: 100 requests per minute

## Endpoints

### Create Recipe (POST /api/recipes)

Creates a new recipe with the provided details.

#### Request Body

```json
{
  "title": "Spaghetti Carbonara",
  "description": "Classic Italian pasta dish",
  "difficulty": "Medium",
  "cuisine": "Italian",
  "prepTime": 15,
  "cookTime": 20,
  "servings": 4,
  "ingredients": [
    {
      "name": "Spaghetti",
      "amount": 1,
      "unit": "pound"
    }
  ],
  "steps": [
    {
      "instruction": "Boil the pasta"
    }
  ],
  "userId": "user123"
}
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "id": "recipe123",
    "title": "Spaghetti Carbonara",
    "description": "Classic Italian pasta dish",
    ...
  }
}
```

### Get Recipe(s) (GET /api/recipes)

Retrieves either a single recipe by ID or a paginated list of recipes.

#### Parameters

- `id` (optional): Recipe ID to fetch a single recipe
- `userId` (required): User ID making the request
- `page` (optional, default: 1): Page number for pagination
- `limit` (optional, default: 10): Items per page

#### Single Recipe Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "recipe123",
    "title": "Spaghetti Carbonara",
    "description": "Classic Italian pasta dish",
    ...
  }
}
```

#### Recipe List Response (200 OK)

```json
{
  "success": true,
  "data": {
    "recipes": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "totalPages": 10
    }
  }
}
```

### Update Recipe (PUT /api/recipes)

Updates an existing recipe with the provided details.

#### Parameters

- `id` (required): Recipe ID to update

#### Request Body

```json
{
  "title": "Updated Spaghetti Carbonara",
  "description": "Updated classic Italian pasta dish",
  ...
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "recipe123",
    "title": "Updated Spaghetti Carbonara",
    ...
  }
}
```

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

### Common Error Codes

- 400: Bad Request (invalid input)
- 401: Unauthorized (missing or invalid API key)
- 422: Unprocessable Entity (validation error)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

## Caching

The API implements caching for both individual recipes and recipe lists:
- Individual recipes: 1-hour TTL
- Recipe lists: 1-hour TTL
- Cache is automatically invalidated on updates

## Monitoring

All requests are monitored for:
- Response time
- Cache hit/miss rates
- Error rates
- User interactions
- Feature usage

## Event Tracking

The API tracks various events:
- Recipe creation
- Recipe updates
- Recipe views
- User interactions
- Cache performance
- Error occurrences

## Feedback Collection

The API automatically collects user feedback for recipe views after a 5-second delay.

## Experimentation

The API supports A/B testing and feature experiments through the ExperimentationService.
