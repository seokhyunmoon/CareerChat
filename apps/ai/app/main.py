from fastapi import FastAPI

from app.api.analysis_jobs import router as analysis_jobs_router
from app.api.result_chat import router as result_chat_router

app = FastAPI(title="CareerChat AI", version="0.1.0")

app.include_router(analysis_jobs_router)
app.include_router(result_chat_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "UP"}
