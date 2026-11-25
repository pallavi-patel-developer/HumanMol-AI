/**
 * HumanMol AI - TypeScript Type Definitions
 * Directly aligned with FastAPI Scientific Engine Pydantic Schemas.
 */

export interface BaseScientificResponse {
  success: boolean;
  message?: string | null;
  execution_time_seconds?: number | null;
  disclaimer: string;
}

// 0. System Health
export interface DatabaseStatus {
  active_backend: 'sqlite' | 'postgresql';
  is_fallback: boolean;
  postgres_port_open: boolean;
  postgres_auth_error?: string | null;
  sqlite_path?: string;
  notes?: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
  version: string;
  database: DatabaseStatus;
  engines: Record<string, string>;
  disclaimer: string;
}

// 1. Chemistry (RDKit)
export interface MolecularDescriptorResponse extends BaseScientificResponse {
  valid: boolean;
  smiles?: string | null;
  formula?: string | null;
  molecular_weight?: number | null;
  logp?: number | null;
  hbd?: number | null;
  hba?: number | null;
  tpsa?: number | null;
  rotatable_bonds?: number | null;
  lipinski_ro5?: boolean | null;
  error?: string | null;
}

// 2. Generation (REINVENT4)
export interface GeneratedMolecule {
  smiles: string;
  nll?: number | null;
  chemical_validity: boolean;
  formula?: string | null;
  molecular_weight?: number | null;
  logp?: number | null;
  tpsa?: number | null;
  lipinski_ro5?: boolean | null;
}

export interface GenerationResponse extends BaseScientificResponse {
  total_generated: number;
  valid_count: number;
  molecules: GeneratedMolecule[];
  model_version: string;
  prior_provenance: string;
  workflow_type?: string;
  target_conditioning?: boolean;
  reward_optimization?: boolean;
  nll_description?: string;
}

// 3. Property Prediction (Chemprop)
export interface PropertyPredictionItem {
  smiles: string;
  predicted_property?: number | null;
  denormalized_property?: number | null;
  status: string;
  model_type: string;
  is_experimental: boolean;
}

export interface PropertyPredictionResponse extends BaseScientificResponse {
  total_evaluated: number;
  predictions: PropertyPredictionItem[];
  endpoint_name?: string;
  endpoint_description?: string;
  target_units?: string;
  model_checkpoint?: string;
  training_dataset?: string;
  normalization_method?: string;
  validation_metrics?: Record<string, number>;
}

// 4. Docking (AutoDock Vina)
export interface DockingMode {
  mode: number;
  affinity_kcal_mol: number;
  rmsd_lb: number;
  rmsd_ub: number;
}

export interface DockingResponse extends BaseScientificResponse {
  experiment_id: string;
  target_protein: string;
  target_pdb_id: string;
  mutation?: string | null;
  ligand_smiles?: string | null;
  best_affinity_kcal_mol?: number | null;
  num_modes: number;
  modes: DockingMode[];
  output_pdbqt_path?: string | null;
  status?: string;
  error_message?: string | null;
  exit_code?: number;
  vina_command?: string | null;
  receptor_sha256?: string | null;
  ligand_sha256?: string | null;
  is_benchmark?: boolean;
  is_experimental: boolean;
}

export interface DockingExperimentItem {
  experiment_id: string;
  timestamp: string;
  target_pdb_id: string;
  target_name: string;
  mutation: string;
  ligand_smiles?: string | null;
  status: string;
  best_affinity_kcal_mol?: number | null;
  num_modes: number;
  runtime_seconds?: number | null;
  exit_code: number;
  is_benchmark: boolean;
  error_message?: string | null;
}

// 5. ADMET (ADMETlab 3.0)
export interface ADMETResponse extends BaseScientificResponse {
  smiles: string;
  categories: string[];
  summary: Record<string, Record<string, any>>;
  is_experimental: boolean;
}

// 6. Target Intelligence (UniProt, ChEMBL, Reactome, AlphaFold, RCSB)
export interface UniProtRecord {
  accession: string;
  primaryAccession?: string;
  id?: string;
  uniProtkbId?: string;
  protein_name?: string;
  gene_name?: string;
  organism?: string;
  common_name?: string;
  sequence_length?: number;
  function_summary?: string;
  is_reviewed?: boolean;
  pdb_ids?: string[];
}

