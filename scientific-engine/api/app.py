"""
HumanMol AI - Unified Scientific Engine FastAPI Application
Integrates RDKit, REINVENT4, Chemprop, AutoDock Vina, ADMETlab 3.0,
UniProt, ChEMBL, Reactome, AlphaFold, RCSB PDB, PubMed, arXiv, and XPert.
"""

import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database.connection import init_db, engine, get_db_status
from scientific_engine.api.routers import (
    chemistry,
    generator,
    properties,
    docking,
    admet,
    targets,
    evidence,
    xpert,
    pipeline,
    bioactivity,
)
from scientific_engine.schemas.schemas import SCIENTIFIC_DISCLAIMER_TEXT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("humanmol.scientific_engine")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database schema and scientific engines on startup."""
    logger.info("Initializing HumanMol AI Scientific Engine...")
    init_db()
    logger.info(f"Database active using dialect: {engine.dialect.name}")
    yield
    logger.info("Shutting down HumanMol AI Scientific Engine.")

app = FastAPI(
    title="HumanMol AI - Scientific Engine API",
    description=(
        "Comprehensive in silico computational biology, generative chemistry, "
        "bioactivity prediction, molecular docking simulation, and evidence mining API.\n\n"
        f"**IMPORTANT SCIENTIFIC DISCLAIMER**:\n> {SCIENTIFIC_DISCLAIMER_TEXT}"
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Request Timing & Error Handling Middleware
@app.middleware("http")
async def add_timing_and_safety_headers(request: Request, call_next):
    t0 = time.time()
    try:
        response = await call_next(request)
        t1 = time.time()
        response.headers["X-Process-Time"] = f"{round((t1 - t0) * 1000, 2)}ms"
        response.headers["X-HumanMol-Disclaimer"] = "In-Silico-Predictions-Only"
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception during request {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Scientific Engine Error",
                "detail": str(exc),
                "disclaimer": SCIENTIFIC_DISCLAIMER_TEXT
            }
        )

# Register All Specialized Routers
app.include_router(chemistry.router)
app.include_router(generator.router, prefix="/api/generation")
app.include_router(generator.router, prefix="/api/generator")
app.include_router(properties.router)
app.include_router(docking.router)
app.include_router(admet.router)
app.include_router(targets.router)
app.include_router(evidence.router)
app.include_router(xpert.router, prefix="/api/cell-response")
app.include_router(xpert.router, prefix="/api/xpert")
app.include_router(pipeline.router)
app.include_router(bioactivity.router)

@app.get("/", tags=["Health & Info"])
def root_info():
    """Returns top-level API metadata, version, and scientific disclaimers."""
    db_info = get_db_status()
    return {
        "service": "HumanMol AI Scientific Engine",
        "version": "1.0.0",
        "status": "online",
        "database": db_info,
        "docs_url": "/docs",
        "frontend_integration": "Next.js / TypeScript compatible",
        "disclaimer": SCIENTIFIC_DISCLAIMER_TEXT
    }

@app.get("/health", tags=["Health & Info"])
def health_check():
    """Health check endpoint with verified database and scientific module status."""
    db_info = get_db_status()
    return {
        "status": "healthy" if db_info.get("status") == "connected" else "degraded",
        "database": db_info,
        "timestamp": time.time(),
        "modules": {
            "rdkit": "active",
            "reinvent4": "active",
            "chemprop": "active",
            "vina": "active",
            "admetlab": "active",
            "uniprot": "active",
            "chembl": "active",
            "reactome": "active",
            "pubmed": "active",
            "arxiv": "active",
            "xpert": "modular_cpu_sdpa"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scientific_engine.api.app:app", host="0.0.0.0", port=8000, reload=True)
