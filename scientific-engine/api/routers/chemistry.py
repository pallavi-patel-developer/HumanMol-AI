"""
HumanMol AI - Chemistry API Router (RDKit)
"""

import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Molecule
from scientific_engine.chemistry.rdkit_service import validate_and_parse_smiles
from scientific_engine.schemas.schemas import (
    SmilesValidationRequest, MolecularDescriptorResponse
)

logger = logging.getLogger("humanmol.api.chemistry")
router = APIRouter(prefix="/api/chemistry", tags=["Chemistry (RDKit)"])

@router.post("/validate", response_model=MolecularDescriptorResponse)
def validate_molecule(req: SmilesValidationRequest, db: Session = Depends(get_db)):
    """
    Validates a SMILES string, calculates physicochemical descriptors,
    evaluates Lipinski's Rule of Five, and persists the molecule to the database.
    """
    t0 = time.time()
    result = validate_and_parse_smiles(req.smiles)
    t1 = time.time()
    exec_time = round(t1 - t0, 3)

    if not result.get("valid"):
        return MolecularDescriptorResponse(
            success=False,
            valid=False,
            error=result.get("error", "Invalid SMILES structure"),
            execution_time_seconds=exec_time
        )

    canonical = result["smiles"]
    # Check if molecule already exists in DB
    existing = db.query(Molecule).filter(Molecule.canonical_smiles == canonical).first()
    if not existing:
        mol_record = Molecule(
            canonical_smiles=canonical,
            molecular_formula=result.get("formula"),
            molecular_weight=result.get("molecular_weight"),
            logp=result.get("logp"),
            hbd=result.get("hbd"),
            hba=result.get("hba"),
            tpsa=result.get("tpsa"),
            rotatable_bonds=result.get("rotatable_bonds"),
            lipinski_ro5=result.get("lipinski_ro5"),
            source_engine="RDKit_Validation"
        )
        db.add(mol_record)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Could not persist molecule to DB: {e}")

    return MolecularDescriptorResponse(
        success=True,
        valid=True,
        smiles=canonical,
        formula=result.get("formula"),
        molecular_weight=result.get("molecular_weight"),
        logp=result.get("logp"),
        hbd=result.get("hbd"),
        hba=result.get("hba"),
        tpsa=result.get("tpsa"),
        rotatable_bonds=result.get("rotatable_bonds"),
        lipinski_ro5=result.get("lipinski_ro5"),
        execution_time_seconds=exec_time
    )
