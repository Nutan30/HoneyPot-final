from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import router
from .database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on application start
    init_db()
    yield


app = FastAPI(
    title="Agentic HoneyPot API",
    description="Autonomous Deceptive Honeypot API for Threat Intelligence & Counter-Interrogation",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for SOC dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
