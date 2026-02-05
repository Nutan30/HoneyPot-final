from fastapi import FastAPI
from .router import router

app = FastAPI(title="Agentic HoneyPot API")
app.include_router(router)
