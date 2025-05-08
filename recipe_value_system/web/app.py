"""Main FastAPI application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from recipe_value_system.services.feedback.api import router as feedback_router
from recipe_value_system.services.variations.api import router as trends_router
from recipe_value_system.web.routes import router as web_router

# Create FastAPI app
app = FastAPI(
    title="Recipe Value System",
    description="A data-driven recipe suggestion engine",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Include routers
app.include_router(web_router)
app.include_router(trends_router)
app.include_router(feedback_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
