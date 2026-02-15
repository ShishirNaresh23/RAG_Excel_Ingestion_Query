from fastapi import FastAPI
from app.api.routes import router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Excel RAG OOP Project",
    version="1.0.0"
)

app.include_router(router)

# For local running
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)