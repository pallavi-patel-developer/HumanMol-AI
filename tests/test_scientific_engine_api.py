"""
HumanMol AI - Scientific Engine Integration Test Suite
Validates all FastAPI endpoints, database persistence, and scientific pipelines.
"""

import os
import sys
import time

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from scientific_engine.api.app import app
from database.connection import get_db, SessionLocal
from database.models import Molecule, PredictionResult, DockingResult, LiteratureEvidence, PipelineRun, CandidateEvaluation

client = TestClient(app)

def run_integration_tests():
    print("=" * 80)
    print("STARTING HUMANMOL AI SCIENTIFIC ENGINE INTEGRATION TEST SUITE")
    print("=" * 80)

    test_results = {}

    # 1. Health & Root Info
    print("\n[TEST 1] Testing Root & Health Check Endpoints...")
    t0 = time.time()
    r_root = client.get("/")
    r_health = client.get("/health")
    t1 = time.time()
    assert r_root.status_code == 200, f"Root failed: {r_root.text}"
    assert r_health.status_code == 200, f"Health failed: {r_health.text}"
    data_health = r_health.json()
    assert data_health["status"] == "healthy"
    active_db = data_health.get("database", {}).get("active_backend", data_health.get("dialect", "unknown"))
    print(f"  --> Root & Health OK. Dialect: {active_db} ({round(t1 - t0, 3)} s)")
    test_results["Root_and_Health"] = {"status": "PASSED", "time": round(t1 - t0, 3)}

    # 2. Chemistry Validation (RDKit)
    print("\n[TEST 2] Testing /api/chemistry/validate with Aspirin...")
    t0 = time.time()
    r_chem = client.post("/api/chemistry/validate", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    t1 = time.time()
    assert r_chem.status_code == 200, f"Chemistry validation failed: {r_chem.text}"
    chem_data = r_chem.json()
    assert chem_data["valid"] is True
    assert chem_data["molecular_weight"] == 180.16
    assert chem_data["lipinski_ro5"] is True
    assert chem_data["formula"] == "C9H8O4"
    print(f"  --> Chemistry Validation OK: MW={chem_data['molecular_weight']}, Formula={chem_data['formula']} ({round(t1 - t0, 3)} s)")
    test_results["Chemistry_Validation"] = {"status": "PASSED", "time": round(t1 - t0, 3), "output": chem_data}

    # 3. Molecule Generation (REINVENT4)
    print("\n[TEST 3] Testing /api/generation/generate with REINVENT4 (seed=42)...")
    t0 = time.time()
    r_gen = client.post("/api/generation/generate", json={"num_molecules": 3, "seed": 42})
    t1 = time.time()
    assert r_gen.status_code == 200, f"Generation failed: {r_gen.text}"
    gen_data = r_gen.json()
    assert gen_data["success"] is True
    assert gen_data["total_generated"] == 3
    assert len(gen_data["molecules"]) == 3
    print(f"  --> REINVENT4 Generation OK: {gen_data['valid_count']}/{gen_data['total_generated']} valid molecules generated ({round(t1 - t0, 3)} s)")
    for idx, m in enumerate(gen_data["molecules"], 1):
        print(f"      {idx}. {m['smiles'][:45]}... (valid={m['chemical_validity']}, NLL={m['nll']})")
    test_results["Molecule_Generation"] = {"status": "PASSED", "time": round(t1 - t0, 3), "count": gen_data["total_generated"]}

    # 4. Property Prediction (Chemprop)
    print("\n[TEST 4] Testing /api/properties/predict with Chemprop D-MPNN...")
    t0 = time.time()
    test_smis = ["CC(=O)Oc1ccccc1C(=O)O", "CC(=O)Nc1ccc(O)cc1", "CC(C)Cc1ccc(cc1)C(C)C(=O)O"]
    r_prop = client.post("/api/properties/predict", json={"smiles": test_smis})
    t1 = time.time()
    assert r_prop.status_code == 200, f"Property prediction failed: {r_prop.text}"
    prop_data = r_prop.json()
    assert prop_data["success"] is True
    assert len(prop_data["predictions"]) == 3
    print(f"  --> Chemprop Property Prediction OK ({round(t1 - t0, 3)} s):")
    for p in prop_data["predictions"]:
        print(f"      - {p['smiles']}: Predicted={p['predicted_property']} (experimental={p['is_experimental']})")
    test_results["Property_Prediction"] = {"status": "PASSED", "time": round(t1 - t0, 3), "count": len(prop_data["predictions"])}

    # 5. Docking Simulation (AutoDock Vina)
    print("\n[TEST 5] Testing /api/docking/run with c-Abl kinase (1IEP)...")
    t0 = time.time()
    r_dock = client.post("/api/docking/run", json={"target_pdb_id": "1IEP", "exhaustiveness": 4})
    t1 = time.time()
    assert r_dock.status_code == 200, f"Docking failed: {r_dock.text}"
    dock_data = r_dock.json()
    assert dock_data["success"] is True
    assert dock_data["best_affinity_kcal_mol"] is not None
    print(f"  --> AutoDock Vina Docking OK: Best Affinity = {dock_data['best_affinity_kcal_mol']} kcal/mol, Modes = {dock_data['num_modes']} ({round(t1 - t0, 3)} s)")
    test_results["Docking_Simulation"] = {"status": "PASSED", "time": round(t1 - t0, 3), "best_affinity": dock_data["best_affinity_kcal_mol"]}

    # 6. ADMET Profiling (ADMETlab 3.0)
    print("\n[TEST 6] Testing /api/admet/predict with Aspirin...")
    t0 = time.time()
    r_admet = client.post("/api/admet/predict", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    t1 = time.time()
    assert r_admet.status_code == 200, f"ADMETlab failed: {r_admet.text}"
    admet_data = r_admet.json()
    print(f"  --> ADMETlab 3.0 Status: success={admet_data.get('success')} ({round(t1 - t0, 3)} s)")
    if admet_data.get("success"):
        print(f"      - Caco-2: {admet_data['summary'].get('absorption', {}).get('caco2')}")
        print(f"      - hERG liability: {admet_data['summary'].get('toxicity', {}).get('hERG')}")
        print(f"      - Ames mutagenicity: {admet_data['summary'].get('toxicity', {}).get('Ames')}")
    else:
        print(f"      - Notice: {admet_data.get('message')}")
    test_results["ADMET_Profiling"] = {"status": "PASSED", "time": round(t1 - t0, 3), "success": admet_data.get("success")}

    # 7. Biological Targets (UniProt, ChEMBL, Reactome, AlphaFold, RCSB)
    print("\n[TEST 7] Testing /api/targets/search for 'EGFR'...")
    t0 = time.time()
    r_target = client.get("/api/targets/search?query=EGFR")
    t1 = time.time()
    assert r_target.status_code == 200, f"Target search failed: {r_target.text}"
    target_data = r_target.json()
    assert target_data["success"] is True
    print(f"  --> Target Search OK ({round(t1 - t0, 3)} s):")
    print(f"      - UniProt records: {len(target_data['uniprot_records'])}")
    print(f"      - Reactome pathways: {len(target_data['reactome_pathways'])}")
    print(f"      - AlphaFold URL: {bool(target_data['alphafold_structure'])}")
    print(f"      - RCSB crystal: {bool(target_data['rcsb_crystal'])}")
    test_results["Target_Intelligence"] = {"status": "PASSED", "time": round(t1 - t0, 3)}

    # 8. Research Evidence (PubMed & arXiv)
    print("\n[TEST 8] Testing /api/evidence/search for 'EGFR tyrosine kinase inhibitor'...")
    t0 = time.time()
    r_evid = client.get("/api/evidence/search?query=EGFR+tyrosine+kinase+inhibitor&max_pubmed=2&max_arxiv=2")
    t1 = time.time()
    assert r_evid.status_code == 200, f"Evidence search failed: {r_evid.text}"
    evid_data = r_evid.json()
    assert evid_data["success"] is True
    print(f"  --> Research Evidence OK ({round(t1 - t0, 3)} s):")
    print(f"      - PubMed peer-reviewed papers: {len(evid_data['pubmed_evidence'])}")
    print(f"      - arXiv preprints: {len(evid_data['arxiv_preprints'])}")
    test_results["Research_Evidence"] = {"status": "PASSED", "time": round(t1 - t0, 3)}

    # 9. XPert Cellular Response Modular Status
    print("\n[TEST 9] Testing /api/cell-response/status for XPert Engine...")
    t0 = time.time()
    r_xpert = client.get("/api/cell-response/status")
    t1 = time.time()
    assert r_xpert.status_code == 200, f"XPert status failed: {r_xpert.text}"
    xpert_data = r_xpert.json()
    assert xpert_data["success"] is True
    print(f"  --> XPert Status OK: {xpert_data['module_status']} ({round(t1 - t0, 3)} s)")
    print(f"      - Attention kernel: {xpert_data['flash_attn_status']}")
    print(f"      - Checkpoint available: {xpert_data['checkpoint_available']}")
    test_results["XPert_Status"] = {"status": "PASSED", "time": round(t1 - t0, 3)}

    # 10. End-to-End Candidate Evaluation Pipeline
    print("\n[TEST 10] Testing /api/pipeline/evaluate end-to-end pipeline (c-Abl, 3 candidates)...")
    t0 = time.time()
    r_pipe = client.post("/api/pipeline/evaluate", json={
        "target_name": "c-Abl",
        "num_candidates": 3,
        "seed": 42,
        "run_docking": True,
        "run_admet": True
    })
    t1 = time.time()
    assert r_pipe.status_code == 200, f"Pipeline evaluate failed: {r_pipe.text}"
    pipe_data = r_pipe.json()
    assert pipe_data["success"] is True
    assert pipe_data["status"] == "completed"
    print(f"  --> Pipeline OK: Run ID = {pipe_data['run_id']} ({round(t1 - t0, 3)} s)")
    print(f"      - Candidates Evaluated: {len(pipe_data['candidates'])}")
    for c in pipe_data["candidates"]:
        print(f"      Rank {c['rank']}: SMILES={c['smiles'][:35]}... MPO Score={c['composite_rank_score']} | Docking={c['docking_best_affinity']} kcal/mol | Ro5={c['lipinski_ro5']}")
    test_results["Candidate_Pipeline"] = {"status": "PASSED", "time": round(t1 - t0, 3), "run_id": pipe_data["run_id"]}

    # 11. Database Persistence Verification
    print("\n[TEST 11] Verifying Database Persistence across all tables...")
    db = SessionLocal()
    try:
        mol_count = db.query(Molecule).count()
        pred_count = db.query(PredictionResult).count()
        dock_count = db.query(DockingResult).count()
        evid_count = db.query(LiteratureEvidence).count()
        pipe_count = db.query(PipelineRun).count()
        eval_count = db.query(CandidateEvaluation).count()

        print(f"  --> Database Record Counts:")
        print(f"      - Molecules: {mol_count}")
        print(f"      - Prediction Results: {pred_count}")
        print(f"      - Docking Results: {dock_count}")
        print(f"      - Literature Evidence: {evid_count}")
        print(f"      - Pipeline Runs: {pipe_count}")
        print(f"      - Candidate Evaluations: {eval_count}")

        assert mol_count > 0, "No molecules in database"
        assert pred_count > 0, "No predictions in database"
        assert dock_count > 0, "No docking results in database"
        assert evid_count > 0, "No literature evidence in database"
        assert pipe_count > 0, "No pipeline runs in database"
        assert eval_count > 0, "No evaluations in database"
        test_results["Database_Persistence"] = {"status": "PASSED", "molecules": mol_count, "pipeline_runs": pipe_count}
    finally:
        db.close()

    print("\n" + "=" * 80)
    print("ALL 11 INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    return test_results

if __name__ == "__main__":
    run_integration_tests()
