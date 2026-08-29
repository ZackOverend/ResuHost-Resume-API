from fastapi import FastAPI, Request
from app.api import (
    activities,
    education,
    experiences,
    profile,
    profile_activities,
    profile_education,
    profile_experiences,
    profile_projects,
    profile_skill_categories,
    projects,
    resume,
    skill_categories,
    snapshots,
    tailor,
    users,
)
from app.config import Settings, get_settings
from app.errors import error_response, install_error_handlers, request_id_from


PUBLIC_PATHS = frozenset({"/", "/health", "/docs", "/openapi.json", "/redoc"})


def create_app(settings: Settings | None = None) -> FastAPI:
    application = FastAPI(title="ResuHost Resume API")
    app_settings = settings or get_settings()
    install_error_handlers(application)

    @application.middleware("http")
    async def require_api_key(request: Request, call_next):
        request.state.request_id = request_id_from(request)
        if request.url.path in PUBLIC_PATHS:
            response = await call_next(request)
        elif (
            app_settings.api_secret_key
            and request.headers.get("X-API-Key") != app_settings.api_secret_key
        ):
            response = error_response(
                request,
                status_code=401,
                code="unauthorized",
                message="A valid API key is required",
            )
        else:
            response = await call_next(request)

        response.headers["X-Request-ID"] = request.state.request_id
        return response

    application.include_router(users.router)
    application.include_router(experiences.router)
    application.include_router(education.router)
    application.include_router(projects.router)
    application.include_router(activities.router)
    application.include_router(skill_categories.router)
    application.include_router(resume.router)
    application.include_router(snapshots.router)
    application.include_router(tailor.router)
    application.include_router(profile.router)
    application.include_router(profile_activities.router)
    application.include_router(profile_education.router)
    application.include_router(profile_experiences.router)
    application.include_router(profile_projects.router)
    application.include_router(profile_skill_categories.router)

    @application.get("/")
    def root():
        return {"message": "ResuHost Resume API", "docs": "/docs"}

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()