export interface ChEMBLAssayRecord {
  activity_id?: number | string;
  assay_chembl_id?: string;
  molecule_chembl_id?: string;
  target_chembl_id?: string;
  target_pref_name?: string;
  assay_type?: string;
  assay_type_code?: string;
  organism?: string;
  standard_type?: string;
  standard_value?: number | null;
  standard_units?: string;
  pchembl_value?: number | null;
  canonical_smiles?: string;
  assay_description?: string;
  source?: string;
  is_experimental?: boolean;
}

export interface ReactomePathwayRecord {
  stId: string;
  displayName: string;
  name?: string;
  speciesName?: string;
  species?: string;
  url?: string;
  is_disease?: boolean;
  database?: string;
  type?: string;
}

export interface RecommendedStructure {
  pdb_id: string;
  title?: string;
  organism?: string;
  mutation?: string;
  mutation_verified?: boolean;
  mutation_residue?: { seq_id: number; wt: string; mut: string; chain: string };
  domain_name?: string;
  domain_residues?: string;
  experimental_method?: string;
  resolution?: number;
  chain_id?: string;
  is_experimental: boolean;
  is_alphafold: boolean;
  source?: string;
  rcsb_url?: string;
  bound_ligand?: {
    comp_id: string;
    name: string;
    chemical_formula?: string;
    formula_weight?: number;
    smiles?: string;
    binding_pocket?: {
      center_x: number;
      center_y: number;
      center_z: number;
      size_x: number;
      size_y: number;
      size_z: number;
    };
  };
  redocking_validation?: {
    status: string;
    software: string;
    exhaustiveness: number;
    best_affinity_kcal_mol: number;
    core_rmsd_angstrom: number;
    all_heavy_rmsd_angstrom: number;
    best_pose_rmsd_angstrom: number;
    heavy_atom_count: number;
    reproducibility: string;
  };
}

export interface TargetSearchResponse extends BaseScientificResponse {
  query: string;
  selected_mutation?: string;
  uniprot_records: UniProtRecord[];
  chembl_assays: ChEMBLAssayRecord[];
  reactome_pathways: ReactomePathwayRecord[];
  alphafold_structure?: {
    uniprot_accession?: string;
    entry_id?: string;
    pdb_url?: string;
    cif_url?: string;
    pae_image_url?: string;
    has_model?: boolean;
    is_experimental?: boolean;
    is_alphafold?: boolean;
    method?: string;
    provenance?: string;
    disclaimer?: string;
  } | null;
  rcsb_crystal?: RecommendedStructure | null;
  recommended_structure?: RecommendedStructure | null;
  redocking_benchmark?: any;
}

// 7. Research Evidence (PubMed & arXiv)
export interface PubMedArticle {
  pmid: string;
  title: string;
  authors?: string[];
  journal?: string;
  pub_date?: string;
  abstract?: string;
  doi?: string;
  url?: string;
  is_peer_reviewed: boolean;
}

export interface ArXivArticle {
  arxiv_id: string;
  title: string;
  authors?: string[];
  summary?: string;
  published?: string;
  pdf_url?: string;
  primary_category?: string;
  is_preprint: boolean;
}

export interface EvidenceSearchResponse extends BaseScientificResponse {
  query: string;
  pubmed_evidence: PubMedArticle[];
  arxiv_preprints: ArXivArticle[];
  experimental_sources_count: number;
  computational_preprints_count: number;
}

// 8. XPert Cell Response Status
export interface XPertStatusResponse extends BaseScientificResponse {
  module_status: string;
  checkpoint_available: boolean;
  weights_path?: string | null;
  flash_attn_status: string;
  gpu_required_for_full_perturbation: boolean;
  required_datasets: string[];
}

