from fastapi import FastAPI
from app.api import users, experiences, education, projects, activities, skill_categories, resume, snapshots, tailor

app = FastAPI(title="Resume Generator API")

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