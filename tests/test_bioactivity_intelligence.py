"""
HumanMol AI - Stage 4A Scientific Integrity & Final Verification Test Suite
Validates:
1. Dataset Count Consistency (Database, In-Memory, and API all report 21 records)
2. Duplicate Experimental Record Detection (All 21 assay_ids are strictly distinct)
3. Cross-Study Selectivity Rejection (Barker vs Yun, Moyer vs Carey return INCOMPARABLE_CROSS_STUDY, selectivity_ratio=None, exploratory_ratio set)
4. Gefitinib Kd Source Provenance (Yun 2007 Table 3: WT 53.5 ± 1.8 nM, L858R 2.6 ± 0.2 nM, ratio 20.58x, COMPARABLE)
5. Afatinib Assay Platform & Incubation (Li 2008 ATP/NADH coupled assay; unverified incubation -> PROVISIONAL, selectivity_ratio=None, exploratory_ratio=1.25)
6. Osimertinib Recombinant Comparability (Cross 2014 Table 1 -> PROVISIONAL due to time-dependent apparent IC50; selectivity_ratio=None, exploratory_ratio=15.33)
7. Missing Protocol Field Not Silently Matched (Irreversible inhibitors with unverified pre-incubation rejected from COMPARABLE)
8. Incomparable Endpoint Rejection: Kd vs IC50 (Thermodynamic Kd vs functional IC50 returns INCOMPARABLE_ENDPOINT)
9. Incomparable Endpoint Rejection: Recombinant vs Cellular (Enzyme IC50 vs Cellular Autophosphorylation returns INCOMPARABLE_ENDPOINT)
10. Censored Inequality Handling (Kobayashi2005 >2000 nM preserves '>' relation and does not produce exact validated scalar ratio)
11. HM-EGFR-012 Zero Transfer & Exact ADMET Model Provenance (UNTESTED status, no 'ensemble' claim, exact ADMETlab 3.0 / Chemprop attribution)
12. Pipeline & Target Isolation Regression (EGFR 2ITZ vs c-Abl 1IEP isolation)
13. Moyer 1997 & Carey 2006 Primary Literature Identifiers (Moyer PMID 9354447, Carey PMID 16912195)
14. Cellular Selectivity Governance (LoVo vs H1975 returns PROVISIONAL_CELLULAR_CONTEXT, selectivity_ratio=None, 32x contextual ratio)
15. Caco-2 Permeability Units (Expressed as log10(cm/s), never unphysical negative linear cm/s)
16. Docking Terminology (Labeled PREDICTED VINA DOCKING SCORE, disclaimer excludes experimentally measured affinity)
17. Scientific Runtime Software Versions (AutoDock Vina v1.2.7 and Chemprop 2.3.1)
"""

import os
import sys
import shutil
import sqlite3
import subprocess

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from fastapi.testclient import TestClient
from scientific_engine.api.app import app
from scientific_engine.biological_data.bioactivity_service import (
    bioactivity_service,
    COMPOUND_ALIAS_MAP,
    VERIFIED_BENCHMARK_RECORDS,
)

client = TestClient(app)

# -----------------------------------------------------------------------------
# Test 1: Dataset Count Consistency
# -----------------------------------------------------------------------------
def test_dataset_count_consistency():
    """Asserts that in-memory dataset, SQLite database, and API endpoint report exactly 21 records."""
    assert len(VERIFIED_BENCHMARK_RECORDS) == 21, f"Expected 21 in-memory records, found {len(VERIFIED_BENCHMARK_RECORDS)}"

    conn = sqlite3.connect("database/humanmol.db")
    c = conn.cursor()
    db_count = c.execute("SELECT COUNT(*) FROM experimental_bioactivities").fetchone()[0]
    conn.close()
    assert db_count == 21, f"Expected 21 database records, found {db_count}"

    resp = client.get("/api/bioactivity/egfr-benchmark")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_records"] == 21
    assert data["reference_inhibitors_count"] == 4
    assert len(data["records"]) == 21


# -----------------------------------------------------------------------------
# Test 2: Duplicate Experimental Record Detection
# -----------------------------------------------------------------------------
def test_duplicate_assay_detection():
    """Ensures each assay_id is strictly unique across the 21 experimental records."""
    benchmarks = bioactivity_service.get_benchmark_dataset()
    assay_ids = [r["assay_id"] for r in benchmarks]
    assert len(assay_ids) == len(set(assay_ids)), "Duplicate assay_ids detected in benchmark dataset!"
    assert len(assay_ids) == 21


