from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from app.routes.api import router as api_router
from app.config import BASE_DIR

app = FastAPI(title="IA-VID-O", description="Générateur de vidéos par IA")

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

# Include API routes
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
