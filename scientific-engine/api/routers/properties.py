"""
HumanMol AI - Property Prediction API Router (Chemprop)
"""

import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Molecule, PredictionResult
from scientific_engine.property_prediction.chemprop_service import predict_molecular_properties
from scientific_engine.schemas.schemas import (
    PropertyPredictionRequest, PropertyPredictionResponse, PropertyPredictionItem
)

logger = logging.getLogger("humanmol.api.properties")
router = APIRouter(prefix="/api/properties", tags=["Property Prediction (Chemprop)"])

@router.post("/predict", response_model=PropertyPredictionResponse)
def predict_properties(req: PropertyPredictionRequest, db: Session = Depends(get_db)):
    """
    Executes in silico molecular property prediction using Chemprop D-MPNN.
    Stores prediction values in the database, explicitly tagged as computational predictions.
    """
    if not req.smiles:
        raise HTTPException(status_code=400, detail="Empty SMILES list provided.")

    t0 = time.time()
    try:
        raw_preds = predict_molecular_properties(req.smiles, model_path=req.model_path)
    except Exception as e:
        logger.error(f"Chemprop prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chemprop inference error: {str(e)}")

    items = []
    for item in raw_preds:
        smi = item.get("smiles")
        val = item.get("predicted_property")
        denorm = item.get("denormalized_property")
        items.append(PropertyPredictionItem(
            smiles=smi,
            predicted_property=val,
            denormalized_property=denorm,
            status=item.get("status", "success"),
            model_type=item.get("model_type", "Chemprop_MPNN_v2.3.1"),
            is_experimental=False
        ))

        # Persist in DB
        mol = db.query(Molecule).filter(Molecule.canonical_smiles == smi).first()
        if mol and val is not None:
            pred_record = PredictionResult(
                molecule_id=mol.id,
                prediction_type="property",
                model_name="Chemprop_MPNN",
                model_version="2.3.1",
                model_provenance="scientific-engine/property-prediction/chemprop_test_model.pt",
                endpoint_name="LogP_prediction",
                predicted_value=val,
                raw_data=item,
                execution_time_seconds=None,
                is_experimental=False
            )
            db.add(pred_record)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Could not persist predictions to DB: {e}")

    t1 = time.time()
    return PropertyPredictionResponse(
        success=True,
        total_evaluated=len(items),
        predictions=items,
        execution_time_seconds=round(t1 - t0, 3)
    )