# -----------------------------------------------------------------------------
# Test 3: Cross-Study Selectivity Rejection (INCOMPARABLE_CROSS_STUDY)
# -----------------------------------------------------------------------------
def test_cross_study_selectivity_rejection():
    """
    STRICT SCIENTIFIC RULE: Cross-study pairs across different laboratories and protocols
    must NOT be marked as COMPARABLE. They must be assigned INCOMPARABLE_CROSS_STUDY.
    Validated selectivity_ratio must be None; exploratory_ratio must be populated.
    """
    # 1. Gefitinib Biochemical: Barker 2001 (AstraZeneca, 33 nM) vs Yun 2007 (Dana-Farber, 7.8 nM)
    res_gef_cross = bioactivity_service.check_selectivity_by_ids("Barker2001-WT-IC50", "Yun2007-L858R-IC50")
    assert res_gef_cross["comparability_status"] == "INCOMPARABLE_CROSS_STUDY"
    assert res_gef_cross["selectivity_ratio"] is None, "Validated ratio must be None for cross-study!"
    assert res_gef_cross["exploratory_ratio"] == 4.23
    assert "Exploratory Cross-Study Comparison" in res_gef_cross["selectivity_interpretation"]

    # 2. Erlotinib Biochemical: Moyer 1997 (Pfizer, 2.0 nM) vs Carey 2006 (Genentech, 0.5 nM)
    res_erl_cross = bioactivity_service.check_selectivity_by_ids("Moyer1997-WT-IC50", "Carey2006-L858R-IC50")
    assert res_erl_cross["comparability_status"] == "INCOMPARABLE_CROSS_STUDY"
    assert res_erl_cross["selectivity_ratio"] is None
    assert res_erl_cross["exploratory_ratio"] == 4.00

    # API validation of cross-study rejection
    resp = client.post("/api/bioactivity/selectivity-check", json={
        "wt_assay_id": "Barker2001-WT-IC50",
        "mutant_assay_id": "Yun2007-L858R-IC50",
        "target_mutation": "L858R"
    })
    assert resp.status_code == 200
    api_data = resp.json()
    assert api_data["comparability_status"] == "INCOMPARABLE_CROSS_STUDY"
    assert api_data["selectivity_ratio"] is None
    assert api_data["exploratory_ratio"] == 4.23


