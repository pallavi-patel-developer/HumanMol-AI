"""
HumanMol AI - Molecule Generator Engine (REINVENT4)
Wraps REINVENT4 RNN prior model for targeted and de novo SMILES generation.
"""

import os
import time
from typing import List, Dict, Any, Optional
import torch
import numpy as np

PRIOR_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "REINVENT4", "priors", "reinvent.prior"
)
PRIOR_PATH = os.path.abspath(PRIOR_PATH)

_cached_adapter = None

def get_generator_adapter():
    """Lazily loads and caches the REINVENT4 prior adapter."""
    global _cached_adapter
    if _cached_adapter is None:
        if not os.path.exists(PRIOR_PATH):
            raise FileNotFoundError(f"REINVENT4 prior not found at: {PRIOR_PATH}")
        from reinvent.runmodes.create_adapter import create_adapter
        adapter, _, _ = create_adapter(PRIOR_PATH, "inference", device="cpu")
        _cached_adapter = adapter
    return _cached_adapter

def generate_molecules(
    num_molecules: int = 10,
    seed: Optional[int] = None,
    batch_size: int = 32
) -> Dict[str, Any]:
    """
    Generates de novo chemical molecules using the pretrained REINVENT4 prior.
    
    :param num_molecules: Target count of molecules to generate
    :param seed: Random seed for deterministic reproducibility
    :param batch_size: Sampling batch size
    :return: Dictionary containing generated SMILES, NLLs, and provenance metadata
    """
    t0 = time.time()
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)

    adapter = get_generator_adapter()
    
    all_smiles: List[str] = []
    all_nlls: List[float] = []
    
    remaining = num_molecules
    while remaining > 0:
        current_batch = min(remaining, batch_size)
        sampled = adapter.sample(current_batch)
        all_smiles.extend(sampled.output)
        if hasattr(sampled, "nlls") and sampled.nlls is not None:
            all_nlls.extend([float(n.item()) for n in sampled.nlls])
        remaining -= current_batch

    t1 = time.time()
    
    return {
        "success": True,
        "total_generated": len(all_smiles),
        "smiles": all_smiles,
        "nlls": all_nlls[:len(all_smiles)],
        "execution_time_seconds": round(t1 - t0, 3),
        "seed": seed,
        "model_version": "REINVENT4 v4.9.34",
        "prior_provenance": "Zenodo Record 15641296 (AstraZeneca/MolecularAI)",
        "model_type": "RNN Prior (PubChem/ChEMBL pretrained)",
    }

if __name__ == "__main__":
    res = generate_molecules(num_molecules=3, seed=42)
    print("Generation successful:", res["success"])
    for s, n in zip(res["smiles"], res["nlls"]):
        print(f"  - SMILES: {s} (NLL: {n:.2f})")
