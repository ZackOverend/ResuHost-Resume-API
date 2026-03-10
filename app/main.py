from fastapi import FastAPI
from app.api import users, experiences, education

app = FastAPI(title="Resume Generator API")

app.include_router(users.router)
app.include_router(experiences.router)
app.include_router(education.router)

@app.get("/")
def root():
    return {"message": "Resume Generator API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}