# -----------------------------------------------------------------------------
# Test 4: Gefitinib Kd Source Provenance (Yun et al. 2007 Table 3)
# -----------------------------------------------------------------------------
def test_gefitinib_kd_provenance_and_selectivity():
    """
    Verifies that Gefitinib Kd values match primary publication Yun et al. 2007 Table 3:
    WT Kd = 53.5 ± 1.8 nM (Table 3), L858R Kd = 2.6 ± 0.2 nM (Table 3), ratio = 20.58x (COMPARABLE).
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()
    wt_kd_rec = next((r for r in benchmarks if r["assay_id"] == "Yun2007-WT-Kd"), None)
    l858r_kd_rec = next((r for r in benchmarks if r["assay_id"] == "Yun2007-L858R-Kd"), None)

    assert wt_kd_rec is not None, "Yun2007-WT-Kd record not found"
    assert l858r_kd_rec is not None, "Yun2007-L858R-Kd record not found"

    # Assert Table 3 values and uncertainty
    assert wt_kd_rec["standard_value"] == 53.5
    assert wt_kd_rec["uncertainty_value"] == 1.8, f"Expected WT uncertainty 1.8, found {wt_kd_rec['uncertainty_value']}"
    assert wt_kd_rec["table_figure_ref"] == "Table 3", f"Expected Table 3, found {wt_kd_rec['table_figure_ref']}"
    assert wt_kd_rec["assay_method"] == "Fluorescence Quenching", f"Expected Fluorescence Quenching, got {wt_kd_rec.get('assay_method')}"
    assert wt_kd_rec["assay_format"] == "Fluorescence Quenching Assay"
    assert "ITC" not in wt_kd_rec["assay_description"] and "Isothermal" not in wt_kd_rec["assay_description"]

    assert l858r_kd_rec["standard_value"] == 2.6
    assert l858r_kd_rec["uncertainty_value"] == 0.2, f"Expected L858R uncertainty 0.2, found {l858r_kd_rec['uncertainty_value']}"
    assert l858r_kd_rec["table_figure_ref"] == "Table 3", f"Expected Table 3, found {l858r_kd_rec['table_figure_ref']}"
    assert l858r_kd_rec["assay_method"] == "Fluorescence Quenching", f"Expected Fluorescence Quenching, got {l858r_kd_rec.get('assay_method')}"
    assert l858r_kd_rec["assay_format"] == "Fluorescence Quenching Assay"
    assert "ITC" not in l858r_kd_rec["assay_description"] and "Isothermal" not in l858r_kd_rec["assay_description"]

    # Calculate intra-study Kd selectivity
    res_kd = bioactivity_service.check_selectivity_by_ids("Yun2007-WT-Kd", "Yun2007-L858R-Kd")
    assert res_kd["comparability_status"] == "COMPARABLE"
    assert res_kd["selectivity_ratio"] == 20.58
    assert res_kd["exploratory_ratio"] == 20.58
    assert "Mutant-Selective" in res_kd["selectivity_interpretation"]


# -----------------------------------------------------------------------------
# Test 5: Afatinib Assay Platform & Incubation (Li 2008)
# -----------------------------------------------------------------------------
def test_afatinib_assay_platform_and_incubation():
    """
    Verifies that Afatinib is described as an ATP/NADH-coupled kinase assay (not Z'-LYTE),
    pre-incubation is marked NOT_REPORTED in methods, and the pair is classified as PROVISIONAL.
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()
    wt_rec = next((r for r in benchmarks if r["assay_id"] == "Li2008-WT-IC50"), None)

    assert "ATP/NADH-coupled" in wt_rec["assay_description"]
    assert "Z'-LYTE" not in wt_rec["assay_description"]
    assert "Z'-LYTE" not in wt_rec["curator_notes"]
    assert "NOT_REPORTED" in wt_rec["curator_notes"]

    res_afa = bioactivity_service.check_selectivity_by_ids("Li2008-WT-IC50", "Li2008-L858R-IC50")
    assert res_afa["comparability_status"] == "PROVISIONAL"
    assert res_afa["selectivity_ratio"] is None, "Validated ratio must be None for provisional pair"
    assert res_afa["exploratory_ratio"] == 1.25
    assert "Provisional" in res_afa["selectivity_interpretation"]
    assert "time-dependent" in res_afa["rejection_reason"].lower()


# -----------------------------------------------------------------------------
# Test 6: Osimertinib Recombinant Comparability (Cross 2014)
# -----------------------------------------------------------------------------
def test_osimertinib_recombinant_comparability():
    """
    Verifies Cross et al. 2014 Table 1 apparent IC50 is PROVISIONAL because pre-incubation duration
    is not reported and irreversible covalent inhibition makes apparent IC50 time-dependent.
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()
    wt_rec = next((r for r in benchmarks if r["assay_id"] == "Cross2014-WT-IC50"), None)
    assert wt_rec["standard_value"] == 184.0
    assert "NOT_REPORTED" in wt_rec["curator_notes"]

    res_osi = bioactivity_service.check_selectivity_by_ids("Cross2014-WT-IC50", "Cross2014-L858R-IC50")
    assert res_osi["comparability_status"] == "PROVISIONAL"
    assert res_osi["selectivity_ratio"] is None
    assert res_osi["exploratory_ratio"] == 15.33
    assert res_osi["irreversible_kinetics_note"] is not None


# -----------------------------------------------------------------------------
# Test 7: Missing Protocol Field Not Silently Matched
# -----------------------------------------------------------------------------
def test_missing_protocol_field_not_silently_matched():
    """
    Asserts that irreversible covalent inhibitor IC50s with unverified pre-incubation
    are NOT silently promoted to COMPARABLE.
    """
    res_osi = bioactivity_service.check_selectivity_by_ids("Cross2014-WT-IC50", "Cross2014-L858R-IC50")
    assert res_osi["comparability_status"] != "COMPARABLE"
    assert res_osi["comparability_status"] == "PROVISIONAL"


# -----------------------------------------------------------------------------
# Test 8: Incomparable Endpoint Rejection: Kd vs IC50
# -----------------------------------------------------------------------------
def test_kd_vs_ic50_endpoint_rejection():
    """Strictly rejects comparison between thermodynamic Kd and functional IC50."""
    res = bioactivity_service.check_selectivity_by_ids(
        wt_assay_id="Yun2007-WT-Kd",      # Kd = 53.5 nM
        mutant_assay_id="Yun2007-L858R-IC50" # IC50 = 7.8 nM
    )
    assert res["comparability_status"] == "INCOMPARABLE_ENDPOINT"
    assert res["selectivity_ratio"] is None
    assert res["exploratory_ratio"] is None
    assert "Mismatched measurement endpoints" in res["rejection_reason"]


# -----------------------------------------------------------------------------
# Test 9: Incomparable Endpoint Rejection: Recombinant vs Cellular
# -----------------------------------------------------------------------------
def test_recombinant_vs_cellular_endpoint_rejection():
    """Strictly rejects comparison between recombinant biochemical IC50 and cellular autophosphorylation."""
    res_mismatch = bioactivity_service.check_selectivity_by_ids(
        wt_assay_id="Cross2014-WT-IC50",          # Recombinant Enzyme (184 nM)
        mutant_assay_id="Finlay2014-H1975-IC50"  # Cellular Autophosphorylation (15 nM)
    )
    assert res_mismatch["comparability_status"] == "INCOMPARABLE_ENDPOINT"
    assert res_mismatch["selectivity_ratio"] is None
    assert res_mismatch["exploratory_ratio"] is None
    assert "Incomparable experimental formats" in res_mismatch["rejection_reason"]


# -----------------------------------------------------------------------------
# Test 10: Censored Inequality Handling (>2000 nM)
# -----------------------------------------------------------------------------
def test_censored_inequality_handling():
    """
    Confirms censored values (e.g. Kobayashi 2005 >2000 nM) retain standard_relation '>'
    and are never converted into exact scalar selectivity ratios.
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()
    t790m_rec = next((r for r in benchmarks if r["assay_id"] == "Kobayashi2005-T790M-IC50"), None)
    assert t790m_rec["standard_relation"] == ">"
    assert t790m_rec["standard_value"] == 2000.0

    res = bioactivity_service.check_selectivity_by_ids("Barker2001-WT-IC50", "Kobayashi2005-T790M-IC50")
    assert res["selectivity_ratio"] is None
    assert "Censored" in res["selectivity_interpretation"] or "Cross-Study" in res["selectivity_interpretation"]


# -----------------------------------------------------------------------------
# Test 11: HM-EGFR-012 Zero Transfer & Exact ADMET Model Provenance
# -----------------------------------------------------------------------------
def test_hm_egfr_012_zero_transfer_and_admet_provenance():
    """
    STRICT BOUNDARY: HM-EGFR-012 is UNTESTED with zero transfer of reference data.
    ADMET model provenance must identify exact models and must NOT claim 'ensemble'.
    """
    resp = client.get("/api/bioactivity/candidate/HM-EGFR-012")
    assert resp.status_code == 200
    data = resp.json()

    # Identity
    assert data["molecular_formula"] == "C17H21N5O2S"
    assert data["molecular_weight"] == 359.46
    assert data["exact_molecular_weight"] == 359.1416
    assert data["inchikey"] == "DCESSRBOYUDSNL-UHFFFAOYSA-N"

    # Strict separation
    exp = data["experimental_bioactivity"]
    assert exp["egfr_l858r_ic50"] == "UNTESTED"
    assert exp["egfr_wt_ic50"] == "UNTESTED"
    assert exp["selectivity_index"] == "NOT_AVAILABLE"
    assert exp["is_experimental_verified"] is False
    assert exp["experimental_records_count"] == 0

    # Model provenance (No 'ensemble' claim)
    comp = data["computational_profile"]
    assert "ensemble" not in comp["model_provenance"].lower()
    assert "ADMETlab 3.0" in comp["model_provenance"]
    assert "Chemprop v2.3.1" in comp["model_provenance"]
    assert "LOW PREDICTED hERG LIABILITY" in comp["admet_herg_liability"]
    assert "LOW PREDICTED DILI RISK" in comp["admet_dili_risk"]
    assert "PREDICTED NEGATIVE" in comp["admet_ames_mutagenicity"]
    assert "PREDICTED CACO-2 PERMEABILITY" in comp["admet_caco2"]


# -----------------------------------------------------------------------------
# Test 12: Pipeline & Target Isolation Regression
# -----------------------------------------------------------------------------
def test_pipeline_and_target_isolation_regression():
    """Confirms pipeline health, chemistry validation, and EGFR 2ITZ vs c-Abl 1IEP isolation."""
    # Health check
    h_resp = client.get("/health")
    assert h_resp.status_code == 200

    # Chemistry validate
    chem_resp = client.post("/api/chemistry/validate", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    assert chem_resp.status_code == 200
    assert chem_resp.json()["valid"] is True

    # EGFR target search
    egfr_resp = client.get("/api/targets/search?query=EGFR&mutation=L858R")
    assert egfr_resp.status_code == 200
    assert egfr_resp.json()["recommended_structure"]["pdb_id"] == "2ITZ"

    # C-Abl target search
    cabl_resp = client.get("/api/targets/search?query=c-Abl&mutation=Wild-Type")
    assert cabl_resp.status_code == 200
    assert cabl_resp.json()["recommended_structure"]["pdb_id"] == "1IEP"


# -----------------------------------------------------------------------------
# Test 13: Moyer 1997 & Carey 2006 Primary Literature Identifiers
# -----------------------------------------------------------------------------
def test_moyer_and_carey_literature_identifiers():
    """
    Verifies that Moyer 1997 maps to PMID 9354447 (not Pollack 10525095),
    and Carey 2006 maps to PMID 16912195 (not 16912194).
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()
    moyer_wt = next(r for r in benchmarks if r["assay_id"] == "Moyer1997-WT-IC50")
    moyer_cell = next(r for r in benchmarks if r["assay_id"] == "Moyer1997-Cellular-IC50")
    carey_mut = next(r for r in benchmarks if r["assay_id"] == "Carey2006-L858R-IC50")

    # Moyer 1997 checks
    assert moyer_wt["doi"] == "10.1158/0008-5472.CAN-97-4838"
    assert moyer_wt["pmid"] == "9354447", f"Incorrect Moyer WT PMID: {moyer_wt['pmid']}"
    assert moyer_cell["pmid"] == "9354447", f"Incorrect Moyer Cellular PMID: {moyer_cell['pmid']}"
    assert "10525095" not in moyer_wt["pmid"]

    # Carey 2006 checks
    assert carey_mut["doi"] == "10.1158/0008-5472.CAN-06-0453"
    assert carey_mut["pmid"] == "16912195", f"Incorrect Carey L858R PMID: {carey_mut['pmid']}"
    assert carey_mut["pmid"] != "16912194"


# -----------------------------------------------------------------------------
# Test 14: Cellular Selectivity Governance & Statistical Uncertainty
# -----------------------------------------------------------------------------
def test_cellular_selectivity_non_isogenic_provisional():
    """
    Asserts that cellular comparison (LoVo colorectal WT vs H1975 NSCLC mutant)
    is PROVISIONAL_CELLULAR_CONTEXT and CANNOT be called validated mutation-specific selectivity.
    Verifies that Finlay 2014 Table 1 geometric mean values (480 nM, 15 nM) have uncertainty
    stored as NULL (NOT_REPORTED in primary source), not fabricated.
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()
    lovo_rec = next(r for r in benchmarks if r["assay_id"] == "Finlay2014-LoVo-IC50")
    h1975_rec = next(r for r in benchmarks if r["assay_id"] == "Finlay2014-H1975-IC50")

    # Finlay 2014 uncertainty checks: must be None/NULL (NOT_REPORTED in primary source)
    assert lovo_rec["uncertainty_value"] is None, f"Expected None/NULL uncertainty for LoVo, found {lovo_rec['uncertainty_value']}"
    assert h1975_rec["uncertainty_value"] is None, f"Expected None/NULL uncertainty for H1975, found {h1975_rec['uncertainty_value']}"
    assert lovo_rec["table_figure_ref"] == "Table 1"
    assert h1975_rec["table_figure_ref"] == "Table 1"
    assert "NOT_REPORTED" in lovo_rec["curator_notes"]
    assert "NOT_REPORTED" in h1975_rec["curator_notes"]
    assert "geometric mean" in lovo_rec["curator_notes"].lower()
    assert "geometric mean" in h1975_rec["curator_notes"].lower()

    # Direct SQLite database inspection: verify uncertainty_value is NULL in storage
    import sqlite3
    con = sqlite3.connect("database/humanmol.db")
    cur = con.cursor()
    cur.execute(
        "SELECT assay_id, standard_value, uncertainty_value, assay_method FROM experimental_bioactivities WHERE assay_id IN (?, ?)",
        ("Finlay2014-LoVo-IC50", "Finlay2014-H1975-IC50")
    )
    db_rows = {row[0]: row for row in cur.fetchall()}
    assert db_rows["Finlay2014-LoVo-IC50"][2] is None, "Database uncertainty_value must be NULL for LoVo"
    assert db_rows["Finlay2014-H1975-IC50"][2] is None, "Database uncertainty_value must be NULL for H1975"
    assert db_rows["Finlay2014-LoVo-IC50"][1] == 480.0
    assert db_rows["Finlay2014-H1975-IC50"][1] == 15.0
    con.close()

    res = bioactivity_service.check_selectivity_by_ids("Finlay2014-LoVo-IC50", "Finlay2014-H1975-IC50")
    assert res["comparability_status"] == "PROVISIONAL_CELLULAR_CONTEXT"
    assert res["selectivity_ratio"] is None, "Validated mutation-specific ratio must be None for non-isogenic cells"
    assert res["exploratory_ratio"] == 32.0, f"Expected exploratory ratio 32.0, found {res['exploratory_ratio']}"
    assert "Non-Isogenic" in res["selectivity_interpretation"]
    assert res["cellular_context_note"] is not None
    assert "does not isolate" in res["rejection_reason"].lower() or "rather than isolated causal" in res["rejection_reason"]


# -----------------------------------------------------------------------------
# Test 15: Caco-2 Permeability Logarithmic Units
# -----------------------------------------------------------------------------
def test_caco2_logarithmic_units():
    """
    Asserts that Caco-2 permeability is labeled in logarithmic units (log10(cm/s)),
    never displayed as an unphysical negative raw permeability in linear cm/s.
    """
    cand = bioactivity_service.get_candidate_evidence_status("HM-EGFR-012")
    comp = cand["computational_profile"]
    assert comp["admet_caco2_unit"] == "log10(cm/s)"
    assert "log10(cm/s)" in comp["admet_caco2"]
    assert comp["admet_caco2_raw_value"] == -4.62
    # Ensure it's not displayed as raw '-4.62 cm/s'
    assert "-4.62 cm/s" not in comp["admet_caco2"]


# -----------------------------------------------------------------------------
# Test 16: Docking Terminology (Predicted Vina Docking Score)
# -----------------------------------------------------------------------------
def test_docking_terminology_predicted_vina_score():
    """
    Verifies docking score is explicitly labeled PREDICTED VINA DOCKING SCORE,
    and disclaimer explicitly states it is not experimentally measured binding affinity.
    """
    cand = bioactivity_service.get_candidate_evidence_status("HM-EGFR-012")
    comp = cand["computational_profile"]
    assert comp["docking_score_label"] == "PREDICTED VINA DOCKING SCORE"
    assert comp["docking_score"] == -7.161
    assert "AutoDock Vina v1.2.7" in comp["docking_software"]
    assert "NOT experimentally measured binding affinity" in comp["docking_disclaimer"]
    assert "empirical scoring function" in comp["docking_scoring_function"]


# -----------------------------------------------------------------------------
# Test 17: Scientific Runtime Software Versions
# -----------------------------------------------------------------------------
def test_runtime_software_versions():
    """
    Verifies runtime environment has AutoDock Vina v1.2.7 and Chemprop 2.3.1 installed.
    """
    import chemprop
    assert chemprop.__version__ == "2.3.1", f"Expected Chemprop 2.3.1, found {chemprop.__version__}"

    vina_bin = shutil.which("vina")
    if not vina_bin and os.path.exists(r"C:\Users\hp\miniconda3\Scripts\vina.EXE"):
        vina_bin = r"C:\Users\hp\miniconda3\Scripts\vina.EXE"
    assert vina_bin is not None, "Vina binary not found"
    
    out = subprocess.check_output([vina_bin, "--version"], text=True)
    assert "1.2.7" in out, f"Expected AutoDock Vina v1.2.7, got {out}"


# -----------------------------------------------------------------------------
# Test 18: Final Stage 4A Scientific Corrections Comprehensive Verification
# -----------------------------------------------------------------------------
def test_stage4a_final_scientific_corrections_suite():
    """
    Comprehensive verification of all 7 Stage 4A Final Correction criteria:
    1. Yun 2007 assay method equals 'Fluorescence Quenching'.
    2. Afatinib provisional selectivity_ratio is NULL.
    3. Osimertinib provisional selectivity_ratio is NULL.
    4. Exploratory ratios remain separately stored (1.25x and 15.33x).
    5. Finlay uncertainty values have source-backed statistical metadata (NOT_REPORTED).
    6. Missing source uncertainty is represented as NULL, not fabricated.
    7. Database, service, API and UI return consistent values.
    """
    benchmarks = bioactivity_service.get_benchmark_dataset()

    # 1. Yun 2007 assay method equals Fluorescence Quenching
    yun_wt = next(r for r in benchmarks if r["assay_id"] == "Yun2007-WT-Kd")
    yun_mut = next(r for r in benchmarks if r["assay_id"] == "Yun2007-L858R-Kd")
    assert yun_wt["assay_method"] == "Fluorescence Quenching"
    assert yun_mut["assay_method"] == "Fluorescence Quenching"
    assert "ITC" not in yun_wt["assay_description"] and "Isothermal" not in yun_wt["assay_description"]

    # 2. Afatinib provisional selectivity_ratio is NULL
    res_afa = bioactivity_service.check_selectivity_by_ids("Li2008-WT-IC50", "Li2008-L858R-IC50")
    assert res_afa["comparability_status"] == "PROVISIONAL"
    assert res_afa["selectivity_ratio"] is None

    # 3. Osimertinib provisional selectivity_ratio is NULL
    res_osi = bioactivity_service.check_selectivity_by_ids("Cross2014-WT-IC50", "Cross2014-L858R-IC50")
    assert res_osi["comparability_status"] == "PROVISIONAL"
    assert res_osi["selectivity_ratio"] is None

    # 4. Exploratory ratios remain separately stored
    assert res_afa["exploratory_ratio"] == 1.25
    assert res_osi["exploratory_ratio"] == 15.33
    res_yun = bioactivity_service.check_selectivity_by_ids("Yun2007-WT-Kd", "Yun2007-L858R-Kd")
    assert res_yun["selectivity_ratio"] == 20.58
    assert res_yun["exploratory_ratio"] == 20.58

    # 5. Finlay uncertainty values have source-backed statistical metadata
    fin_lovo = next(r for r in benchmarks if r["assay_id"] == "Finlay2014-LoVo-IC50")
    fin_h1975 = next(r for r in benchmarks if r["assay_id"] == "Finlay2014-H1975-IC50")
    assert "geometric mean" in fin_lovo["curator_notes"].lower()
    assert "geometric mean" in fin_h1975["curator_notes"].lower()
    assert "NOT_REPORTED" in fin_lovo["curator_notes"]
    assert "NOT_REPORTED" in fin_h1975["curator_notes"]

    # 6. Missing source uncertainty is represented as NULL, not fabricated
    assert fin_lovo["uncertainty_value"] is None
    assert fin_h1975["uncertainty_value"] is None

    # 7. Database, service, API consistency
    import sqlite3
    con = sqlite3.connect("database/humanmol.db")
    cur = con.cursor()
    cur.execute("SELECT assay_method, uncertainty_value FROM experimental_bioactivities WHERE assay_id='Yun2007-WT-Kd'")
    db_yun = cur.fetchone()
    assert db_yun[0] == "Fluorescence Quenching"
    assert db_yun[1] == 1.8

    cur.execute("SELECT assay_method, uncertainty_value FROM experimental_bioactivities WHERE assay_id='Finlay2014-LoVo-IC50'")
    db_lovo = cur.fetchone()
    assert db_lovo[1] is None  # SQLite NULL is Python None
    con.close()

    # FastApi test client verification
    api_resp = client.get("/api/bioactivity/egfr-benchmark")
    assert api_resp.status_code == 200
    api_recs = api_resp.json()["records"]
    api_yun = next(r for r in api_recs if r["assay_id"] == "Yun2007-WT-Kd")
    assert api_yun["assay_method"] == "Fluorescence Quenching"
    api_lovo = next(r for r in api_recs if r["assay_id"] == "Finlay2014-LoVo-IC50")
    assert api_lovo["uncertainty_value"] is None

    api_select_afa = client.post("/api/bioactivity/selectivity-check", json={
        "wt_assay_id": "Li2008-WT-IC50",
        "mutant_assay_id": "Li2008-L858R-IC50",
        "target_mutation": "L858R"
    })
    assert api_select_afa.status_code == 200
    assert api_select_afa.json()["comparability_status"] == "PROVISIONAL"
    assert api_select_afa.json()["selectivity_ratio"] is None
    assert api_select_afa.json()["exploratory_ratio"] == 1.25


if __name__ == "__main__":
    tests = [
        ("Test 01: Dataset Count Consistency (DB, In-Memory, API = 21)", test_dataset_count_consistency),
        ("Test 02: Duplicate Experimental Record Detection (21 distinct)", test_duplicate_assay_detection),
        ("Test 03: Cross-Study Selectivity Rejection (INCOMPARABLE_CROSS_STUDY)", test_cross_study_selectivity_rejection),
        ("Test 04: Gefitinib Kd Source Provenance (Yun 2007 Table 3: 53.5 ± 1.8 vs 2.6 ± 0.2)", test_gefitinib_kd_provenance_and_selectivity),
        ("Test 05: Afatinib Assay Platform & Incubation (Li 2008 ATP/NADH coupled -> PROVISIONAL)", test_afatinib_assay_platform_and_incubation),
        ("Test 06: Osimertinib Recombinant Comparability (Cross 2014 Table 1 -> PROVISIONAL)", test_osimertinib_recombinant_comparability),
        ("Test 07: Missing Protocol Field Not Silently Matched (Irreversible kinetics)", test_missing_protocol_field_not_silently_matched),
        ("Test 08: Incomparable Endpoint Rejection: Kd vs IC50 (INCOMPARABLE_ENDPOINT)", test_kd_vs_ic50_endpoint_rejection),
        ("Test 09: Incomparable Endpoint Rejection: Recombinant vs Cellular (INCOMPARABLE_ENDPOINT)", test_recombinant_vs_cellular_endpoint_rejection),
        ("Test 10: Censored Inequality Handling (>2000 nM not scalar)", test_censored_inequality_handling),
        ("Test 11: HM-EGFR-012 Zero Transfer & Exact ADMET Model Provenance", test_hm_egfr_012_zero_transfer_and_admet_provenance),
        ("Test 12: Pipeline & Target Isolation Regression (2ITZ vs 1IEP)", test_pipeline_and_target_isolation_regression),
        ("Test 13: Moyer 1997 & Carey 2006 Primary Literature Identifiers (PMID 9354447, 16912195)", test_moyer_and_carey_literature_identifiers),
        ("Test 14: Cellular Selectivity Governance (LoVo vs H1975 -> PROVISIONAL_CELLULAR_CONTEXT)", test_cellular_selectivity_non_isogenic_provisional),
        ("Test 15: Caco-2 Permeability Units (log10(cm/s))", test_caco2_logarithmic_units),
        ("Test 16: Docking Terminology (PREDICTED VINA DOCKING SCORE, disclaimer)", test_docking_terminology_predicted_vina_score),
        ("Test 17: Runtime Software Versions (Vina v1.2.7 & Chemprop 2.3.1)", test_runtime_software_versions),
        ("Test 18: Final Stage 4A Scientific Corrections (Assay Method, Provisional Selectivity NULL, Finlay Uncertainty)", test_stage4a_final_scientific_corrections_suite),
    ]

    print("\n" + "=" * 80)
    print("HUMANMOL AI — STAGE 4A FINAL METADATA CORRECTIONS & READINESS TEST SUITE")
    print("=" * 80)
    passed = 0
    failed = 0
    for name, func in tests:
        try:
            func()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            import traceback
            print(f"[FAIL] {name}: {e}")
            traceback.print_exc()
            failed += 1
    print("=" * 80)
    print(f"AUDIT RESULTS: {passed} PASSED, {failed} FAILED (TOTAL: {len(tests)})")
    print("=" * 80 + "\n")
    if failed > 0:
        sys.exit(1)