// 9. Pipeline & Candidate Evaluation
export interface CandidateEvaluationResult {
  rank: number;
  smiles: string;
  formula?: string | null;
  molecular_weight?: number | null;
  logp?: number | null;
  lipinski_ro5?: boolean | null;
  chemprop_predicted_property?: number | null;
  chemprop_status?: 'SUCCESS' | 'NOT_RUN' | 'FAILED';
  chemprop_error?: string | null;
  docking_best_affinity?: number | null;
  docking_status?: 'SUCCESS' | 'NOT_RUN' | 'FAILED';
  docking_error?: string | null;
  admet_caco2?: number | null;
  admet_herg?: number | null;
  admet_dili?: number | null;
  admet_ames?: number | null;
  admet_status?: 'SUCCESS' | 'NOT_RUN' | 'FAILED';
  admet_error?: string | null;
  composite_rank_score: number;
  is_experimental: boolean;
}

export interface PipelineRunResponse extends BaseScientificResponse {
  run_id: string;
  status: string;
  target_name: string;
  target_pdb_id?: string | null;
  mutation?: string | null;
  disease?: string | null;
  total_generated: number;
  valid_count: number;
  modules_status?: Record<string, string>;
  pipeline_errors?: string[];
  candidates: CandidateEvaluationResult[];
}

// 10. Experimental Bioactivity & Selectivity
export interface BioactivityRecord {
  id?: number;
  compound_name: string;
  compound_chembl_id: string;
  target_name: string;
  target_uniprot_id: string;
  target_chembl_id: string;
  mutation: string;
  organism: string;
  assay_id: string;
  assay_description: string;
  assay_type: string;
  assay_format: string;
  assay_method?: string | null;
  measurement_type: string;
  original_value: number;
  original_units: string;
  standard_value: number;
  standard_units: string;
  standard_relation: string;
  uncertainty_value?: number | null;
  replicate_count?: number | null;
  cell_line?: string | null;
  atp_concentration?: string | null;
  source_database: string;
  primary_citation: string;
  doi?: string | null;
  pmid?: string | null;
  publication_year?: number | null;
  table_figure_ref?: string | null;
  verification_status: 'VERIFIED_PRIMARY_SOURCE' | 'VERIFIED_DATABASE_RECORD' | 'SECONDARY_SOURCE_ONLY' | 'UNVERIFIED' | 'INCOMPARABLE' | 'UNTESTED';
  curator_notes?: string | null;
  is_experimental: boolean;
}

export interface BioactivityBenchmarkResponse extends BaseScientificResponse {
  target_protein: string;
  reference_inhibitors_count: number;
  total_records: number;
  records: BioactivityRecord[];
}

export interface CompoundBioactivityResponse extends BaseScientificResponse {
  compound_query: string;
  records_count: number;
  records: BioactivityRecord[];
}

export interface SelectivityCheckRequest {
  wt_assay_id?: string;
  mutant_assay_id?: string;
  wt_record?: BioactivityRecord;
  mutant_record?: BioactivityRecord;
  target_mutation?: string;
}

export interface SelectivityCheckResponse extends BaseScientificResponse {
  comparability_status: 'COMPARABLE' | 'PROVISIONAL' | 'PROVISIONAL_CELLULAR_CONTEXT' | 'INCOMPARABLE' | 'INCOMPARABLE_CROSS_STUDY' | 'INCOMPARABLE_ENDPOINT' | 'NOT_AVAILABLE';
  selectivity_ratio?: number | null;
  exploratory_ratio?: number | null;
  selectivity_interpretation: string;
  rejection_reason?: string | null;
  wt_measurement?: BioactivityRecord | null;
  mutant_measurement?: BioactivityRecord | null;
  formula_used: string;
  irreversible_kinetics_note?: string | null;
  cellular_context_note?: string | null;
}

export interface CandidateBioactivityStatusResponse extends BaseScientificResponse {
  candidate_id: string;
  canonical_smiles?: string | null;
  isomeric_smiles?: string | null;
  molecular_formula?: string | null;
  molecular_weight?: number | null;
  exact_molecular_weight?: number | null;
  inchikey?: string | null;
  target: string;
  computational_profile: Record<string, any>;
  experimental_bioactivity: Record<string, any>;
  scientific_disclaimer: string;
  required_validation_assays: Array<{
    step: number;
    assay_name: string;
    objective?: string;
    status: string;
  }>;
}

