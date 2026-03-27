import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api import users, experiences, education, projects, activities, skill_categories, resume, snapshots, tailor

app = FastAPI(title="Resume Generator API")

API_SECRET_KEY = os.getenv("API_SECRET_KEY")

@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path in ("/", "/health", "/docs", "/openapi.json", "/redoc"):
        return await call_next(request)
    if API_SECRET_KEY and request.headers.get("X-API-Key") != API_SECRET_KEY:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return await call_next(request)

app.include_router(users.router)
app.include_router(experiences.router)
app.include_router(education.router)
app.include_router(projects.router)
app.include_router(activities.router)
app.include_router(skill_categories.router)
app.include_router(resume.router)
app.include_router(snapshots.router)
app.include_router(tailor.router)


@app.get("/")
def root():
    return {"message": "Resume Generator API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}