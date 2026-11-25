"""
HumanMol AI - Molecular Docking Engine (AutoDock Vina)
Handles receptor validation, ligand validation, grid box parameters,
isolated experiment execution, output parsing, and error diagnostics.
"""

import os
import hashlib
import subprocess
from typing import Dict, Any, Optional, List

VINA_BIN = os.path.join(os.path.dirname(__file__), "vina.exe")

def calculate_file_sha256(filepath: str) -> Optional[str]:
    """Calculates SHA256 checksum of a file for provenance verification."""
    if not os.path.isfile(filepath):
        return None
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def parse_vina_output(output_pdbqt: str) -> List[Dict[str, float]]:
    """Parses docked poses and affinities from a Vina output PDBQT file."""
    modes = []
    if not os.path.exists(output_pdbqt) or os.path.getsize(output_pdbqt) == 0:
        return modes
    
    with open(output_pdbqt, "r", encoding="utf-8", errors="replace") as f:
        current_mode = None
        for line in f:
            if line.startswith("MODEL"):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        current_mode = int(parts[1])
                    except ValueError:
                        current_mode = len(modes) + 1
            elif line.startswith("REMARK VINA RESULT:"):
                parts = line.split()
                if len(parts) >= 6 and current_mode is not None:
                    try:
                        modes.append({
                            "mode": current_mode,
                            "affinity_kcal_mol": float(parts[3]),
                            "rmsd_lb": float(parts[4]),
                            "rmsd_ub": float(parts[5]),
                        })
                    except ValueError:
                        pass
    return modes

def validate_pdbqt_file(filepath: str, label: str = "PDBQT") -> Dict[str, Any]:
    """Validates that a PDBQT file exists, is non-empty, and readable."""
    if not os.path.exists(filepath):
        return {"valid": False, "error": f"{label} file not found: {filepath}"}
    if not os.path.isfile(filepath):
        return {"valid": False, "error": f"{label} path is not a regular file: {filepath}"}
    if os.path.getsize(filepath) == 0:
        return {"valid": False, "error": f"{label} file is empty (0 bytes): {filepath}"}
    
    # Verify basic PDBQT content (at least one ATOM/HETATM line)
    has_atoms = False
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("ATOM") or line.startswith("HETATM") or line.startswith("ROOT"):
                    has_atoms = True
                    break
    except Exception as e:
        return {"valid": False, "error": f"Could not read {label} file: {e}"}
    
    if not has_atoms:
        return {"valid": False, "error": f"{label} file contains no ATOM or HETATM coordinates: {filepath}"}
    
    return {"valid": True, "size_bytes": os.path.getsize(filepath), "sha256": calculate_file_sha256(filepath)}

def run_docking(
    receptor_pdbqt: str,
    ligand_pdbqt: str,
    center_x: float,
    center_y: float,
    center_z: float,
    size_x: float = 20.0,
    size_y: float = 20.0,
    size_z: float = 20.0,
    out_pdbqt: Optional[str] = None,
    exhaustiveness: int = 8
) -> Dict[str, Any]:
    """
    Runs AutoDock Vina molecular docking with strict error diagnosis,
    parameter validation, and full execution output capture.
    """
    # 1. Validate receptor PDBQT
    rec_val = validate_pdbqt_file(receptor_pdbqt, label="Receptor PDBQT")
    if not rec_val["valid"]:
        return {
            "success": False,
            "exit_code": 2,
            "error": rec_val["error"],
            "stdout": "",
            "stderr": rec_val["error"],
            "command": ""
        }

    # 2. Validate ligand PDBQT
    lig_val = validate_pdbqt_file(ligand_pdbqt, label="Ligand PDBQT")
    if not lig_val["valid"]:
        return {
            "success": False,
            "exit_code": 2,
            "error": lig_val["error"],
            "stdout": "",
            "stderr": lig_val["error"],
            "command": ""
        }

    # 3. Validate grid box dimensions
    if size_x <= 0 or size_y <= 0 or size_z <= 0:
        err = f"Invalid grid box dimensions: size_x={size_x}, size_y={size_y}, size_z={size_z}. All box sizes must be strictly positive (> 0 Å)."
        return {
            "success": False,
            "exit_code": 2,
            "error": err,
            "stdout": "",
            "stderr": err,
            "command": ""
        }

    # 4. Resolve output PDBQT path & ensure directory exists
    if not out_pdbqt:
        out_pdbqt = ligand_pdbqt.replace(".pdbqt", "_out.pdbqt")
    out_dir = os.path.dirname(os.path.abspath(out_pdbqt))
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        err = f"Failed to create docking output directory '{out_dir}': {e}"
        return {
            "success": False,
            "exit_code": 2,
            "error": err,
            "stdout": "",
            "stderr": err,
            "command": ""
        }

    # 5. Locate Vina binary
    vina_exec = VINA_BIN if os.path.exists(VINA_BIN) else "vina"

    cmd = [
        vina_exec,
        "--receptor", receptor_pdbqt,
        "--ligand", ligand_pdbqt,
        "--center_x", str(center_x),
        "--center_y", str(center_y),
        "--center_z", str(center_z),
        "--size_x", str(size_x),
        "--size_y", str(size_y),
        "--size_z", str(size_z),
        "--out", out_pdbqt,
        "--exhaustiveness", str(exhaustiveness),
    ]

    cmd_str = " ".join(f'"{c}"' if " " in c else c for c in cmd)

    try:
        # Run without check=True to directly capture non-zero exit codes and stderr
        res = subprocess.run(cmd, capture_output=True, text=True)
        stdout = res.stdout or ""
        stderr = res.stderr or ""
        exit_code = res.returncode

        if exit_code != 0:
            # Parse specific error line from stderr or stdout
            clean_error = None
            for line in stderr.splitlines():
                line_s = line.strip()
                if line_s.startswith("Error:") or line_s.startswith("Vina runtime error:") or "error" in line_s.lower():
                    clean_error = line_s
                    break
            if not clean_error:
                clean_error = stderr.strip() or stdout.strip() or f"AutoDock Vina process terminated with non-zero exit code {exit_code}."
            
            return {
                "success": False,
                "exit_code": exit_code,
                "error": clean_error,
                "stdout": stdout,
                "stderr": stderr,
                "command": cmd_str,
                "output_file": out_pdbqt,
                "receptor_sha256": rec_val.get("sha256"),
                "ligand_sha256": lig_val.get("sha256"),
            }

        # Exit code 0: parse output
        modes = parse_vina_output(out_pdbqt)
        if not modes:
            return {
                "success": False,
                "exit_code": 0,
                "error": f"AutoDock Vina completed (code 0) but generated no valid binding modes in {out_pdbqt}.",
                "stdout": stdout,
                "stderr": stderr,
                "command": cmd_str,
                "output_file": out_pdbqt,
                "receptor_sha256": rec_val.get("sha256"),
                "ligand_sha256": lig_val.get("sha256"),
            }

        return {
            "success": True,
            "exit_code": 0,
            "output_file": out_pdbqt,
            "best_affinity_kcal_mol": modes[0]["affinity_kcal_mol"],
            "modes": modes,
            "stdout": stdout,
            "stderr": stderr,
            "command": cmd_str,
            "receptor_sha256": rec_val.get("sha256"),
            "ligand_sha256": lig_val.get("sha256"),
        }

    except Exception as e:
        return {
            "success": False,
            "exit_code": -1,
            "error": f"Subprocess invocation failure: {str(e)}",
            "stdout": "",
            "stderr": str(e),
            "command": cmd_str,
            "output_file": out_pdbqt,
        }
