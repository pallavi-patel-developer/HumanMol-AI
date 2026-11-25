"""
HumanMol AI - Molecule Generation API Router (REINVENT4)
"""

import time
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Molecule
from scientific_engine.molecule_generator.generator_service import generate_molecules
from scientific_engine.chemistry.rdkit_service import validate_and_parse_smiles
from scientific_engine.schemas.schemas import (
    GenerationRequest, GenerationResponse, GeneratedMolecule
)

logger = logging.getLogger("humanmol.api.generation")
router = APIRouter(tags=["Generation (REINVENT4)"])

@router.post("/generate", response_model=GenerationResponse)
def generate_candidates(req: GenerationRequest, db: Session = Depends(get_db)):
    """
    Generates de novo drug candidates using REINVENT4 prior model,
    performs real-time RDKit chemical validation, computes Lipinski Ro5,
    and stores generated candidates in the database.
    """
    t0 = time.time()
    try:
        gen_result = generate_molecules(
            num_molecules=req.num_molecules,
            seed=req.seed,
            batch_size=req.batch_size
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"REINVENT4 generation error: {str(e)}")

    molecules_out = []
    valid_count = 0
    smiles_list = gen_result.get("smiles", [])
    nlls_list = gen_result.get("nlls", [None] * len(smiles_list))

    for idx, smi in enumerate(smiles_list):
        nll_val = nlls_list[idx] if idx < len(nlls_list) else None
        parsed = validate_and_parse_smiles(smi)
        
        if parsed.get("valid"):
            valid_count += 1
            canonical = parsed["smiles"]
            
            # Store in DB if not already present
            existing = db.query(Molecule).filter(Molecule.canonical_smiles == canonical).first()
            if not existing:
                mol_record = Molecule(
                    canonical_smiles=canonical,
                    molecular_formula=parsed.get("formula"),
                    molecular_weight=parsed.get("molecular_weight"),
                    logp=parsed.get("logp"),
                    hbd=parsed.get("hbd"),
                    hba=parsed.get("hba"),
                    tpsa=parsed.get("tpsa"),
                    rotatable_bonds=parsed.get("rotatable_bonds"),
                    lipinski_ro5=parsed.get("lipinski_ro5"),
                    source_engine="REINVENT4"
                )
                db.add(mol_record)
            
            molecules_out.append(GeneratedMolecule(
                smiles=canonical,
                nll=round(nll_val, 2) if nll_val is not None else None,
                chemical_validity=True,
                formula=parsed.get("formula"),
                molecular_weight=parsed.get("molecular_weight"),
                logp=parsed.get("logp"),
                tpsa=parsed.get("tpsa"),
                lipinski_ro5=parsed.get("lipinski_ro5")
            ))
        else:
            molecules_out.append(GeneratedMolecule(
                smiles=smi,
                nll=round(nll_val, 2) if nll_val is not None else None,
                chemical_validity=False
            ))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.warning(f"Database commit warning: {e}")

    t1 = time.time()
    return GenerationResponse(
        success=True,
        total_generated=len(smiles_list),
        valid_count=valid_count,
        molecules=molecules_out,
        execution_time_seconds=round(t1 - t0, 3),
        model_version=gen_result.get("model_version", "REINVENT4 v4.9.34"),
        prior_provenance=gen_result.get("prior_provenance", "Zenodo Record 15641296"),
        workflow_type="Prior-Based De Novo Chemical Sampling (Unconditioned)",
        target_conditioning=False,
        reward_optimization=False,
        nll_description=(
            "Negative Log-Likelihood (NLL) measures sequence probability under the prior RNN "
            "model trained on ChEMBL/PubChem. Lower NLL indicates common drug-like syntax; "
            "it is NOT an indicator of EGFR target binding affinity, potency, or drug efficacy."
        )
    )
