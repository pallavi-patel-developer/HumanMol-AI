"""
HumanMol AI - Standardized Scientific Input & Output Schemas
Implements strict Pydantic v2 schemas preserving model provenance,
disclaimers, and separation of computational vs. experimental data.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator

# ==============================================================================
# 0. COMMON & SCIENTIFIC DISCLAIMERS
# ==============================================================================

SCIENTIFIC_DISCLAIMER_TEXT = (
    "DISCLAIMER: Computational predictions (including property predictions, ADMET profiles, "
    "and docking affinity scores) represent in silico mathematical approximations. "
    "Never interpret docking scores as proof of biological inhibition or clinical efficacy. "
    "Never classify generated molecules as safe or therapeutically effective without wet-lab "
    "in vitro assays and in vivo experimental validation."
)

class BaseScientificResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    disclaimer: str = Field(default=SCIENTIFIC_DISCLAIMER_TEXT)

# ==============================================================================
# 1. CORE CHEMISTRY SCHEMAS (RDKit)
# ==============================================================================

class SmilesValidationRequest(BaseModel):
    smiles: str = Field(..., description="SMILES string to validate and featurize")

class MolecularDescriptorResponse(BaseScientificResponse):
    valid: bool
    smiles: Optional[str] = None
    formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    logp: Optional[float] = None
    hbd: Optional[int] = None
    hba: Optional[int] = None
    tpsa: Optional[float] = None
    rotatable_bonds: Optional[int] = None
    lipinski_ro5: Optional[bool] = None
    error: Optional[str] = None

# ==============================================================================
# 2. MOLECULE GENERATION SCHEMAS (REINVENT4)
# ==============================================================================

class GenerationRequest(BaseModel):
    num_molecules: int = Field(default=10, ge=1, le=100, description="Number of molecules to generate")
    seed: Optional[int] = Field(default=None, description="Optional random seed for exact reproducibility")
    batch_size: int = Field(default=32, ge=1, le=128)

class GeneratedMolecule(BaseModel):
    smiles: str
    nll: Optional[float] = None
    chemical_validity: bool = True
    formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    logp: Optional[float] = None
    tpsa: Optional[float] = None
    lipinski_ro5: Optional[bool] = None

class GenerationResponse(BaseScientificResponse):
    total_generated: int
    valid_count: int
    molecules: List[GeneratedMolecule]
    model_version: str
    prior_provenance: str
    workflow_type: str = "Prior-Based De Novo Chemical Sampling (Unconditioned)"
    target_conditioning: bool = False
    reward_optimization: bool = False
    nll_description: str = (
        "Negative Log-Likelihood with respect to the prior RNN training distribution. "
        "Measures chemical syntax typicality; NOT an indicator of biological affinity or therapeutic efficacy."
    )

# ==============================================================================
# 3. PROPERTY PREDICTION SCHEMAS (Chemprop)
# ==============================================================================

class PropertyPredictionRequest(BaseModel):
    smiles: List[str] = Field(..., description="List of SMILES to evaluate")
    model_path: Optional[str] = Field(default=None, description="Optional custom checkpoint path")

class PropertyPredictionItem(BaseModel):
    smiles: str
    predicted_property: Optional[float] = None
    denormalized_property: Optional[float] = None
    status: str = "success"
    model_type: str = "Chemprop_MPNN_v2.3.1"
    is_experimental: bool = False

class PropertyPredictionResponse(BaseScientificResponse):
    total_evaluated: int
    predictions: List[PropertyPredictionItem]
    endpoint_name: str = "Octanol-Water Partition Coefficient Surrogate (LogP Benchmark)"
    endpoint_description: str = (
        "Computational graph neural network regression estimate of LogP. "
        "This is NOT target binding potency (IC50), cellular toxicity, or clinical efficacy."
    )
    target_units: str = "Logarithmic partition ratio (dimensionless)"
    model_checkpoint: str = "chemprop_test_model.pt"
    training_dataset: str = "Curated MoleculeNet Lipophilicity / ChEMBL benchmark subset"
    normalization_method: str = "Z-score standardization during training: y_scaled = (y - 2.18) / 1.20"
    validation_metrics: Dict[str, float] = Field(default_factory=lambda: {"val_rmse": 0.65, "val_mae": 0.48, "r_squared": 0.72})

# ==============================================================================
# 4. DOCKING SCHEMAS (AutoDock Vina)
# ==============================================================================

class DockingRequest(BaseModel):
    ligand_smiles: Optional[str] = Field(default=None, description="SMILES to dock")
    ligand_pdbqt_path: Optional[str] = Field(default=None, description="Existing ligand PDBQT path")
    target_pdb_id: Optional[str] = Field(default="2ITZ", description="PDB structure ID (e.g. 2ITZ or 1IEP)")
    receptor_pdbqt_path: Optional[str] = Field(default=None, description="Receptor PDBQT file path")
    center_x: Optional[float] = Field(default=None, description="Binding site center X coordinate")
    center_y: Optional[float] = Field(default=None, description="Binding site center Y coordinate")
    center_z: Optional[float] = Field(default=None, description="Binding site center Z coordinate")
    size_x: float = Field(default=20.0, description="Grid box X dimension in Angstroms")
    size_y: float = Field(default=20.0, description="Grid box Y dimension in Angstroms")
    size_z: float = Field(default=20.0, description="Grid box Z dimension in Angstroms")
    exhaustiveness: int = Field(default=8, ge=1, le=16)

class DockingMode(BaseModel):
    mode: int
    affinity_kcal_mol: float
    rmsd_lb: float
    rmsd_ub: float

class DockingResponse(BaseScientificResponse):
    experiment_id: str
    target_protein: str
    target_pdb_id: str
    mutation: Optional[str] = None
    ligand_smiles: Optional[str] = None
    best_affinity_kcal_mol: Optional[float] = None
    num_modes: int = 0
    modes: List[DockingMode] = []
    output_pdbqt_path: Optional[str] = None
    status: str = "SUCCESS" # "SUCCESS", "FAILED"
    error_message: Optional[str] = None
    exit_code: int = 0
    vina_command: Optional[str] = None
    receptor_sha256: Optional[str] = None
    ligand_sha256: Optional[str] = None
    is_benchmark: bool = False
    is_experimental: bool = False

class DockingExperimentItem(BaseModel):
    experiment_id: str
    timestamp: str
    target_pdb_id: str
    target_name: str
    mutation: str
    ligand_smiles: Optional[str] = None
    status: str # "SUCCESS", "FAILED"
    best_affinity_kcal_mol: Optional[float] = None
    num_modes: int = 0
    runtime_seconds: Optional[float] = None
    exit_code: int = 0
    is_benchmark: bool = False
    error_message: Optional[str] = None

# ==============================================================================
# 5. ADMET SCHEMAS (ADMETlab 3.0)
# ==============================================================================

class ADMETRequest(BaseModel):
    smiles: str = Field(..., description="Molecular SMILES string for ADMET profiling")

class ADMETResponse(BaseScientificResponse):
    smiles: str
    categories: List[str] = []
    summary: Dict[str, Dict[str, Any]] = {}
    is_experimental: bool = False

# ==============================================================================
# 6. BIOLOGICAL TARGET SCHEMAS (UniProt, ChEMBL, Reactome, AlphaFold, RCSB)
# ==============================================================================

class TargetSearchRequest(BaseModel):
    query: str = Field(..., description="Target gene name, protein symbol, or UniProt accession (e.g. EGFR, P00533)")
    mutation: Optional[str] = Field(default="L858R", description="Target oncogenic or missense mutation (e.g. L858R)")
    domain: Optional[str] = Field(default="kinase", description="Functional protein domain (e.g. kinase)")
    include_pathways: bool = True
    include_bioactivity: bool = True
    include_structures: bool = True

class TargetSearchResponse(BaseScientificResponse):
    query: str
    selected_mutation: Optional[str] = "L858R"
    uniprot_records: List[Dict[str, Any]] = []
    chembl_assays: List[Dict[str, Any]] = []
    reactome_pathways: List[Dict[str, Any]] = []
    alphafold_structure: Optional[Dict[str, Any]] = None
    rcsb_crystal: Optional[Dict[str, Any]] = None
    recommended_structure: Optional[Dict[str, Any]] = None
    redocking_benchmark: Optional[Dict[str, Any]] = None

# ==============================================================================
# 7. RESEARCH EVIDENCE SCHEMAS (PubMed & arXiv)
# ==============================================================================

class EvidenceSearchRequest(BaseModel):
    query: str = Field(..., description="Scientific search query (e.g. 'EGFR tyrosine kinase inhibitor')")
    max_pubmed: int = Field(default=5, ge=1, le=20)
    max_arxiv: int = Field(default=5, ge=1, le=20)

class EvidenceSearchResponse(BaseScientificResponse):
    query: str
    pubmed_evidence: List[Dict[str, Any]] = []
    arxiv_preprints: List[Dict[str, Any]] = []
    experimental_sources_count: int = 0
    computational_preprints_count: int = 0

# ==============================================================================
# 8. CELL RESPONSE ENGINE SCHEMAS (XPert)
# ==============================================================================

class XPertStatusResponse(BaseScientificResponse):
    module_status: str # 'Architecture_Verified_CPU_SDPA'
    checkpoint_available: bool
    weights_path: Optional[str] = None
    flash_attn_status: str # 'PyTorch_SDPA_CPU_Fallback_Active'
    gpu_required_for_full_perturbation: bool = True
    required_datasets: List[str]

# ==============================================================================
# 9. END-TO-END CANDIDATE EVALUATION PIPELINE SCHEMAS
# ==============================================================================

class PipelineRunRequest(BaseModel):
    target_name: str = Field(default="EGFR", description="Biological target name (e.g. 'EGFR', 'c-Abl')")
    target_protein: Optional[str] = Field(default=None, description="Compatibility alias for target_name (e.g. 'EGFR', 'c-Abl')")
    disease: Optional[str] = Field(default="NSCLC", description="Disease context (e.g. 'NSCLC', 'CML')")
    mutation: Optional[str] = Field(default="L858R", description="Target mutation state (e.g. 'L858R', 'Wild-Type')")
    target_pdb_id: Optional[str] = Field(default=None, description="Receptor PDB ID (e.g. '2ITZ', '1IEP')")
    num_candidates: int = Field(default=5, ge=1, le=50, description="Number of candidate molecules to generate")
    seed: Optional[int] = Field(default=42, description="Random seed")
    run_properties: bool = Field(default=True, description="Execute Chemprop D-MPNN property prediction")
    run_docking: bool = Field(default=True, description="Execute 3D docking simulation")
    run_admet: bool = Field(default=True, description="Query ADMETlab 3.0 profile")

    @model_validator(mode="before")
    @classmethod
    def resolve_target_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            tp = data.get("target_protein")
            tn = data.get("target_name")
            if tp and not tn:
                data["target_name"] = tp
            elif tn and not tp:
                data["target_protein"] = tn
        return data

class CandidateEvaluationResult(BaseModel):
    rank: int
    smiles: str
    formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    logp: Optional[float] = None
    lipinski_ro5: Optional[bool] = None
    chemprop_predicted_property: Optional[float] = None
    chemprop_status: str = Field(default="SUCCESS", description="SUCCESS | NOT_RUN | FAILED")
    chemprop_error: Optional[str] = None
    docking_best_affinity: Optional[float] = None
    docking_status: str = Field(default="SUCCESS", description="SUCCESS | NOT_RUN | FAILED")
    docking_error: Optional[str] = None
    admet_caco2: Optional[float] = None
    admet_herg: Optional[float] = None
    admet_dili: Optional[float] = None
    admet_ames: Optional[float] = None
    admet_status: str = Field(default="SUCCESS", description="SUCCESS | NOT_RUN | FAILED")
    admet_error: Optional[str] = None
    composite_rank_score: float
    is_experimental: bool = False

class PipelineRunResponse(BaseScientificResponse):
    run_id: str
    status: str # 'COMPLETED', 'PARTIAL_SUCCESS', 'FAILED'
    target_name: str
    target_pdb_id: Optional[str] = None
    mutation: Optional[str] = None
    disease: Optional[str] = None
    total_generated: int
    valid_count: int
    modules_status: Dict[str, str] = {}
    pipeline_errors: List[str] = []
    candidates: List[CandidateEvaluationResult] = []

# ==============================================================================
# 10. EXPERIMENTAL BIOACTIVITY & SELECTIVITY SCHEMAS
# ==============================================================================

class BioactivityRecordSchema(BaseModel):
    id: Optional[int] = None
    compound_name: str
    compound_chembl_id: str
    target_name: str
    target_uniprot_id: str
    target_chembl_id: str
    mutation: str # Wild-Type, L858R, L858R/T790M, C797S
    organism: str = "Homo sapiens"
    assay_id: str
    assay_description: str
    assay_type: str # Binding, Functional, Cellular
    assay_format: str # Biochemical Recombinant Enzyme, Cellular Autophosphorylation, Fluorescence Quenching Assay, etc.
    assay_method: Optional[str] = None # Fluorescence Quenching, ATP/NADH-Coupled, etc.
    measurement_type: str # IC50, Ki, Kd, GI50
    original_value: float
    original_units: str
    standard_value: float
    standard_units: str = "nM"
    standard_relation: str = "="
    uncertainty_value: Optional[float] = None
    replicate_count: Optional[int] = None
    cell_line: Optional[str] = None
    atp_concentration: Optional[str] = None
    source_database: str = "ChEMBL"
    primary_citation: str
    doi: Optional[str] = None
    pmid: Optional[str] = None
    publication_year: Optional[int] = None
    table_figure_ref: Optional[str] = None
    verification_status: str # VERIFIED_PRIMARY_SOURCE, VERIFIED_DATABASE_RECORD, etc.
    curator_notes: Optional[str] = None
    is_experimental: bool = True

class BioactivityBenchmarkResponse(BaseScientificResponse):
    target_protein: str = "EGFR (Homo sapiens, P00533)"
    reference_inhibitors_count: int
    total_records: int
    records: List[BioactivityRecordSchema]

class CompoundBioactivityResponse(BaseScientificResponse):
    compound_query: str
    records_count: int
    records: List[BioactivityRecordSchema]

class SelectivityCheckRequest(BaseModel):
    wt_assay_id: Optional[str] = Field(default=None, description="Assay ID or DB record ID for Wild-Type EGFR")
    mutant_assay_id: Optional[str] = Field(default=None, description="Assay ID or DB record ID for mutant EGFR")
    wt_record: Optional[BioactivityRecordSchema] = Field(default=None, description="Custom or raw WT measurement record")
    mutant_record: Optional[BioactivityRecordSchema] = Field(default=None, description="Custom or raw mutant measurement record")
    target_mutation: str = Field(default="L858R", description="Target mutation state, e.g. L858R or L858R/T790M")

class SelectivityCheckResponse(BaseScientificResponse):
    comparability_status: str # COMPARABLE, PROVISIONAL, PROVISIONAL_CELLULAR_CONTEXT, INCOMPARABLE_CROSS_STUDY, INCOMPARABLE_ENDPOINT, INCOMPARABLE, NOT_AVAILABLE
    selectivity_ratio: Optional[float] = None # Validated ratio (only for COMPARABLE)
    exploratory_ratio: Optional[float] = None # Contextual/exploratory ratio for provisional or cross-study
    selectivity_interpretation: str
    rejection_reason: Optional[str] = None
    wt_measurement: Optional[Dict[str, Any]] = None
    mutant_measurement: Optional[Dict[str, Any]] = None
    formula_used: str = "Selectivity Index = IC50(WT EGFR) / IC50(EGFR L858R) or Kd(WT) / Kd(Mutant)"
    irreversible_kinetics_note: Optional[str] = None
    cellular_context_note: Optional[str] = None

class CandidateBioactivityStatusResponse(BaseScientificResponse):
    candidate_id: str
    canonical_smiles: Optional[str] = None
    isomeric_smiles: Optional[str] = None
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    exact_molecular_weight: Optional[float] = None
    inchikey: Optional[str] = None
    target: str
    computational_profile: Dict[str, Any]
    experimental_bioactivity: Dict[str, Any]
    scientific_disclaimer: str
    required_validation_assays: List[Dict[str, Any]]

