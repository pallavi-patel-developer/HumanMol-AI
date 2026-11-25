"""
HumanMol AI - ADMET API Router (ADMETlab 3.0)
"""

import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Molecule, PredictionResult
from scientific_engine.admet.admetlab_client import ADMETService
from scientific_engine.schemas.schemas import (
    ADMETRequest, ADMETResponse
)

logger = logging.getLogger("humanmol.api.admet")
router = APIRouter(prefix="/api/admet", tags=["ADMET (ADMETlab 3.0)"])

admet_service = ADMETService()

@router.post("/predict", response_model=ADMETResponse)
def evaluate_admet(req: ADMETRequest, db: Session = Depends(get_db)):
    """
    Submits a molecular SMILES string to the verified ADMETlab 3.0 REST service,
    extracting 119 physicochemical, absorption, distribution, metabolism, excretion,
    and toxicity parameters with uncertainty estimation.
    """
    if not req.smiles:
        raise HTTPException(status_code=400, detail="Empty SMILES provided.")

    t0 = time.time()
    try:
        res = admet_service.predict_properties(req.smiles)
    except Exception as e:
        logger.error(f"ADMETlab query failed: {e}")
        raise HTTPException(status_code=500, detail=f"ADMETlab error: {str(e)}")

    if not res.get("success"):
        logger.warning(f"ADMET query unfulfilled: {res.get('error')}")
        return ADMETResponse(
            success=False,
            smiles=req.smiles,
            message=f"ADMETlab 3.0 remote notice: {res.get('error')}",
            execution_time_seconds=res.get("execution_time_seconds", round(time.time() - t0, 3)),
            is_experimental=False
        )

    summary = res.get("summary", {})
    categories = res.get("categories", [])
    exec_time = res.get("execution_time_seconds", round(time.time() - t0, 3))

    # Persist key endpoints to DB
    mol = db.query(Molecule).filter(Molecule.canonical_smiles == req.smiles).first()
    if mol:
        pred_record = PredictionResult(
            molecule_id=mol.id,
            prediction_type="admet",
            model_name="ADMETlab_3.0_DMPNN",
            model_version="3.0",
            model_provenance="https://admetlab3.scbdd.com/api/single/admet",
            endpoint_name="Comprehensive_ADMET_Profile",
            predicted_value=None,
            raw_data=summary,
            execution_time_seconds=exec_time,
            is_experimental=False
        )
        db.add(pred_record)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Could not persist ADMET predictions to DB: {e}")

    return ADMETResponse(
        success=True,
        smiles=req.smiles,
        categories=categories,
        summary=summary,
        execution_time_seconds=exec_time,
        is_experimental=False
    )
