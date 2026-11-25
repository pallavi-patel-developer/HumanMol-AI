"""
HumanMol AI - Database ORM Models
Defines tables for molecules, predictions, docking simulations,
literature evidence, and candidate evaluation pipelines.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from database.connection import Base

class Molecule(Base):
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, index=True)
    canonical_smiles = Column(String(1000), unique=True, index=True, nullable=False)
    molecular_formula = Column(String(100), nullable=True)
    molecular_weight = Column(Float, nullable=True)
    logp = Column(Float, nullable=True)
    hbd = Column(Integer, nullable=True)
    hba = Column(Integer, nullable=True)
    tpsa = Column(Float, nullable=True)
    rotatable_bonds = Column(Integer, nullable=True)
    lipinski_ro5 = Column(Boolean, nullable=True)
    source_engine = Column(String(100), default="User-Submitted")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    predictions = relationship("PredictionResult", back_populates="molecule", cascade="all, delete-orphan")
    dockings = relationship("DockingResult", back_populates="molecule", cascade="all, delete-orphan")
    evaluations = relationship("CandidateEvaluation", back_populates="molecule", cascade="all, delete-orphan")

class PredictionResult(Base):
    __tablename__ = "prediction_results"

    id = Column(Integer, primary_key=True, index=True)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    prediction_type = Column(String(50), nullable=False) # 'property', 'admet', 'cell_response'
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=True)
    model_provenance = Column(String(255), nullable=True)
    endpoint_name = Column(String(100), nullable=False)
    predicted_value = Column(Float, nullable=True)
    raw_data = Column(JSON, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)
    is_experimental = Column(Boolean, default=False) # False for in silico predictions
    created_at = Column(DateTime, default=datetime.utcnow)

    molecule = relationship("Molecule", back_populates="predictions")

class DockingResult(Base):
    __tablename__ = "docking_results"

    id = Column(Integer, primary_key=True, index=True)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    target_protein = Column(String(100), nullable=False) # e.g. '1IEP', 'c-Abl'
    best_affinity_kcal_mol = Column(Float, nullable=False)
    num_modes = Column(Integer, default=1)
    modes_json = Column(JSON, nullable=True)
    output_pdbqt_path = Column(String(500), nullable=True)
    is_experimental = Column(Boolean, default=False) # Computational simulation disclaimer
    created_at = Column(DateTime, default=datetime.utcnow)

    molecule = relationship("Molecule", back_populates="dockings")

class LiteratureEvidence(Base):
    __tablename__ = "literature_evidence"

    id = Column(Integer, primary_key=True, index=True)
    query_target = Column(String(200), index=True, nullable=False)
    source = Column(String(50), nullable=False) # 'PubMed' or 'arXiv'
    source_id = Column(String(100), index=True, nullable=False) # PMID or arXiv ID
    title = Column(String(500), nullable=False)
    abstract = Column(Text, nullable=True)
    authors = Column(JSON, nullable=True)
    publication_date = Column(String(50), nullable=True)
    doi = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)
    is_experimental = Column(Boolean, default=False) # True for clinical/assay papers, False for preprints
    created_at = Column(DateTime, default=datetime.utcnow)

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(100), unique=True, index=True, nullable=False)
    target_name = Column(String(200), nullable=False)
    status = Column(String(50), default="pending") # 'pending', 'running', 'completed', 'failed'
    total_candidates = Column(Integer, default=0)
    valid_candidates = Column(Integer, default=0)
    metadata_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    evaluations = relationship("CandidateEvaluation", back_populates="pipeline_run", cascade="all, delete-orphan")

class CandidateEvaluation(Base):
    __tablename__ = "candidate_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_run_id = Column(Integer, ForeignKey("pipeline_runs.id"), nullable=False)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    chemical_validity = Column(Boolean, default=True)
    lipinski_passed = Column(Boolean, default=False)
    chemprop_predicted_property = Column(Float, nullable=True)
    docking_best_affinity = Column(Float, nullable=True)
    admet_caco2 = Column(Float, nullable=True)
    admet_herg = Column(Float, nullable=True)
    admet_dili = Column(Float, nullable=True)
    admet_ames = Column(Float, nullable=True)
    is_experimental_verified = Column(Boolean, default=False) # Explicit separation
    composite_rank_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    pipeline_run = relationship("PipelineRun", back_populates="evaluations")
    molecule = relationship("Molecule", back_populates="evaluations")

class ExperimentalBioactivity(Base):
    __tablename__ = "experimental_bioactivities"

    id = Column(Integer, primary_key=True, index=True)
    compound_name = Column(String(100), index=True, nullable=False) # e.g. Gefitinib, Erlotinib, Afatinib, Osimertinib
    compound_chembl_id = Column(String(50), index=True, nullable=False) # e.g. CHEMBL68920
    target_name = Column(String(200), nullable=False) # e.g. Epidermal growth factor receptor
    target_uniprot_id = Column(String(50), nullable=False) # P00533
    target_chembl_id = Column(String(50), nullable=False) # CHEMBL203
    mutation = Column(String(100), index=True, nullable=False) # Wild-Type, L858R, L858R/T790M, C797S
    organism = Column(String(100), default="Homo sapiens")
    assay_id = Column(String(100), index=True, nullable=False) # e.g. CHEMBL674637, Cross2014-T1-WT
    assay_description = Column(Text, nullable=False)
    assay_type = Column(String(50), nullable=False) # Binding, Functional, Cellular
    assay_format = Column(String(100), nullable=False) # Biochemical Recombinant Enzyme, Cellular Autophosphorylation, Proliferation
    assay_method = Column(String(100), nullable=True) # Fluorescence Quenching, ATP/NADH-Coupled, DELFIA, ELISA
    measurement_type = Column(String(50), index=True, nullable=False) # IC50, Ki, Kd, GI50, EC50
    original_value = Column(Float, nullable=False)
    original_units = Column(String(50), nullable=False) # nM, uM
    standard_value = Column(Float, nullable=False) # Normalized to nM
    standard_units = Column(String(50), default="nM")
    standard_relation = Column(String(10), default="=") # '=', '<', '>', '~'
    uncertainty_value = Column(Float, nullable=True) # +/- error
    replicate_count = Column(Integer, nullable=True) # n replicates
    cell_line = Column(String(100), nullable=True) # e.g. Ba/F3, H1975, PC-9, LoVo, A431
    atp_concentration = Column(String(100), nullable=True) # e.g. 10 uM, Km ATP, 1 mM
    source_database = Column(String(100), default="ChEMBL")
    primary_citation = Column(Text, nullable=False)
    doi = Column(String(150), nullable=True)
    pmid = Column(String(50), nullable=True)
    publication_year = Column(Integer, nullable=True)
    table_figure_ref = Column(String(100), nullable=True) # e.g. Table 1, Fig 2B
    verification_status = Column(String(50), nullable=False) # VERIFIED_PRIMARY_SOURCE, VERIFIED_DATABASE_RECORD, SECONDARY_SOURCE_ONLY, UNVERIFIED, INCOMPARABLE
    curator_notes = Column(Text, nullable=True)
    is_experimental = Column(Boolean, default=True) # Always True for wet-lab data
    created_at = Column(DateTime, default=datetime.utcnow)

class KinaseSelectivity(Base):
    __tablename__ = "kinase_selectivities"

    id = Column(Integer, primary_key=True, index=True)
    compound_name = Column(String(100), index=True, nullable=False)
    compound_chembl_id = Column(String(50), index=True, nullable=False)
    wt_bioactivity_id = Column(Integer, ForeignKey("experimental_bioactivities.id"), nullable=False)
    mutant_bioactivity_id = Column(Integer, ForeignKey("experimental_bioactivities.id"), nullable=False)
    target_mutation = Column(String(100), index=True, nullable=False) # e.g. L858R, L858R/T790M
    comparability_status = Column(String(50), nullable=False) # COMPARABLE, INCOMPARABLE
    comparability_notes = Column(Text, nullable=True)
    selectivity_ratio = Column(Float, nullable=True) # WT IC50 / Mutant IC50
    selectivity_interpretation = Column(String(100), nullable=False) # Mutant-Selective, Equipotent, Wild-Type-Selective, Incomparable
    created_at = Column(DateTime, default=datetime.utcnow)

    wt_bioactivity = relationship("ExperimentalBioactivity", foreign_keys=[wt_bioactivity_id])
    mutant_bioactivity = relationship("ExperimentalBioactivity", foreign_keys=[mutant_bioactivity_id])

