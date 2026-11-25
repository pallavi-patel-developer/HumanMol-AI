"""
HumanMol AI - Core Chemistry Engine (RDKit)
Provides molecular validation, canonicalization, descriptor calculation, and structure generation.
"""

from typing import Dict, Any, Optional

def validate_and_parse_smiles(smiles: str) -> Dict[str, Any]:
    """Validates SMILES string and computes molecular descriptors."""
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Lipinski, Crippen

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"valid": False, "error": f"Invalid SMILES string: {smiles}"}

    canonical_smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
    mw = Descriptors.MolWt(mol)
    logp = Crippen.MolLogP(mol)
    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    tpsa = Descriptors.TPSA(mol)
    rotatable_bonds = Lipinski.NumRotatableBonds(mol)

    # Lipinski's Rule of Five check
    ro5_passed = (mw <= 500) and (logp <= 5) and (hbd <= 5) and (hba <= 10)

    return {
        "valid": True,
        "smiles": canonical_smiles,
        "formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
        "molecular_weight": round(mw, 2),
        "logp": round(logp, 2),
        "hbd": hbd,
        "hba": hba,
        "tpsa": round(tpsa, 2),
        "rotatable_bonds": rotatable_bonds,
        "lipinski_ro5": ro5_passed,
    }

if __name__ == "__main__":
    import sys
    test_smiles = sys.argv[1] if len(sys.argv) > 1 else "CC(=O)OC1=CC=CC=C1C(=O)O"  # Aspirin
    print(validate_and_parse_smiles(test_smiles))
