from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.db.session import engine
from app.models.warehouse import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup if they don't exist yet
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="CareerLens — AI-Powered Job Intelligence Platform",
    version="1.0.0",
    description=(
        "Modular job ingestion, ETL, analytics, and AI resume matching platform. "
        "Real job data only — no synthetic datasets."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes mounted at root — no /api prefix (frontend calls /jobs, /analytics, etc.)
app.include_router(router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "platform": "CareerLens"}
