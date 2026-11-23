from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.config import logger, UPLOAD_DIR, REPORT_DIR, LOG_DIR
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.services.database import connect_db, disconnect_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Initializing workspace folders...")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Connecting to database...")
    await connect_db()

    logger.info("FastAPI backend started successfully.")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Disconnecting from database...")
    await disconnect_db()

    # NOTE: Persistent upload/report directories are intentionally NOT deleted
    # on shutdown.  Wiping them on every container restart would destroy user
    # data mounted via Docker named volumes.  Session-level cleanup is handled
    # by the DELETE /session/{session_id} endpoint and the POST /admin/cleanup
    # expired-session sweeper, both of which operate on individual sessions.
    logger.info("Shutdown complete. Upload and report directories preserved.")


app = FastAPI(
    title="AI Multi-Agent Research & Report Platform",
    description="Professional enterprise AI multi-agent analyst dashboard and report generator.",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)   # /auth/register, /auth/login, /auth/me
app.include_router(router)        # /upload, /research, /download, /health, etc.
