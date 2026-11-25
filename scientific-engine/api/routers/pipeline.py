"""
HumanMol AI - Candidate Evaluation Pipeline API Router
Orchestrates de novo generation, chemical validation, property prediction,
molecular docking, and ADMET profiling into a unified multi-parameter workflow.
"""

import os
import uuid
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Molecule, PipelineRun, CandidateEvaluation, DockingResult
from scientific_engine.molecule_generator.generator_service import generate_molecules
from scientific_engine.chemistry.rdkit_service import validate_and_parse_smiles
from scientific_engine.property_prediction.chemprop_service import predict_molecular_properties
from scientific_engine.docking.vina_docking import run_docking, VINA_BIN
from scientific_engine.docking.vina_docking import calculate_file_sha256
from scientific_engine.api.routers.docking import (
    TARGET_PRESETS, convert_smiles_to_pdbqt, EXPERIMENTS_DIR, BASE_DOCKING_DIR
)
from scientific_engine.admet.admetlab_client import ADMETService
from scientific_engine.schemas.schemas import (
    PipelineRunRequest, PipelineRunResponse, CandidateEvaluationResult
)

logger = logging.getLogger("humanmol.api.pipeline")
router = APIRouter(prefix="/api/pipeline", tags=["Candidate Evaluation Pipeline"])

admet_client = ADMETService()

def compute_mpo_composite_score(
    docking_affinity: Optional[float] = None,
    lipinski_passed: bool = False,
    chemprop_val: Optional[float] = None,
    herg_prob: Optional[float] = None,
    dili_prob: Optional[float] = None
) -> float:
    """
    Computes a Multi-Parameter Optimization (MPO) composite rank score (0.0 to 10.0 scale).
    Higher is better.
    - Docking Affinity: -8 to -12 kcal/mol adds points.
    - Lipinski Ro5: +2.0 points.
    - ADMET Safety: penalizes hERG cardiotoxicity and liver injury liabilities.
    """
    score = 5.0 # Base score

    if docking_affinity is not None:
        # e.g., -8 kcal/mol -> +2.4 points; -12 kcal/mol -> +3.6 points
        score += max(0.0, (-docking_affinity) * 0.3)

    if lipinski_passed:
        score += 2.0
    else:
        score -= 1.5

    if chemprop_val is not None:
        # Favorable drug-like LogP range (1.0 - 3.5)
        if 1.0 <= chemprop_val <= 3.5:
            score += 1.0
        elif chemprop_val > 5.0:
            score -= 1.5

    if herg_prob is not None and herg_prob > 0.5:
        score -= 2.0 # High cardiotoxicity penalty

    if dili_prob is not None and dili_prob > 0.5:
        score -= 1.5 # Hepatotoxicity penalty

    return round(max(0.0, min(10.0, score)), 2)

