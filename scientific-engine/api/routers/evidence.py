"""
HumanMol AI - Research Evidence API Router (PubMed & arXiv)
"""

import time
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import LiteratureEvidence
from scientific_engine.research_evidence.pubmed_service import search_pubmed_literature
from scientific_engine.research_evidence.arxiv_service import search_arxiv_preprints
from scientific_engine.schemas.schemas import EvidenceSearchResponse, EvidenceSearchRequest

logger = logging.getLogger("humanmol.api.evidence")
router = APIRouter(prefix="/api/evidence", tags=["Research Evidence"])

@router.post("/search", response_model=EvidenceSearchResponse)
def search_scientific_literature_post(body: EvidenceSearchRequest, db: Session = Depends(get_db)):
    """POST endpoint for literature searching matching request body schema."""
    return search_scientific_literature(
        query=body.query,
        max_pubmed=body.max_pubmed,
        max_arxiv=body.max_arxiv,
        db=db,
    )

@router.get("/search", response_model=EvidenceSearchResponse)
def search_scientific_literature(
    query: str = Query(..., description="Target or drug design topic to research"),
    max_pubmed: int = Query(5, ge=1, le=20),
    max_arxiv: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Retrieves scientific evidence from PubMed (peer-reviewed & experimental literature)
    and arXiv (computational chemistry & machine learning preprints).
    Persists citations into the database, explicitly distinguishing experimental vs. computational evidence.
    """
    t0 = time.time()
    pubmed_articles = []
    arxiv_preprints = []

    # 1. PubMed
    try:
        pubmed_articles = search_pubmed_literature(query, max_results=max_pubmed)
    except Exception as e:
        logger.warning(f"PubMed search error: {e}")

    # 2. arXiv
    try:
        arxiv_preprints = search_arxiv_preprints(query, max_results=max_arxiv)
    except Exception as e:
        logger.warning(f"arXiv search error: {e}")

    # Persist PubMed to DB (Experimental = True)
    for p in pubmed_articles:
        pmid = p.get("pmid")
        if pmid:
            existing = db.query(LiteratureEvidence).filter(
                LiteratureEvidence.source == "PubMed",
                LiteratureEvidence.source_id == pmid
            ).first()
            if not existing:
                record = LiteratureEvidence(
                    query_target=query,
                    source="PubMed",
                    source_id=pmid,
                    title=p.get("title", ""),
                    abstract=p.get("abstract", ""),
                    authors=p.get("authors", []),
                    publication_date=p.get("pub_year", ""),
                    doi=p.get("doi", ""),
                    url=p.get("url", ""),
                    is_experimental=True
                )
                db.add(record)

    # Persist arXiv to DB (Experimental = False)
    for a in arxiv_preprints:
        aid = a.get("id")
        if aid:
            existing = db.query(LiteratureEvidence).filter(
                LiteratureEvidence.source == "arXiv",
                LiteratureEvidence.source_id == aid
            ).first()
            if not existing:
                record = LiteratureEvidence(
                    query_target=query,
                    source="arXiv",
                    source_id=aid,
                    title=a.get("title", ""),
                    abstract=a.get("abstract", ""),
                    authors=a.get("authors", []),
                    publication_date=a.get("published", ""),
                    doi=None,
                    url=a.get("pdf_url") or aid,
                    is_experimental=False
                )
                db.add(record)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Could not persist literature to DB: {e}")

    t1 = time.time()
    return EvidenceSearchResponse(
        success=True,
        query=query,
        pubmed_evidence=pubmed_articles,
        arxiv_preprints=arxiv_preprints,
        experimental_sources_count=len(pubmed_articles),
        computational_preprints_count=len(arxiv_preprints),
        execution_time_seconds=round(t1 - t0, 3)
    )
