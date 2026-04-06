from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.nudges import router as nudges_router
from app.api.practice import router as practice_router
from app.api.providers import router as providers_router
from app.api.sessions import router as sessions_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


app.include_router(sessions_router, prefix=settings.api_prefix)
app.include_router(nudges_router, prefix=settings.api_prefix)
app.include_router(practice_router, prefix=settings.api_prefix)
app.include_router(providers_router, prefix=settings.api_prefix)
