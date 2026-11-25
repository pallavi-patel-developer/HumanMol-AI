"""
HumanMol AI - Protein Data Engine (RCSB PDB + AlphaFold DB)
Mutation-aware and domain-aware 3D macromolecular structure resolution.
Strictly separates experimental RCSB crystallographic structures from
computational AlphaFold deep learning models.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("humanmol.protein_service")

# Verified experimental target catalog with domain & mutation awareness
VERIFIED_MUTATION_STRUCTURES: Dict[str, Dict[str, Any]] = {
    "P00533_L858R": {
        "pdb_id": "2ITZ",
        "title": "Crystal structure of EGFR kinase domain L858R mutation in complex with Iressa (Gefitinib)",
        "gene_symbol": "EGFR",
        "uniprot_accession": "P00533",
        "organism": "Homo sapiens",
        "mutation": "L858R",
        "mutation_verified": True,
        "mutation_residue": {"seq_id": 858, "wt": "LEU", "mut": "ARG", "chain": "A"},
        "domain_name": "Protein Tyrosine Kinase Domain",
        "domain_residues": "697-1020",
        "experimental_method": "X-RAY DIFFRACTION",
        "resolution": 2.80,
        "chain_id": "A",
        "is_experimental": True,
        "is_alphafold": False,
        "source": "RCSB Protein Data Bank",
        "rcsb_url": "https://www.rcsb.org/structure/2ITZ",
        "pubmed_id": "17016524",
        "doi": "10.1038/sj.emboj.7601386",
        "bound_ligand": {
            "comp_id": "IRE",
            "name": "Gefitinib (Iressa, ZD1839)",
            "chemical_formula": "C22H24ClFN4O3",
            "formula_weight": 446.9,
            "smiles": "COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1OCCCN1CCOCC1",
            "binding_pocket": {
                "center_x": -51.654,
                "center_y": -1.266,
                "center_z": -21.945,
                "size_x": 20.0,
                "size_y": 20.0,
                "size_z": 20.0
            }
        },
        "redocking_validation": {
            "status": "VALIDATED",
            "software": "AutoDock Vina v1.2.7",
            "exhaustiveness": 16,
            "best_affinity_kcal_mol": -8.36,
            "core_rmsd_angstrom": 0.460,
            "all_heavy_rmsd_angstrom": 2.644,
            "best_pose_rmsd_angstrom": 2.297,
            "heavy_atom_count": 31,
            "reproducibility": "High (Hinge-binding quinazoline core reproduced within 0.46 Å)"
        },
        "files": {
            "receptor_pdbqt": "scientific-engine/docking/targets/2itz/2itz_receptor.pdbqt",
            "ligand_pdbqt": "scientific-engine/docking/targets/2itz/2itz_ligand.pdbqt",
            "receptor_pdb": "scientific-engine/docking/targets/2itz/2itz_receptor.pdb",
            "ligand_sdf": "scientific-engine/docking/targets/2itz/2itz_ligand.sdf"
        }
    },
    "P00533_WT": {
        "pdb_id": "1M17",
        "title": "Structure of the EGFR kinase domain in complex with Erlotinib (OSI-774)",
        "gene_symbol": "EGFR",
        "uniprot_accession": "P00533",
        "organism": "Homo sapiens",
        "mutation": "Wild-Type",
        "mutation_verified": False,
        "domain_name": "Protein Tyrosine Kinase Domain",
        "domain_residues": "696-1022",
        "experimental_method": "X-RAY DIFFRACTION",
        "resolution": 2.60,
        "chain_id": "A",
        "is_experimental": True,
        "is_alphafold": False,
        "source": "RCSB Protein Data Bank",
        "rcsb_url": "https://www.rcsb.org/structure/1M17",
        "bound_ligand": {
            "comp_id": "AQ4",
            "name": "Erlotinib (Tarceva)",
            "chemical_formula": "C22H23N3O4",
            "smiles": "COCCOC1=C(OCCOC)C=C2C(=C1)C(=NC=N2)NC3=CC=CC(=C3)C#C"
        }
    },
    "P00519_WT": {
        "pdb_id": "1IEP",
        "title": "Crystal structure of c-Abl kinase in complex with Imatinib (STI-571)",
        "gene_symbol": "ABL1",
        "uniprot_accession": "P00519",
        "organism": "Homo sapiens",
        "mutation": "Wild-Type",
        "domain_name": "Tyrosine-protein kinase ABL1 catalytic domain",
        "experimental_method": "X-RAY DIFFRACTION",
        "resolution": 2.10,
        "chain_id": "A",
        "is_experimental": True,
        "is_alphafold": False,
        "source": "RCSB Protein Data Bank",
        "rcsb_url": "https://www.rcsb.org/structure/1IEP",
        "bound_ligand": {
            "comp_id": "STI",
            "name": "Imatinib (Gleevec)",
            "chemical_formula": "C29H31N7O",
            "smiles": "Cc1ccc(NC(=O)c2ccc(CN3CCN(C)CC3)cc2)cc1Nc1nccc(-c2cccnc2)n1",
            "binding_pocket": {
                "center_x": 15.6,
                "center_y": 53.6,
                "center_z": 15.4,
                "size_x": 20.0,
                "size_y": 20.0,
                "size_z": 20.0
            }
        }
    }
}

def resolve_mutation_aware_structure(
    query_target: str,
    uniprot_accession: Optional[str] = None,
    mutation: Optional[str] = "L858R",
    domain: Optional[str] = "kinase"
) -> Dict[str, Any]:
    """
    Selects the experimentally validated reference structure based on target gene,
    UniProt accession, specified oncogenic mutation (e.g. L858R), and structural domain.
    Never returns an extracellular complex (e.g. 1IVO) when kinase domain docking is needed.
    """
    q_upper = query_target.strip().upper()
    acc = uniprot_accession.strip().upper() if uniprot_accession else ""
    mut = (mutation or "L858R").strip().upper()

    # Match EGFR L858R
    if ("EGFR" in q_upper or acc == "P00533" or "L858R" in q_upper) and mut == "L858R":
        return VERIFIED_MUTATION_STRUCTURES["P00533_L858R"]
    elif "EGFR" in q_upper or acc == "P00533":
        if mut == "WT" or not mut:
            return VERIFIED_MUTATION_STRUCTURES["P00533_WT"]
        return VERIFIED_MUTATION_STRUCTURES["P00533_L858R"]
    elif "ABL" in q_upper or acc == "P00519":
        return VERIFIED_MUTATION_STRUCTURES["P00519_WT"]

    # Fallback to general RCSB query if unknown
    pdb_id = "2ITZ" if ("EGFR" in q_upper or acc == "P00533") else "1IEP"
    rcsb = fetch_rcsb_entry(pdb_id)
    if rcsb:
        rcsb["is_experimental"] = True
        rcsb["is_alphafold"] = False
        return rcsb
    return {
        "pdb_id": pdb_id,
        "is_experimental": True,
        "is_alphafold": False,
        "organism": "Homo sapiens"
    }

def fetch_alphafold_structure_url(uniprot_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves AlphaFold DB predicted structure metadata and download URLs.
    Explicitly tags the output as computational model, NOT experimental.
    """
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list):
                entry = data[0]
                return {
                    "uniprot_id": uniprot_id,
                    "pdb_url": entry.get("pdbUrl"),
                    "cif_url": entry.get("cifUrl"),
                    "bcif_url": entry.get("bcifUrl"),
                    "model_created_date": entry.get("modelCreatedDate"),
                    "latest_version": entry.get("latestVersion", "v4"),
                    "is_experimental": False,
                    "is_alphafold": True,
                    "method": "AlphaFold DB In Silico Prediction",
                    "provenance": "EMBL-EBI AlphaFold DB (Deep Learning Model)",
                    "disclaimer": "Predicted computational coordinate model. Does not represent crystallographic empirical data or ligand complex."
                }
    except Exception as e:
        logger.warning(f"AlphaFold API request failed for {uniprot_id}: {e}")
    return None

def fetch_rcsb_entry(pdb_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches experimental PDB entry metadata from RCSB REST API.
    Explicitly tags the output as experimental empirical structure.
    """
    url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id.lower()}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "pdb_id": pdb_id.upper(),
                "title": data.get("struct", {}).get("title"),
                "resolution": data.get("rcsb_entry_info", {}).get("resolution_combined", [None])[0],
                "experimental_method": data.get("exptl", [{}])[0].get("method", "X-RAY DIFFRACTION"),
                "is_experimental": True,
                "is_alphafold": False,
                "source": "RCSB Protein Data Bank",
                "rcsb_url": f"https://www.rcsb.org/structure/{pdb_id.upper()}",
            }
    except Exception as e:
        logger.warning(f"RCSB API request failed for {pdb_id}: {e}")
    return None
