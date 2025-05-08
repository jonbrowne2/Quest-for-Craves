"""Web routes for the recipe value system."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTMLResponse, RedirectResponse, Request
from fastapi.templating import Jinja2Templates

from recipe_value_system.config import get_config, get_db
from recipe_value_system.config.config import SystemConfig

# Set up templates and static files
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


@router.get("/rankings", response_class=HTMLResponse)
async def rankings_page(
    request: Request,
    session=Depends(get_db),
    config: SystemConfig = Depends(get_config),
) -> HTMLResponse:
    """Serve the recipe rankings page.

    Args:
        request: FastAPI request object.
        session: Database session.
        config: System configuration.

    Returns:
        HTML response with rankings page.
    """
    return templates.TemplateResponse("rankings.html", {"request": request})


@router.get("/")
async def home(request: Request) -> RedirectResponse:
    """Redirect home to rankings page.

    Args:
        request: FastAPI request object.

    Returns:
        Redirect response to rankings page.
    """
    return RedirectResponse(url="/rankings")
