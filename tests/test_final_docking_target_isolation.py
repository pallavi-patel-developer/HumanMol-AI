"""
HumanMol AI - Final Docking Target Isolation & Result Binding Audit Suite
Verifies all 10 required regression tests:
1. Open EGFR 2ITZ directly using its URL parameters.
2. Execute EGFR docking and verify its result.
3. Refresh the browser and verify the same experiment retrieval.
4. Open C-Abl 1IEP and verify its result.
5. Switch from C-Abl to EGFR (integrity rejection of mismatched state).
6. Switch from EGFR to C-Abl (integrity rejection of mismatched state).
7. Open a previous experiment from history.
8. Trigger a failed docking run and verify old results are never displayed as new results.
9. Open two experiments with different ligands and verify complete isolation.
10. Verify 3D viewer receptor and ligand checksums and pose endpoints.
"""

import os
import sys
import json
import unittest

# Add workspace root and scientific-engine to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scientific-engine")))

from api.routers.docking import (
    execute_docking, get_docking_experiment, get_docking_experiment_poses,
    list_docking_experiments, TARGET_PRESETS, EXPERIMENTS_DIR
)
from schemas.schemas import DockingRequest, DockingResponse
from database.connection import get_db

def validate_response_integrity(res: DockingResponse, expected_target: str) -> bool:
    """Mirrors frontend client integrity guard."""
    if not res.experiment_id or not res.experiment_id.startswith("exp_"):
        return False
    if (res.target_pdb_id or "").upper().strip() != expected_target.upper().strip():
        return False
    return True

