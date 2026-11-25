"""
HumanMol AI - Docking Isolation & State Integrity Verification Suite
Executes all 7 test cases specified in the Stage 2 Critical Fix:
1. EGFR L858R + 2ITZ + Gefitinib benchmark redocking.
2. EGFR L858R + a generated candidate.
3. C-Abl + a separate ligand.
4. Intentionally invalid ligand input.
5. Missing receptor file.
6. Vina execution failure (e.g. invalid box dimensions).
7. Retry after failure.
Verifies experiment isolation, distinct experiment IDs, lack of cross-contamination,
and authentic error diagnostics.
"""

import os
import sys
import json
import unittest

# Add workspace root and scientific-engine to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scientific-engine")))

from api.routers.docking import execute_docking, TARGET_PRESETS, BASE_DOCKING_DIR, EXPERIMENTS_DIR
from schemas.schemas import DockingRequest, DockingResponse
from database.connection import get_db

class TestDockingIsolationAndIntegrity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_gen = get_db()
        cls.db = next(cls.db_gen)
        print("\n" + "="*80)
        print("STARTING HUMANMOL AI DOCKING ISOLATION & STATE INTEGRITY AUDIT")
        print("="*80)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.db.close()
        except Exception:
            pass

    def test_01_egfr_l858r_benchmark_redocking(self):
        """Test 1: EGFR L858R + 2ITZ + Gefitinib benchmark redocking."""
        print("\n--- TEST 1: EGFR L858R + 2ITZ + Gefitinib Benchmark Redocking ---")
        req = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles=TARGET_PRESETS["2ITZ"]["reference_smiles"],
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Status: {res.status}")
        print(f"  Best Affinity: {res.best_affinity_kcal_mol} kcal/mol")
        print(f"  Modes Count: {res.num_modes}")
        print(f"  Exit Code: {res.exit_code}")
        print(f"  Vina Command: {res.vina_command}")
        print(f"  Receptor SHA256: {res.receptor_sha256}")

        self.assertTrue(res.success)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(res.target_pdb_id, "2ITZ")
        self.assertIn("EGFR L858R", res.target_protein)
        self.assertIsNotNone(res.best_affinity_kcal_mol)
        self.assertLess(res.best_affinity_kcal_mol, -5.0) # Strongly negative binding energy
        self.assertGreaterEqual(res.num_modes, 1)
        self.assertTrue(res.is_benchmark)

    def test_02_egfr_l858r_generated_candidate(self):
        """Test 2: EGFR L858R + a generated candidate."""
        print("\n--- TEST 2: EGFR L858R + Generated Candidate Docking ---")
        candidate_smiles = "C(Cc1nnn(c1)Cc1cccc2ncccc21)(C)(C)C" # Valid novel candidate from REINVENT
        req = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles=candidate_smiles,
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Status: {res.status}")
        print(f"  Best Affinity: {res.best_affinity_kcal_mol} kcal/mol")
        print(f"  Modes Count: {res.num_modes}")
        print(f"  Exit Code: {res.exit_code}")

        self.assertTrue(res.success)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(res.target_pdb_id, "2ITZ")
        self.assertFalse(res.is_benchmark) # Must NOT be marked as reference benchmark
        self.assertEqual(res.ligand_smiles, candidate_smiles)

    def test_03_c_abl_separate_ligand(self):
        """Test 3: C-Abl + a separate ligand."""
        print("\n--- TEST 3: C-Abl + Separate Ligand (Imatinib) Docking ---")
        req = DockingRequest(
            target_pdb_id="1IEP",
            ligand_smiles=TARGET_PRESETS["1IEP"]["reference_smiles"],
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Target: {res.target_protein}")
        print(f"  Status: {res.status}")
        print(f"  Best Affinity: {res.best_affinity_kcal_mol} kcal/mol")
        print(f"  Exit Code: {res.exit_code}")

        self.assertTrue(res.success)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(res.target_pdb_id, "1IEP")
        self.assertIn("c-Abl", res.target_protein)
        self.assertLess(res.best_affinity_kcal_mol, -8.0) # Imatinib high affinity in 1IEP

    def test_04_invalid_ligand_input(self):
        """Test 4: Intentionally invalid ligand input."""
        print("\n--- TEST 4: Intentionally Invalid Ligand Input ---")
        invalid_smiles = "NOT_A_VALID_SMILES_STRUCTURE_XYZ!!!"
        req = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles=invalid_smiles,
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Status: {res.status}")
        print(f"  Error Message: {res.error_message}")
        print(f"  Exit Code: {res.exit_code}")

        self.assertFalse(res.success)
        self.assertEqual(res.status, "FAILED")
        self.assertNotEqual(res.exit_code, 0)
        self.assertIsNotNone(res.error_message)
        self.assertIn("RDKit could not parse", res.error_message)
        # Crucial check: must NOT have fallen back to preset ligand or returned an affinity!
        self.assertIsNone(res.best_affinity_kcal_mol)
        self.assertEqual(res.num_modes, 0)

    def test_05_missing_receptor_file(self):
        """Test 5: Missing receptor file."""
        print("\n--- TEST 5: Missing Receptor File Handling ---")
        req = DockingRequest(
            target_pdb_id="2ITZ",
            receptor_pdbqt_path="d:/nonexistent_path_to_receptor_12345.pdbqt",
            ligand_smiles=TARGET_PRESETS["2ITZ"]["reference_smiles"],
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Status: {res.status}")
        print(f"  Error Message: {res.error_message}")
        print(f"  Exit Code: {res.exit_code}")

        self.assertFalse(res.success)
        self.assertEqual(res.status, "FAILED")
        self.assertIn("not found", res.error_message.lower())
        self.assertIsNone(res.best_affinity_kcal_mol)

    def test_06_vina_execution_failure_invalid_box(self):
        """Test 6: Vina execution failure (e.g. invalid zero box dimensions)."""
        print("\n--- TEST 6: Vina Execution Failure (Invalid Box Size 0 Å) ---")
        req = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles=TARGET_PRESETS["2ITZ"]["reference_smiles"],
            size_x=0.0,
            size_y=0.0,
            size_z=0.0,
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Status: {res.status}")
        print(f"  Error Message: {res.error_message}")
        print(f"  Exit Code: {res.exit_code}")

        self.assertFalse(res.success)
        self.assertEqual(res.status, "FAILED")
        self.assertIn("box", res.error_message.lower())
        self.assertIsNone(res.best_affinity_kcal_mol)

    def test_07_retry_after_failure(self):
        """Test 7: Retry after failure creates distinct experiment and succeeds."""
        print("\n--- TEST 7: Retry Execution After Failure ---")
        # Step A: Run failing experiment
        req_fail = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles="INVALID_SYNTAX_123",
            exhaustiveness=1
        )
        res_fail = execute_docking(req_fail, db=self.db)
        print(f"  Initial Failed Run ID: {res_fail.experiment_id} | Status: {res_fail.status}")
        self.assertFalse(res_fail.success)

        # Step B: User fixes input and retries
        valid_smiles = TARGET_PRESETS["2ITZ"]["reference_smiles"]
        req_retry = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles=valid_smiles,
            exhaustiveness=1
        )
        res_retry = execute_docking(req_retry, db=self.db)
        print(f"  Retried Run ID: {res_retry.experiment_id} | Status: {res_retry.status}")
        print(f"  Retried Run Affinity: {res_retry.best_affinity_kcal_mol} kcal/mol")

        self.assertTrue(res_retry.success)
        self.assertEqual(res_retry.status, "SUCCESS")
        self.assertNotEqual(res_fail.experiment_id, res_retry.experiment_id)
        self.assertIsNotNone(res_retry.best_affinity_kcal_mol)

        # Verify disk isolation: both metadata files exist independently
        fail_meta = os.path.join(EXPERIMENTS_DIR, res_fail.experiment_id, "experiment_metadata.json")
        retry_meta = os.path.join(EXPERIMENTS_DIR, res_retry.experiment_id, "experiment_metadata.json")
        self.assertTrue(os.path.exists(fail_meta))
        self.assertTrue(os.path.exists(retry_meta))

        with open(fail_meta) as f:
            fail_data = json.load(f)
        with open(retry_meta) as f:
            retry_data = json.load(f)

        self.assertEqual(fail_data["status"], "FAILED")
        self.assertEqual(retry_data["status"], "SUCCESS")
        print("  Isolation verified: Failed experiment remains marked FAILED on disk.")
        print("  Isolation verified: Retried experiment succeeded with independent workspace.")

if __name__ == "__main__":
    unittest.main()
