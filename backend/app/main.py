from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_insights import router as insights_router
from app.api.routes_progress import router as progress_router
from app.api.routes_roles import router as roles_router
from app.core.config import get_settings
from app.db.bootstrap import init_db
from app.schemas.common import HealthOut


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


settings = get_settings()

app = FastAPI(
    title="RoleRoute API",
    description="Backend for the RoleRoute career-growth MVP.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roles_router)
app.include_router(progress_router)
app.include_router(insights_router)


@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        app="RoleRoute",
        demo_mode=not settings.llm_configured,
        llm_configured=settings.llm_configured,
    )
