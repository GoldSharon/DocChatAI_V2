from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import APP_NAME, APP_VERSION
from app.api.routes import router
from app.api.upload_routes import upload_router
import os, shutil

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Run after port is bound — safe for slow operations."""
    for folder in ["uploads", "data"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    print("[Startup] Session data cleared")

@app.get("/")
def root():
    if os.path.exists("app/static/index.html"):
        return FileResponse("app/static/index.html")
    return {"message": f"Welcome to {APP_NAME}!"}