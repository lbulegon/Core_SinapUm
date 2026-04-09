"""
Architecture Intelligence Service - Meta-orbital de inteligência arquitetural do Core_SinapUm.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OPENMIND_SERVICE_URL = os.getenv("OPENMIND_SERVICE_URL", "http://openmind:8001")
PORT = int(os.getenv("ARCHITECTURE_INTELLIGENCE_PORT", "7025"))

app = FastAPI(
    title="Architecture Intelligence Service - SinapUm",
    description="Meta-orbital: design, review, refine, think, evolve, govern, stress",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/architecture", tags=["Architecture Intelligence"])


@app.get("/")
async def root():
    return {"service": "Architecture Intelligence Service", "status": "online", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "architecture_intelligence_service", "openmind_url": OPENMIND_SERVICE_URL}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False, log_level="info")
