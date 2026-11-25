# HumanMol AI

> **Disease-to-Molecule Discovery & Biological Intelligence Platform**  
> Unified translational bioinformatics architecture connecting target discovery, *de novo* generative chemistry, neural property prediction, 3D molecular docking, ADMET pharmacokinetics, and experimental bioactivity benchmarks.
>
> 📘 **[Beginner's & Non-Biologist Visual Guide (PDF)](HumanMol_AI_Beginners_Guide.pdf)** — *Step-by-step illustrated manual with plain English definitions, analogies, and click-by-click instructions.*  
> 📖 **[Platform User Guide & Operational Manual (PDF)](HumanMol_AI_User_Guide.pdf)** — *Technical reference for researchers, data models, and deployment configurations.*

---

## Overview

**HumanMol AI** is an end-to-end computational biology and drug discovery platform focused on precision oncology (e.g. Non-Small Cell Lung Cancer / EGFR L858R, CML / c-Abl). It bridges the gap between computational molecular design and verified wet-lab bioactivity evidence without conflating in silico approximations with experimental reality.

---

## Core Capabilities & Scientific Engines

1. **Disease & Target Intelligence (Modules 01 & 02)**
   - Curates target disease associations across ICD-11, OMIM, and DisGeNET.
   - Resolves UniProt KB sequences, functional kinase domains, PDB crystal structures (e.g., EGFR `2ITZ`, c-Abl `1IEP`), and Reactome downstream signaling pathways.

2. **Experimental Bioactivity Intelligence (Module 02B)**
   - Connects primary literature benchmarks (Gefitinib, Erlotinib, Afatinib, Osimertinib) with curated ChEMBL records.
   - Rigorous intra-study selectivity ratios (e.g., Gefitinib $K_d$ intra-assay ratio: 20.58× mutant-selective) strictly distinguishing enzyme inhibition, binding constants, and cellular anti-proliferation assays.

3. **De Novo Molecule Generation (Module 03)**
   - Deep generative chemical sampling using **REINVENT4** with official ChEMBL priors, NLL scoring, and Lipinski Rule of 5 filtering.

4. **Molecular Property Estimation (Module 04)**
   - Directed Message Passing Neural Networks (**Chemprop D-MPNN**) for molecular featurization and quantitative structure-activity relationship (QSAR) scoring.

5. **3D Protein-Ligand Docking (Module 05)**
   - Physics-based docking with **AutoDock Vina v1.2.7** against isolated target receptor grids with real-time WebGL molecular visualization powered by **3Dmol.js**.

6. **ADMET & Toxicity Profiling (Module 06)**
   - Pharmacokinetic profiling across 119 endpoints via **ADMETlab 3.0** (Caco-2 permeability, hERG cardiac liability, DILI hepatotoxicity, blood-brain barrier penetration).

7. **Cellular Response & Perturbation (Module 07)**
   - Transcriptomic perturbation tracking powered by the **XPert** Dual-Branch Transformer architecture.

8. **Research Evidence & Decision Dossier (Modules 08, 09 & 10)**
   - Automated literature evidence retrieval from PubMed and arXiv preprints.
   - Multi-Parameter Optimization (MPO) composite ranking and downloadable scientific research dossiers.

---

## System Architecture

```
HumanMol AI/
├── frontend/                     # Next.js 14 App Router, TypeScript, Tailwind CSS
├── scientific-engine/            # FastAPI Scientific Microservice
│   ├── api/                      # REST routers and Pydantic schemas
│   ├── molecule-generator/       # REINVENT4 generative pipeline
│   ├── chemistry/                # RDKit cheminformatics services
│   ├── property-prediction/      # Chemprop D-MPNN graph models
│   ├── docking/                  # AutoDock Vina binary runner & PDBQT prep
│   ├── admet/                    # ADMETlab 3.0 API client
│   ├── cell-response/            # XPert transcriptomic model
│   ├── biological-data/          # UniProt & ChEMBL benchmark integration
│   ├── pathways/                 # Reactome pathway mappings
│   └── research-evidence/        # PubMed (NCBI Entrez) & arXiv miners
├── database/                     # SQLAlchemy models, PostgreSQL / SQLite backend
├── docker/                       # Dockerfile.scientific & docker-compose.yml
└── scripts/                      # Automated pipeline runners and verification audits
```

---

## Tech Stack

- **Frontend Interface:** Next.js 14, TypeScript, Tailwind CSS, Lucide Icons, 3Dmol.js
- **Scientific Backend:** FastAPI, Python 3.11, PyTorch, PyTorch Geometric, RDKit, Chemprop, Biopython
- **Molecular Simulation:** AutoDock Vina v1.2.7 (64-bit)
- **Data Persistence:** PostgreSQL / SQLite with SQLAlchemy ORM

---

## Getting Started

### Prerequisites

- Node.js 18.x or later & npm
- Conda (Miniconda / Anaconda) with Python 3.11
- AutoDock Vina v1.2.7 (included in `scientific-engine/docking/`)

### 1. Environment Setup

```powershell
# Clone the repository
git clone https://github.com/pallavi-patel-developer/HumanMol-AI.git
cd HumanMol-AI

# Create or activate the Conda environment
conda activate humanmol-xpert

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Launch Services

#### Option A: One-Click Launcher (Windows)
Run the automated launcher script to start both backend and frontend:
```powershell
.\start_humanmol.ps1
```
or run `start_humanmol.bat`.

#### Option B: Manual Execution

**Start Scientific Engine (Port 8000):**
```powershell
python scientific-engine/main.py
```

**Start Next.js Dashboard (Port 3000):**
```bash
cd frontend
npm run dev
```

---

## Service Endpoints

| Service | URL | Description |
|---|---|---|
| **Web Dashboard** | `http://localhost:3000` | Modern SaaS Discovery Dashboard |
| **FastAPI Backend** | `http://localhost:8000` | REST API Scientific Engine |
| **Interactive API Docs** | `http://localhost:8000/docs` | Swagger / OpenAPI Documentation |
| **Health Check** | `http://localhost:8000/health` | Engine & Database Status |

---

## Scientific Rigor & Regulatory Notice

Computational predictions (including molecular generation, Chemprop QSAR scores, ADMET profiles, and AutoDock Vina docking scores) represent in silico mathematical approximations. Docking affinity scores do not constitute proof of biological inhibition or clinical efficacy. All generated candidate molecules require in vitro assay verification and in vivo wet-lab experimental validation before therapeutic consideration.

---

## License

This project is licensed under the [MIT License](LICENSE).