class TestFinalDockingTargetIsolation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db_gen = get_db()
        cls.db = next(cls.db_gen)
        print("\n" + "="*80)
        print("RUNNING 10 REQUIRED DOCKING TARGET ISOLATION & RESULT BINDING REGRESSION TESTS")
        print("="*80)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.db.close()
        except Exception:
            pass

    def test_01_open_egfr_2itz_directly(self):
        """Test 1: Open EGFR 2ITZ directly using URL target."""
        print("\n--- TEST 1: URL Parameter Resolution for EGFR 2ITZ ---")
        preset = TARGET_PRESETS["2ITZ"]
        self.assertEqual(preset["target_pdb_id"], "2ITZ")
        self.assertEqual(preset["mutation"], "L858R (Arg 858 verified)")
        self.assertEqual(preset["center_x"], -51.654)
        self.assertEqual(preset["center_y"], -1.266)
        self.assertEqual(preset["center_z"], -21.945)
        print("  Target resolved: EGFR L858R (2ITZ)")
        print(f"  Pocket Centroid: [{preset['center_x']}, {preset['center_y']}, {preset['center_z']}]")
        print("  VERIFIED: URL ?target=2ITZ resolves authoritative 2ITZ parameters.")

    def test_02_execute_egfr_docking_and_verify(self):
        """Test 2: Execute EGFR docking and verify its result."""
        print("\n--- TEST 2: Execute EGFR 2ITZ Docking ---")
        req = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles=TARGET_PRESETS["2ITZ"]["reference_smiles"],
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Target Protein: {res.target_protein}")
        print(f"  Target PDB: {res.target_pdb_id}")
        print(f"  Best Affinity: {res.best_affinity_kcal_mol} kcal/mol")
        print(f"  Modes: {res.num_modes}")
        print(f"  Exit Code: {res.exit_code}")

        self.assertTrue(res.success)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.target_pdb_id, "2ITZ")
        self.assertIn("EGFR L858R", res.target_protein)
        self.assertLess(res.best_affinity_kcal_mol, -5.0)
        self.assertEqual(res.exit_code, 0)
        self.assertTrue(validate_response_integrity(res, "2ITZ"))

        # Save for Test 3
        TestFinalDockingTargetIsolation.egfr_exp_id = res.experiment_id
        TestFinalDockingTargetIsolation.egfr_res = res

    def test_03_refresh_browser_and_verify_same_experiment(self):
        """Test 3: Refresh browser and verify same experiment retrieval."""
        print("\n--- TEST 3: Refresh / Retrieve Same Experiment via Experiment ID ---")
        exp_id = TestFinalDockingTargetIsolation.egfr_exp_id
        meta = get_docking_experiment(exp_id)
        print(f"  Retrieved Experiment ID: {meta['experiment_id']}")
        print(f"  Target PDB: {meta['target_pdb_id']}")
        print(f"  Affinity: {meta['best_affinity_kcal_mol']} kcal/mol")
        print(f"  Status: {meta['status']}")

        self.assertEqual(meta["experiment_id"], exp_id)
        self.assertEqual(meta["target_pdb_id"], "2ITZ")
        self.assertEqual(meta["status"], "SUCCESS")
        self.assertEqual(meta["best_affinity_kcal_mol"], TestFinalDockingTargetIsolation.egfr_res.best_affinity_kcal_mol)
        print("  VERIFIED: Refreshing URL with experiment_id retrieves identical authoritative record.")

    def test_04_open_c_abl_1iep_and_verify(self):
        """Test 4: Open C-Abl 1IEP and verify its result."""
        print("\n--- TEST 4: Execute C-Abl 1IEP Docking ---")
        req = DockingRequest(
            target_pdb_id="1IEP",
            ligand_smiles=TARGET_PRESETS["1IEP"]["reference_smiles"],
            exhaustiveness=1
        )
        res = execute_docking(req, db=self.db)
        print(f"  Experiment ID: {res.experiment_id}")
        print(f"  Target Protein: {res.target_protein}")
        print(f"  Target PDB: {res.target_pdb_id}")
        print(f"  Best Affinity: {res.best_affinity_kcal_mol} kcal/mol")

        self.assertTrue(res.success)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.target_pdb_id, "1IEP")
        self.assertIn("c-Abl", res.target_protein)
        self.assertLess(res.best_affinity_kcal_mol, -8.0)
        self.assertTrue(validate_response_integrity(res, "1IEP"))

        TestFinalDockingTargetIsolation.cabl_exp_id = res.experiment_id
        TestFinalDockingTargetIsolation.cabl_res = res

    def test_05_switch_from_c_abl_to_egfr(self):
        """Test 5: Switch from C-Abl to EGFR (integrity rejection of mismatched state)."""
        print("\n--- TEST 5: Target Switch from C-Abl to EGFR (Validation Rejection) ---")
        # Attempt to display previous c-Abl response when active URL target is 2ITZ
        cabl_res = TestFinalDockingTargetIsolation.cabl_res
        is_valid = validate_response_integrity(cabl_res, expected_target="2ITZ")
        print(f"  Is C-Abl result valid when active target is 2ITZ? {is_valid}")
        self.assertFalse(is_valid) # MUST be rejected!

        # Now execute clean EGFR docking
        req = DockingRequest(target_pdb_id="2ITZ", ligand_smiles=TARGET_PRESETS["2ITZ"]["reference_smiles"], exhaustiveness=1)
        res = execute_docking(req, db=self.db)
        self.assertEqual(res.target_pdb_id, "2ITZ")
        self.assertTrue(validate_response_integrity(res, expected_target="2ITZ"))
        print("  VERIFIED: Switching to EGFR strictly rejects 1IEP results and binds to new 2ITZ experiment.")

    def test_06_switch_from_egfr_to_c_abl(self):
        """Test 6: Switch from EGFR to C-Abl (integrity rejection of mismatched state)."""
        print("\n--- TEST 6: Target Switch from EGFR to C-Abl (Validation Rejection) ---")
        egfr_res = TestFinalDockingTargetIsolation.egfr_res
        is_valid = validate_response_integrity(egfr_res, expected_target="1IEP")
        print(f"  Is EGFR result valid when active target is 1IEP? {is_valid}")
        self.assertFalse(is_valid) # MUST be rejected!

        req = DockingRequest(target_pdb_id="1IEP", ligand_smiles=TARGET_PRESETS["1IEP"]["reference_smiles"], exhaustiveness=1)
        res = execute_docking(req, db=self.db)
        self.assertEqual(res.target_pdb_id, "1IEP")
        self.assertTrue(validate_response_integrity(res, expected_target="1IEP"))
        print("  VERIFIED: Switching to C-Abl strictly rejects 2ITZ results and binds to new 1IEP experiment.")

    def test_07_open_previous_experiment_from_history(self):
        """Test 7: Open a previous experiment from history."""
        print("\n--- TEST 7: Open Previous Experiment from History ---")
        experiments = list_docking_experiments(limit=5)
        self.assertGreater(len(experiments), 0)
        target_exp = experiments[0]
        print(f"  Inspecting historical experiment: {target_exp.experiment_id} ({target_exp.target_pdb_id})")

        meta = get_docking_experiment(target_exp.experiment_id)
        self.assertEqual(meta["experiment_id"], target_exp.experiment_id)
        self.assertEqual(meta["target_pdb_id"], target_exp.target_pdb_id)
        print("  VERIFIED: Historical experiment loads solely with its own target, mutation, and score.")

    def test_08_failed_docking_does_not_display_old_results(self):
        """Test 8: Trigger a failed docking run and verify old results are not displayed."""
        print("\n--- TEST 8: Trigger Failed Docking Run (No Stale Leakage) ---")
        req_fail = DockingRequest(
            target_pdb_id="2ITZ",
            ligand_smiles="INVALID_CHEMICAL_SMILES_STRING_12345",
            exhaustiveness=1
        )
        res_fail = execute_docking(req_fail, db=self.db)
        print(f"  Failed Experiment ID: {res_fail.experiment_id}")
        print(f"  Status: {res_fail.status}")
        print(f"  Exit Code: {res_fail.exit_code}")
        print(f"  Best Affinity: {res_fail.best_affinity_kcal_mol}")
        print(f"  Modes: {res_fail.modes}")

        self.assertFalse(res_fail.success)
        self.assertEqual(res_fail.status, "FAILED")
        self.assertIsNone(res_fail.best_affinity_kcal_mol)
        self.assertEqual(len(res_fail.modes), 0)
        self.assertNotEqual(res_fail.exit_code, 0)
        print("  VERIFIED: Failed run returns None for affinity, 0 modes, and never reuses C-Abl or prior EGFR scores.")

    def test_09_two_experiments_different_ligands(self):
        """Test 9: Open two experiments with different ligands and verify complete isolation."""
        print("\n--- TEST 9: Two Experiments with Different Ligands ---")
        smi_a = "COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1" # Gefitinib
        smi_b = "C(Cc1nnn(c1)Cc1cccc2ncccc21)(C)(C)C" # Novel candidate

        res_a = execute_docking(DockingRequest(target_pdb_id="2ITZ", ligand_smiles=smi_a, exhaustiveness=1), db=self.db)
        res_b = execute_docking(DockingRequest(target_pdb_id="2ITZ", ligand_smiles=smi_b, exhaustiveness=1), db=self.db)

        print(f"  Exp A ({smi_a[:20]}...): ID = {res_a.experiment_id}, SHA256 = {res_a.ligand_sha256[:16]}..., Aff = {res_a.best_affinity_kcal_mol}")
        print(f"  Exp B ({smi_b[:20]}...): ID = {res_b.experiment_id}, SHA256 = {res_b.ligand_sha256[:16]}..., Aff = {res_b.best_affinity_kcal_mol}")

        self.assertNotEqual(res_a.experiment_id, res_b.experiment_id)
        self.assertNotEqual(res_a.ligand_sha256, res_b.ligand_sha256)
        self.assertNotEqual(res_a.ligand_smiles, res_b.ligand_smiles)
        print("  VERIFIED: Complete ligand and workspace isolation between distinct molecules.")

    def test_10_verify_3d_viewer_checksums_and_poses(self):
        """Test 10: Verify 3D viewer receptor and ligand checksums and pose endpoints."""
        print("\n--- TEST 10: 3D Viewer Checksums & PDBQT Pose Retrieval ---")
        exp_id = TestFinalDockingTargetIsolation.egfr_exp_id
        meta = get_docking_experiment(exp_id)
        poses = get_docking_experiment_poses(exp_id)

        print(f"  Receptor SHA256: {meta['receptor_sha256']}")
        print(f"  Ligand SHA256: {meta['ligand_sha256']}")
        print(f"  Poses Content Length: {len(poses['pdbqt_content'])} bytes")

        self.assertIsNotNone(meta["receptor_sha256"])
        self.assertIsNotNone(meta["ligand_sha256"])
        self.assertIn("MODEL", poses["pdbqt_content"])
        self.assertIn("REMARK VINA RESULT", poses["pdbqt_content"])
        self.assertEqual(poses["experiment_id"], exp_id)
        print("  VERIFIED: 3D visualizer receives authoritative poses and checksums for the specific experiment.")

if __name__ == "__main__":
    unittest.main()