@router.post("/run", response_model=PipelineRunResponse)
@router.post("/evaluate", response_model=PipelineRunResponse)
def run_candidate_evaluation_pipeline(req: PipelineRunRequest, db: Session = Depends(get_db)):
    """
    Executes the end-to-end HumanMol AI discovery pipeline:
    1. Generates N de novo chemical candidates via REINVENT4 prior.
    2. Filters chemically valid structures and calculates Lipinski Ro5 descriptors via RDKit.
    3. Evaluates molecular bioactivity/property predictions via Chemprop D-MPNN (if enabled).
    4. Simulates 3D target docking poses & binding affinities via AutoDock Vina (if enabled).
    5. Evaluates pharmacokinetics and safety profiles via ADMETlab 3.0 (if enabled).
    6. Computes MPO composite rank scores and persists the run into PostgreSQL/SQLite.
    """
    t0 = time.time()
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    
    # 0. Canonical Target Resolution
    target_input = (req.target_name or req.target_protein or req.target_pdb_id or "EGFR").strip().upper()
    disease_input = (req.disease or "").strip().upper()
    
    if "EGFR" in target_input or "2ITZ" in target_input or "L858R" in target_input or "NSCLC" in disease_input:
        preset = TARGET_PRESETS["2ITZ"]
        canonical_target_name = "EGFR L858R Kinase Domain (2ITZ)"
        canonical_target_pdb = "2ITZ"
        canonical_mutation = "L858R (Leu 858 substituted by Arg 858)"
        canonical_disease = req.disease or "NSCLC"
    else:
        preset = TARGET_PRESETS["1IEP"]
        canonical_target_name = "c-Abl Kinase Domain (1IEP)"
        canonical_target_pdb = "1IEP"
        canonical_mutation = "Wild-Type"
        canonical_disease = req.disease or "CML"

    logger.info(f"Starting Candidate Evaluation Pipeline {run_id} for target '{canonical_target_name}' (PDB: {canonical_target_pdb})")

    # Module execution tracker
    modules_status = {
        "generation": "PENDING",
        "properties": "NOT_RUN" if not req.run_properties else "PENDING",
        "docking": "NOT_RUN" if not req.run_docking else "PENDING",
        "admet": "NOT_RUN" if not req.run_admet else "PENDING",
    }
    pipeline_errors: List[str] = []

    # 1. Initialize PipelineRun record in DB
    pipeline_record = PipelineRun(
        run_id=run_id,
        target_name=canonical_target_name,
        status="running",
        total_candidates=req.num_candidates,
        valid_candidates=0,
        metadata_json={
            "seed": req.seed,
            "target_pdb_id": canonical_target_pdb,
            "mutation": canonical_mutation,
            "disease": canonical_disease,
            "run_properties": req.run_properties,
            "run_docking": req.run_docking,
            "run_admet": req.run_admet
        }
    )
    db.add(pipeline_record)
    db.commit()

    try:
        # =====================================================================
        # Step A: Generative Sampling (REINVENT4 Prior)
        # =====================================================================
        try:
            gen_result = generate_molecules(num_molecules=req.num_candidates, seed=req.seed)
            raw_smiles = gen_result.get("smiles", [])
            modules_status["generation"] = "SUCCESS"
        except Exception as e:
            modules_status["generation"] = "FAILED"
            pipeline_errors.append(f"De Novo Generation failure: {str(e)}")
            raise e

        # =====================================================================
        # Step B: RDKit Chemistry Validation & Descriptors
        # =====================================================================
        validated_candidates = []
        for smi in raw_smiles:
            parsed = validate_and_parse_smiles(smi)
            if parsed.get("valid"):
                canonical = parsed["smiles"]
                
                # Ensure molecule is in DB
                mol = db.query(Molecule).filter(Molecule.canonical_smiles == canonical).first()
                if not mol:
                    mol = Molecule(
                        canonical_smiles=canonical,
                        molecular_formula=parsed.get("formula"),
                        molecular_weight=parsed.get("molecular_weight"),
                        logp=parsed.get("logp"),
                        hbd=parsed.get("hbd"),
                        hba=parsed.get("hba"),
                        tpsa=parsed.get("tpsa"),
                        rotatable_bonds=parsed.get("rotatable_bonds"),
                        lipinski_ro5=parsed.get("lipinski_ro5"),
                        source_engine="REINVENT4_Pipeline"
                    )
                    db.add(mol)
                    db.commit()
                validated_candidates.append((mol, parsed))

        pipeline_record.valid_candidates = len(validated_candidates)
        valid_smiles_list = [v[0].canonical_smiles for v in validated_candidates]

        # =====================================================================
        # Step C: Chemprop Property Prediction (D-MPNN)
        # =====================================================================
        chemprop_preds: Dict[str, Optional[float]] = {}
        chemprop_statuses: Dict[str, str] = {}
        chemprop_errors: Dict[str, Optional[str]] = {}

        if req.run_properties and valid_smiles_list:
            try:
                raw_props = predict_molecular_properties(valid_smiles_list)
                for p in raw_props:
                    s = p.get("smiles")
                    chemprop_preds[s] = p.get("predicted_property")
                    chemprop_statuses[s] = "SUCCESS"
                modules_status["properties"] = "SUCCESS"
            except Exception as e:
                logger.error(f"Chemprop prediction failed in pipeline: {e}")
                modules_status["properties"] = "FAILED"
                pipeline_errors.append(f"Chemprop D-MPNN failed: {str(e)}")
                for s in valid_smiles_list:
                    chemprop_preds[s] = None
                    chemprop_statuses[s] = "FAILED"
                    chemprop_errors[s] = str(e)
        else:
            for s in valid_smiles_list:
                chemprop_preds[s] = None
                chemprop_statuses[s] = "NOT_RUN"

        # =====================================================================
        # Step D: AutoDock Vina Docking Simulation
        # =====================================================================
        docking_scores: Dict[str, Optional[float]] = {}
        docking_statuses: Dict[str, str] = {}
        docking_errors: Dict[str, Optional[str]] = {}

        if req.run_docking and valid_smiles_list:
            docking_failed_count = 0
            # Dock top candidates (up to 3 for fast, responsive pipeline execution)
            for idx, smi in enumerate(valid_smiles_list):
                if idx < 3: # Actively dock the top 3 candidates
                    cand_exp_dir = os.path.join(EXPERIMENTS_DIR, f"{run_id}_cand{idx+1}")
                    os.makedirs(cand_exp_dir, exist_ok=True)
                    cand_ligand_pdbqt = os.path.join(cand_exp_dir, "ligand.pdbqt")
                    cand_out_pdbqt = os.path.join(cand_exp_dir, "docked_out.pdbqt")

                    ok, prep_err = convert_smiles_to_pdbqt(smi, cand_ligand_pdbqt)
                    if not ok:
                        docking_scores[smi] = None
                        docking_statuses[smi] = "FAILED"
                        docking_errors[smi] = prep_err
                        docking_failed_count += 1
                        continue

                    # Execute Vina with target preset coordinates
                    dock_res = run_docking(
                        receptor_pdbqt=preset["receptor"],
                        ligand_pdbqt=cand_ligand_pdbqt,
                        center_x=preset["center_x"],
                        center_y=preset["center_y"],
                        center_z=preset["center_z"],
                        size_x=preset["size_x"],
                        size_y=preset["size_y"],
                        size_z=preset["size_z"],
                        out_pdbqt=cand_out_pdbqt,
                        exhaustiveness=1 # Fast screening exhaustiveness for interactive pipeline
                    )

                    if dock_res.get("success") and dock_res.get("best_affinity_kcal_mol") is not None:
                        docking_scores[smi] = dock_res["best_affinity_kcal_mol"]
                        docking_statuses[smi] = "SUCCESS"
                    else:
                        docking_scores[smi] = None
                        docking_statuses[smi] = "FAILED"
                        docking_errors[smi] = dock_res.get("error", "Vina docking failed")
                        docking_failed_count += 1
                else:
                    # Candidates beyond top 3 marked as NOT_RUN in quick pipeline
                    docking_scores[smi] = None
                    docking_statuses[smi] = "NOT_RUN"

            if docking_failed_count == len(valid_smiles_list[:3]):
                modules_status["docking"] = "FAILED"
                pipeline_errors.append("AutoDock Vina failed to dock generated candidates.")
            elif docking_failed_count > 0:
                modules_status["docking"] = "PARTIAL_SUCCESS"
            else:
                modules_status["docking"] = "SUCCESS"
        else:
            for s in valid_smiles_list:
                docking_scores[s] = None
                docking_statuses[s] = "NOT_RUN"

        # =====================================================================
        # Step E: ADMET Profiling (ADMETlab 3.0)
        # =====================================================================
        admet_profiles: Dict[str, Dict[str, Any]] = {}
        admet_statuses: Dict[str, str] = {}
        admet_errors: Dict[str, Optional[str]] = {}

        if req.run_admet and valid_smiles_list:
            admet_failed_count = 0
            for idx, smi in enumerate(valid_smiles_list):
                if idx < 3: # Profile top 3 candidates to respect external rate limits
                    try:
                        admet_res = admet_client.predict_properties(smi)
                        if admet_res.get("success"):
                            admet_profiles[smi] = admet_res.get("summary", {})
                            admet_statuses[smi] = "SUCCESS"
                        else:
                            admet_statuses[smi] = "FAILED"
                            admet_errors[smi] = admet_res.get("error", "ADMETlab query failed")
                            admet_failed_count += 1
                    except Exception as e:
                        logger.warning(f"ADMET profiling error for {smi}: {e}")
                        admet_statuses[smi] = "FAILED"
                        admet_errors[smi] = str(e)
                        admet_failed_count += 1
                else:
                    admet_statuses[smi] = "NOT_RUN"

            if admet_failed_count == len(valid_smiles_list[:3]):
                modules_status["admet"] = "FAILED"
                pipeline_errors.append("ADMETlab 3.0 profiling failed for all tested candidates.")
            elif admet_failed_count > 0:
                modules_status["admet"] = "PARTIAL_SUCCESS"
            else:
                modules_status["admet"] = "SUCCESS"
        else:
            for s in valid_smiles_list:
                admet_statuses[s] = "NOT_RUN"

        # =====================================================================
        # Step F: Multi-Parameter Optimization (MPO) Scoring & Persistence
        # =====================================================================
        candidates_out = []
        for mol, parsed in validated_candidates:
            smi = mol.canonical_smiles
            cp_val = chemprop_preds.get(smi)
            dock_val = docking_scores.get(smi)
            
            adm = admet_profiles.get(smi, {})
            caco2_val = adm.get("absorption", {}).get("caco2")
            herg_val = adm.get("toxicity", {}).get("hERG")
            dili_val = adm.get("toxicity", {}).get("DILI")
            ames_val = adm.get("toxicity", {}).get("Ames")

            mpo_score = compute_mpo_composite_score(
                docking_affinity=dock_val,
                lipinski_passed=parsed.get("lipinski_ro5", False),
                chemprop_val=cp_val,
                herg_prob=herg_val,
                dili_prob=dili_val
            )

            # Persist docking result if available
            if dock_val is not None:
                dock_rec = DockingResult(
                    molecule_id=mol.id,
                    target_protein=canonical_target_name,
                    best_affinity_kcal_mol=dock_val,
                    num_modes=1,
                    modes_json=[{"mode": 1, "affinity_kcal_mol": dock_val}],
                    output_pdbqt_path=None,
                    is_experimental=False
                )
                db.add(dock_rec)

            # Persist evaluation record
            eval_record = CandidateEvaluation(
                pipeline_run_id=pipeline_record.id,
                molecule_id=mol.id,
                chemical_validity=True,
                lipinski_passed=parsed.get("lipinski_ro5", False),
                chemprop_predicted_property=cp_val,
                docking_best_affinity=dock_val,
                admet_caco2=caco2_val,
                admet_herg=herg_val,
                admet_dili=dili_val,
                admet_ames=ames_val,
                composite_rank_score=mpo_score,
                is_experimental_verified=False
            )
            db.add(eval_record)

            candidates_out.append(CandidateEvaluationResult(
                rank=1,
                smiles=smi,
                formula=parsed.get("formula"),
                molecular_weight=parsed.get("molecular_weight"),
                logp=parsed.get("logp"),
                lipinski_ro5=parsed.get("lipinski_ro5"),
                chemprop_predicted_property=cp_val,
                chemprop_status=chemprop_statuses.get(smi, "NOT_RUN"),
                chemprop_error=chemprop_errors.get(smi),
                docking_best_affinity=dock_val,
                docking_status=docking_statuses.get(smi, "NOT_RUN"),
                docking_error=docking_errors.get(smi),
                admet_caco2=caco2_val,
                admet_herg=herg_val,
                admet_dili=dili_val,
                admet_ames=ames_val,
                admet_status=admet_statuses.get(smi, "NOT_RUN"),
                admet_error=admet_errors.get(smi),
                composite_rank_score=mpo_score,
                is_experimental=False
            ))

        # Sort by MPO composite score descending
        candidates_out.sort(key=lambda c: c.composite_rank_score, reverse=True)
        for idx, c in enumerate(candidates_out, 1):
            c.rank = idx

        overall_status = "PARTIAL_SUCCESS" if pipeline_errors else "COMPLETED"
        pipeline_record.status = overall_status
        pipeline_record.completed_at = datetime.utcnow()
        db.commit()

        t1 = time.time()
        return PipelineRunResponse(
            success=True,
            run_id=run_id,
            status=overall_status,
            target_name=canonical_target_name,
            target_pdb_id=canonical_target_pdb,
            mutation=canonical_mutation,
            disease=canonical_disease,
            total_generated=len(raw_smiles),
            valid_count=len(validated_candidates),
            modules_status=modules_status,
            pipeline_errors=pipeline_errors,
            candidates=candidates_out,
            execution_time_seconds=round(t1 - t0, 3)
        )

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        pipeline_record.status = "failed"
        pipeline_record.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pipeline execution failure: {str(e)}")
