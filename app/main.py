from fastapi import FastAPI
from app.router import router

app = FastAPI()

@app.get("/")
def health():
    return {"status": "alive"}

app.include_router(router)
