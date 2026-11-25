"""
HumanMol AI - Bioactivity & Selectivity API Router
Provides strictly validated endpoints for experimental bioactivity benchmarks,
compound assay queries, scientific comparability checks, and candidate evidence status.
"""

import time
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Path, Query
from scientific_engine.biological_data.bioactivity_service import bioactivity_service
from scientific_engine.schemas.schemas import (
    BioactivityBenchmarkResponse,
    CompoundBioactivityResponse,
    SelectivityCheckRequest,
    SelectivityCheckResponse,
    CandidateBioactivityStatusResponse,
    SCIENTIFIC_DISCLAIMER_TEXT,
)

logger = logging.getLogger("humanmol.api.bioactivity")
router = APIRouter(prefix="/api/bioactivity", tags=["Experimental Bioactivity & Selectivity"])

@router.get("/egfr-benchmark", response_model=BioactivityBenchmarkResponse)
def get_egfr_benchmark():
    """
    Returns verified primary-source experimental reference-inhibitor measurements
    (Gefitinib, Erlotinib, Afatinib, Osimertinib) against Wild-Type and mutant EGFR.
    """
    t0 = time.time()
    records = bioactivity_service.get_benchmark_dataset()
    unique_compounds = set(r["compound_name"] for r in records)
    t1 = time.time()

    return BioactivityBenchmarkResponse(
        success=True,
        execution_time_seconds=round(t1 - t0, 4),
        disclaimer=SCIENTIFIC_DISCLAIMER_TEXT,
        target_protein="EGFR (Homo sapiens, UniProt: P00533, ChEMBL: CHEMBL203)",
        reference_inhibitors_count=len(unique_compounds),
        total_records=len(records),
        records=records,
    )

@router.get("/compound/{compound_id}", response_model=CompoundBioactivityResponse)
def get_compound_bioactivity(
    compound_id: str = Path(..., description="Compound name or ChEMBL ID (e.g. CHEMBL68920, Gefitinib, Osimertinib)")
):
    """
    Returns all experimental bioactivity records for a compound across wild-type and mutant EGFR.
    """
    t0 = time.time()
    records = bioactivity_service.get_compound_bioactivities(compound_id)
    t1 = time.time()

    return CompoundBioactivityResponse(
        success=True,
        execution_time_seconds=round(t1 - t0, 4),
        disclaimer=SCIENTIFIC_DISCLAIMER_TEXT,
        compound_query=compound_id,
        records_count=len(records),
        records=records,
    )

@router.post("/selectivity-check", response_model=SelectivityCheckResponse)
def check_selectivity(request: SelectivityCheckRequest):
    """
    Validates scientific comparability between Wild-Type and Mutant EGFR measurements
    before computing the Selectivity Index:
    Selectivity Index = IC50(WT EGFR) / IC50(EGFR L858R)

    Requires compatible measurement types, assay formats, ATP cofactors, and identical compounds.
    Returns INCOMPARABLE with explicit scientific rationale if conditions differ.
    """
    t0 = time.time()

    if request.wt_record and request.mutant_record:
        result = bioactivity_service.validate_and_compute_selectivity(
            wt_record=request.wt_record.model_dump(),
            mutant_record=request.mutant_record.model_dump(),
            target_mutation=request.target_mutation
        )
    elif request.wt_assay_id and request.mutant_assay_id:
        result = bioactivity_service.check_selectivity_by_ids(
            wt_assay_id=request.wt_assay_id,
            mutant_assay_id=request.mutant_assay_id
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either (wt_assay_id, mutant_assay_id) or (wt_record, mutant_record) objects."
        )

    t1 = time.time()
    return SelectivityCheckResponse(
        success=True,
        execution_time_seconds=round(t1 - t0, 4),
        disclaimer=SCIENTIFIC_DISCLAIMER_TEXT,
        comparability_status=result["comparability_status"],
        selectivity_ratio=result.get("selectivity_ratio"),
        exploratory_ratio=result.get("exploratory_ratio"),
        selectivity_interpretation=result["selectivity_interpretation"],
        rejection_reason=result.get("rejection_reason"),
        wt_measurement=result.get("wt_measurement"),
        mutant_measurement=result.get("mutant_measurement"),
        irreversible_kinetics_note=result.get("irreversible_kinetics_note"),
        cellular_context_note=result.get("cellular_context_note"),
    )

@router.get("/candidate/{candidate_id}", response_model=CandidateBioactivityStatusResponse)
def get_candidate_evidence_status(
    candidate_id: str = Path(..., description="HumanMol candidate identifier (e.g. HM-EGFR-012)")
):
    """
    Returns the experimental evidence status of a HumanMol candidate molecule.
    Strictly asserts UNTESTED status for computational de novo candidates and lists
    required wet-lab assays before biological claims can be made.
    """
    t0 = time.time()
    data = bioactivity_service.get_candidate_evidence_status(candidate_id)
    t1 = time.time()

    return CandidateBioactivityStatusResponse(
        success=True,
        execution_time_seconds=round(t1 - t0, 4),
        disclaimer=SCIENTIFIC_DISCLAIMER_TEXT,
        candidate_id=data["candidate_id"],
        canonical_smiles=data.get("canonical_smiles"),
        isomeric_smiles=data.get("isomeric_smiles"),
        molecular_formula=data.get("molecular_formula"),
        molecular_weight=data.get("molecular_weight"),
        exact_molecular_weight=data.get("exact_molecular_weight"),
        inchikey=data.get("inchikey"),
        target=data["target"],
        computational_profile=data["computational_profile"],
        experimental_bioactivity=data["experimental_bioactivity"],
        scientific_disclaimer=data["scientific_disclaimer"],
        required_validation_assays=data["required_validation_assays"],
    )
