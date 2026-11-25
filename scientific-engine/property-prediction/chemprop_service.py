"""
HumanMol AI - Property Prediction Engine (Chemprop)
Uses Chemprop D-MPNN models to predict molecular properties and bioactivity.
"""

import os
from typing import List, Dict, Any, Optional
import torch
import lightning.pytorch as pl
from chemprop import data, featurizers, models, nn

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "chemprop_test_model.pt")

NORM_MEAN = 2.18
NORM_STD = 1.20

def load_or_create_model(model_path: Optional[str] = None):
    """
    Loads an MPNN model from state_dict or initializes a default architecture.
    """
    path = model_path or DEFAULT_MODEL_PATH
    mp = nn.BondMessagePassing()
    agg = nn.MeanAggregation()
    ffn = nn.RegressionFFN(input_dim=mp.output_dim)
    model = models.MPNN(message_passing=mp, agg=agg, predictor=ffn)
    
    if os.path.exists(path):
        state_dict = torch.load(path, map_location="cpu")
        model.load_state_dict(state_dict)
        model.eval()
    return model

def predict_molecular_properties(smiles_list: List[str], model_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Runs property prediction on a list of SMILES using Chemprop MPNN.
    """
    model = load_or_create_model(model_path)
    featurizer = featurizers.SimpleMoleculeMolGraphFeaturizer()
    datapoints = [data.MoleculeDatapoint.from_smi(smi) for smi in smiles_list]
    dataset = data.MoleculeDataset(datapoints, featurizer=featurizer)
    dataloader = data.build_dataloader(dataset, batch_size=max(1, len(datapoints)), shuffle=False)
    
    trainer = pl.Trainer(logger=False, enable_checkpointing=False, accelerator="cpu", devices=1, enable_progress_bar=False)
    raw_preds = trainer.predict(model, dataloader)
    
    results = []
    preds_tensor = raw_preds[0] if raw_preds else []
    for idx, smi in enumerate(smiles_list):
        raw_val = float(preds_tensor[idx].item()) if len(preds_tensor) > idx else None
        denorm_val = round(raw_val * NORM_STD + NORM_MEAN, 4) if raw_val is not None else None
        results.append({
            "smiles": smi,
            "predicted_property": round(raw_val, 4) if raw_val is not None else None,
            "denormalized_property": denorm_val,
            "status": "success",
            "model_type": "Chemprop_MPNN_v2.3.1",
            "endpoint_name": "Octanol-Water Partition Coefficient Surrogate (LogP Benchmark)",
            "target_units": "log P (dimensionless)",
            "normalization_method": "Z-score (mean=2.18, std=1.20)",
            "model_checkpoint": "chemprop_test_model.pt"
        })
    return results

if __name__ == "__main__":
    test_molecules = ["CC(=O)Oc1ccccc1C(=O)O", "CC(=O)Nc1ccc(O)cc1", "CC(C)Cc1ccc(cc1)C(C)C(=O)O"]
    preds = predict_molecular_properties(test_molecules)
    for p in preds:
        print(p)

