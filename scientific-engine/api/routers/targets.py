"""
HumanMol AI - Biological Targets API Router
(UniProt, ChEMBL, Reactome, AlphaFold DB, RCSB PDB)
Federated biological intelligence with mutation-aware & domain-aware structure resolution.
Strictly separates experimental RCSB crystallographic structures from
computational AlphaFold deep learning models.
"""

import time
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from scientific_engine.biological_data.uniprot_chembl_service import (
    query_uniprot_protein, query_chembl_bioactivity, resolve_chembl_target_id
)
from scientific_engine.pathways.reactome_service import get_pathways_for_uniprot
from scientific_engine.protein_data.protein_service import (
    fetch_alphafold_structure_url, fetch_rcsb_entry, resolve_mutation_aware_structure
)
from scientific_engine.schemas.schemas import TargetSearchResponse, TargetSearchRequest

logger = logging.getLogger("humanmol.api.targets")
router = APIRouter(prefix="/api/targets", tags=["Biological Targets"])

@router.post("/search", response_model=TargetSearchResponse)
def search_biological_target_post(body: TargetSearchRequest):
    """POST endpoint for target searching matching request body schema."""
    return search_biological_target(
        query=body.query,
        mutation=body.mutation,
        domain=body.domain,
        include_pathways=body.include_pathways,
        include_bioactivity=body.include_bioactivity,
        include_structures=body.include_structures,
    )

@router.get("/search", response_model=TargetSearchResponse)
def search_biological_target(
    query: str = Query(..., description="Target symbol, gene, or UniProt accession (e.g. EGFR, P00533)"),
    mutation: Optional[str] = Query("L858R", description="Target mutation (e.g. L858R for EGFR kinase domain)"),
    domain: Optional[str] = Query("kinase", description="Target domain (e.g. kinase)"),
    include_pathways: bool = Query(True, description="Fetch Reactome pathways"),
    include_bioactivity: bool = Query(True, description="Fetch ChEMBL assays"),
    include_structures: bool = Query(True, description="Fetch AlphaFold and RCSB PDB data")
):
    """
    Performs federated biological intelligence queries:
    - UniProt: accession, protein name, organism (Homo sapiens priority), gene symbol, sequence length, function
    - ChEMBL: wet-lab bioactivity assays (distinct activity_id, assay_chembl_id, molecule_chembl_id, IC50/Ki)
    - Reactome: biological pathway annotations with readable names and direct URLs
    - AlphaFold DB: In silico predicted monomer structure coordinates URL (explicitly labeled computational)
    - RCSB PDB: Mutation-aware crystallographic reference (e.g. 2ITZ for EGFR L858R kinase domain with Gefitinib)
    """
    t0 = time.time()
    uniprot_records = []
    chembl_assays = []
    reactome_pathways = []
    alphafold_data = None
    rcsb_data = None
    recommended_structure = None
    redocking_benchmark = None

    q_clean = query.strip()

    # 1. UniProt Search (Enforces human reviewed priority for EGFR, c-Abl, etc.)
    try:
        uniprot_records = query_uniprot_protein(q_clean, limit=5)
    except Exception as e:
        logger.warning(f"UniProt query failed for {q_clean}: {e}")

    primary_record = uniprot_records[0] if uniprot_records else None
    primary_accession = primary_record.get("accession") or primary_record.get("primaryAccession") if primary_record else None
    gene_symbol = primary_record.get("gene_name") if primary_record else q_clean

    target_identifier = primary_accession or q_clean

    # 2. Reactome Pathways (Human pathways genuinely associated with target)
    if include_pathways and target_identifier:
        try:
            reactome_pathways = get_pathways_for_uniprot(target_identifier, max_results=10)
        except Exception as e:
            logger.warning(f"Reactome query failed for {target_identifier}: {e}")

    # 3. AlphaFold Structure (Explicitly computational predicted coordinates)
    if include_structures and primary_accession:
        try:
            alphafold_data = fetch_alphafold_structure_url(primary_accession)
        except Exception as e:
            logger.warning(f"AlphaFold query failed for {primary_accession}: {e}")

    # 4. Mutation-Aware Experimental RCSB Reference Structure Selection
    # For EGFR L858R kinase domain research, resolves PDB 2ITZ (never extracellular 1IVO)
    if include_structures:
        try:
            recommended_structure = resolve_mutation_aware_structure(
                query_target=q_clean,
                uniprot_accession=primary_accession,
                mutation=mutation or "L858R",
                domain=domain or "kinase"
            )
            rcsb_data = recommended_structure
            redocking_benchmark = recommended_structure.get("redocking_validation")
        except Exception as e:
            logger.warning(f"Mutation-aware structure resolution failed for {q_clean}: {e}")

    # 5. ChEMBL Bioactivity Assays (Dynamically resolves target ChEMBL ID)
    if include_bioactivity:
        try:
            target_chembl_id = resolve_chembl_target_id(primary_accession or q_clean, gene_symbol)
            chembl_assays = query_chembl_bioactivity(target_chembl_id, limit=8)
        except Exception as e:
            logger.warning(f"ChEMBL query failed for {target_identifier}: {e}")

    t1 = time.time()
    return TargetSearchResponse(
        success=True,
        query=query,
        selected_mutation=mutation or "L858R",
        uniprot_records=uniprot_records,
        chembl_assays=chembl_assays,
        reactome_pathways=reactome_pathways,
        alphafold_structure=alphafold_data,
        rcsb_crystal=rcsb_data,
        recommended_structure=recommended_structure,
        redocking_benchmark=redocking_benchmark,
        execution_time_seconds=round(t1 - t0, 3)
    )
