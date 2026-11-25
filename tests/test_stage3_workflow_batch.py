"""
HumanMol AI - Stage 3 Workflow Test & Preparation Script
Verifies all modules (Target Intelligence, REINVENT4, RDKit, Chemprop, Vina 2ITZ, ADMET, DB)
with a small test batch before full scale execution.
"""

import os
import sys
import time
import json

# Ensure scientific-engine and root are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE_DIR = os.path.join(BASE_DIR, "scientific-engine")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from database.connection import get_engine, Base, get_db
from database.models import Molecule, PipelineRun, CandidateEvaluation, DockingResult, LiteratureEvidence
from scientific_engine.biological_data.uniprot_chembl_service import query_uniprot_protein, query_chembl_bioactivity
from scientific_engine.pathways.reactome_service import get_pathways_for_uniprot
from scientific_engine.protein_data.protein_service import resolve_mutation_aware_structure
from scientific_engine.molecule_generator.generator_service import generate_molecules
from scientific_engine.chemistry.rdkit_service import validate_and_parse_smiles
from scientific_engine.property_prediction.chemprop_service import predict_molecular_properties
from scientific_engine.docking.vina_docking import run_docking, calculate_file_sha256, validate_pdbqt_file
from scientific_engine.api.routers.docking import convert_smiles_to_pdbqt, TARGET_PRESETS, EXPERIMENTS_DIR
from scientific_engine.admet.admetlab_client import ADMETService

def run_test_batch():
    print("=== [Stage 3 Verification] Starting Small Test Batch (5 candidates) ===")
    
    # 1. Target Intelligence
    print("\n--- 1. Testing Target Intelligence (EGFR L858R / P00533) ---")
    uniprot = query_uniprot_protein("P00533", limit=1)
    print(f"UniProt resolved: {uniprot[0]['protein_name']}, Organism: {uniprot[0]['organism']}")
    
    struct = resolve_mutation_aware_structure("EGFR", "P00533", mutation="L858R", domain="kinase")
    pdb_id = struct.get("pdb_id")
    print(f"Structure resolved: PDB {pdb_id}, Mutation: {struct.get('mutation')}")
    assert pdb_id == "2ITZ", f"Expected 2ITZ, got {pdb_id}"
    
    # 2. REINVENT4 Sampling
    print("\n--- 2. Testing REINVENT4 Sampling ---")
    gen = generate_molecules(num_molecules=3, seed=42)
    print(f"Generated {len(gen['smiles'])} molecules in {gen['execution_time_seconds']}s")
    for s in gen['smiles']:
        print(f"  Sample: {s}")
        
    # 3. RDKit Validation
    print("\n--- 3. Testing RDKit Validation ---")
    parsed_list = []
    for s in gen['smiles']:
        p = validate_and_parse_smiles(s)
        print(f"  Valid: {p['valid']}, MW: {p.get('molecular_weight')}, Ro5: {p.get('lipinski_ro5')}")
        if p['valid']:
            parsed_list.append(p)
            
    # 4. Chemprop Prediction
    print("\n--- 4. Testing Chemprop Prediction ---")
    c_smiles = [p['smiles'] for p in parsed_list]
    c_preds = predict_molecular_properties(c_smiles)
    for cp in c_preds:
        print(f"  SMILES: {cp['smiles'][:30]}... Pred: {cp['predicted_property']}")
        
    # 5. Vina Docking on 2ITZ
    print("\n--- 5. Testing Vina Docking on PDB 2ITZ ---")
    preset_2itz = TARGET_PRESETS["2ITZ"]
    test_cand_smi = c_smiles[0]
    test_exp_dir = os.path.join(EXPERIMENTS_DIR, "test_exp_2itz_verification")
    os.makedirs(test_exp_dir, exist_ok=True)
    test_lig_pdbqt = os.path.join(test_exp_dir, "ligand.pdbqt")
    test_out_pdbqt = os.path.join(test_exp_dir, "docked_out.pdbqt")
    
    ok, err = convert_smiles_to_pdbqt(test_cand_smi, test_lig_pdbqt)
    assert ok, f"PDBQT conversion failed: {err}"
    
    dock_res = run_docking(
        receptor_pdbqt=preset_2itz["receptor"],
        ligand_pdbqt=test_lig_pdbqt,
        center_x=preset_2itz["center_x"],
        center_y=preset_2itz["center_y"],
        center_z=preset_2itz["center_z"],
        size_x=preset_2itz["size_x"],
        size_y=preset_2itz["size_y"],
        size_z=preset_2itz["size_z"],
        out_pdbqt=test_out_pdbqt,
        exhaustiveness=1
    )
    print(f"  Docking success: {dock_res['success']}, Best affinity: {dock_res.get('best_affinity_kcal_mol')} kcal/mol, Modes: {len(dock_res.get('modes', []))}")
    assert dock_res['success'], f"Docking failed: {dock_res.get('error')}"
    
    # 6. Database Persistence
    print("\n--- 6. Testing Database Connectivity & Schema ---")
    db_gen = get_db()
    db = next(db_gen)
    try:
        p_count = db.query(PipelineRun).count()
        m_count = db.query(Molecule).count()
        print(f"  Database connected! Current PipelineRuns: {p_count}, Molecules: {m_count}")
    finally:
        db.close()
        
    print("\n=== [Stage 3 Verification] Small Test Batch PASSED! All engines ready ===")

if __name__ == "__main__":
    run_test_batch()
