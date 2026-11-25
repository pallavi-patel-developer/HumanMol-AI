"""
HumanMol AI - Professional User Guide PDF Generator
Uses ReportLab to generate a clean, multi-page, publication-quality User Guide.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "HumanMol AI  |  Platform User Guide & Operational Manual")
            self.drawRightString(558, 750, "v1.0.0-PROD")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 45, 558, 45)

        self.drawString(54, 32, "Confidential  -  For Translational Bioinformatics & Research Use Only")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def generate_user_guide_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Color Palette matching Valora SaaS theme
    c_primary = colors.HexColor("#2563EB")     # Vibrant Blue
    c_dark = colors.HexColor("#0F172A")        # Slate-900
    c_body = colors.HexColor("#334155")        # Slate-700
    c_muted = colors.HexColor("#64748B")       # Slate-500
    c_border = colors.HexColor("#E2E8F0")      # Slate-200
    c_bg_subtle = colors.HexColor("#F8FAFC")   # Slate-50
    c_emerald = colors.HexColor("#059669")     # Emerald-600
    c_card_bg = colors.HexColor("#FFFFFF")     # White

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_dark,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=c_dark,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=c_body,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=c_dark,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=c_dark,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_body,
    )

    story = []

    # ==================== COVER / HEADER BANNER ====================
    story.append(Paragraph("HumanMol AI Platform", title_style))
    story.append(Paragraph("User Guide & Operational Manual  |  Translational Bioinformatics Suite", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=14))

    # Executive Summary Card
    summary_text = (
        "<b>Executive Overview:</b> HumanMol AI is a unified, multi-engine computational biology "
        "and <i>de novo</i> drug discovery platform engineered for precision oncology. It bridges target "
        "disease biology, neural generative chemistry (REINVENT4), neural graph QSAR regression (Chemprop D-MPNN), "
        "structural protein-ligand docking (AutoDock Vina), ADMET pharmacokinetics (ADMETlab 3.0), "
        "and published wet-lab experimental bioactivity benchmarks into an integrated research workflow."
    )
    summary_table = Table(
        [[Paragraph(summary_text, callout_style)]],
        colWidths=[504],
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # ==================== SECTION 1: ARCHITECTURE ====================
    story.append(Paragraph("1. System Architecture & Workspaces Directory", h1_style))
    story.append(Paragraph(
        "HumanMol AI organizes translational drug discovery into 10 connected scientific workspaces, "
        "accessible directly from the left navigation sidebar:",
        body_style
    ))

    modules_data = [
        [Paragraph("Module", table_header_style), Paragraph("Workspace Name", table_header_style), Paragraph("Underlying Engine / Databases", table_header_style), Paragraph("Primary Scientific Function", table_header_style)],
        [Paragraph("<b>01</b>", table_cell_style), Paragraph("Disease Intelligence", table_cell_style), Paragraph("ICD-11, OMIM, DisGeNET", table_cell_style), Paragraph("Disease etiology, resistance mutations, target phenotype associations.", table_cell_style)],
        [Paragraph("<b>02</b>", table_cell_style), Paragraph("Target Explorer", table_cell_style), Paragraph("UniProt KB, Reactome, RCSB", table_cell_style), Paragraph("Kinase sequence domains, biological signaling cascades, PDB crystals.", table_cell_style)],
        [Paragraph("<b>02B</b>", table_cell_style), Paragraph("Bioactivity Intel", table_cell_style), Paragraph("ChEMBL, Primary Literature", table_cell_style), Paragraph("Curated wet-lab IC50/Ki/Kd benchmarks, intra-study selectivity ratios.", table_cell_style)],
        [Paragraph("<b>03</b>", table_cell_style), Paragraph("Molecule Generation", table_cell_style), Paragraph("REINVENT4 Prior (PyTorch)", table_cell_style), Paragraph("De novo chemical sampling, NLL likelihood scoring, Lipinski filtering.", table_cell_style)],
        [Paragraph("<b>04</b>", table_cell_style), Paragraph("Molecular Properties", table_cell_style), Paragraph("Chemprop D-MPNN", table_cell_style), Paragraph("Neural message passing graph regression, physicochemical QSAR scoring.", table_cell_style)],
        [Paragraph("<b>05</b>", table_cell_style), Paragraph("Molecular Docking", table_cell_style), Paragraph("AutoDock Vina 1.2.7 + 3Dmol", table_cell_style), Paragraph("Structural binding affinity (kcal/mol), RMSD poses, WebGL 3D rendering.", table_cell_style)],
        [Paragraph("<b>06</b>", table_cell_style), Paragraph("ADMET & Toxicity", table_cell_style), Paragraph("ADMETlab 3.0 (119 Endpoints)", table_cell_style), Paragraph("Caco-2 permeability, hERG cardiac toxicity, DILI liver liability, BBB.", table_cell_style)],
        [Paragraph("<b>07</b>", table_cell_style), Paragraph("Cellular Response", table_cell_style), Paragraph("XPert Transformer (CPU/GPU)", table_cell_style), Paragraph("Transcriptomic cellular perturbation & differential gene expression.", table_cell_style)],
        [Paragraph("<b>08</b>", table_cell_style), Paragraph("Research Evidence", table_cell_style), Paragraph("PubMed Entrez + arXiv API", table_cell_style), Paragraph("Literature mining, clinical trial citations, preprint PDF linking.", table_cell_style)],
        [Paragraph("<b>09</b>", table_cell_style), Paragraph("Candidate Explorer", table_cell_style), Paragraph("MPO Ranking Engine", table_cell_style), Paragraph("Composite Multi-Parameter Optimization leaderboard & pairwise comparison.", table_cell_style)],
        [Paragraph("<b>10</b>", table_cell_style), Paragraph("Research Reports", table_cell_style), Paragraph("Dossier Generator", table_cell_style), Paragraph("Automated export of reproducible audit dossiers in PDF, JSON, and MD.", table_cell_style)],
    ]

    modules_table = Table(modules_data, colWidths=[42, 110, 140, 212])
    modules_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(modules_table)
    story.append(Spacer(1, 14))

    # ==================== SECTION 2: WORKFLOWS ====================
    story.append(Paragraph("2. Primary Operational Workflows", h1_style))

    # Workflow 1
    story.append(Paragraph("Workflow A: Executing the Unified Discovery Pipeline (One-Click)", h2_style))
    story.append(Paragraph(
        "The Executive Dashboard (<code>/</code>) provides automated end-to-end batch execution connecting sampling to profiling:",
        body_style
    ))
    story.append(Paragraph("• <b>Step 1 — Target Selection:</b> Select pre-configured target preset (e.g. <i>EGFR L858R (2ITZ)</i> or <i>c-Abl (1IEP)</i>) or enter custom kinase target.", bullet_style))
    story.append(Paragraph("• <b>Step 2 — Batch Parameters:</b> Define number of candidates (1–20) and integer reproducibility seed (e.g. 42).", bullet_style))
    story.append(Paragraph("• <b>Step 3 — Engine Toggles:</b> Check or uncheck <i>Chemprop D-MPNN Screen</i>, <i>AutoDock Vina 3D Docking</i>, and <i>ADMETlab 3.0 Profiling</i> according to screening depth required.", bullet_style))
    story.append(Paragraph("• <b>Step 4 — Execution & Table Inspection:</b> Click <b>LAUNCH DISCOVERY PIPELINE</b>. Inspect generated candidates sorted by composite MPO rank.", bullet_style))
    story.append(Paragraph("• <b>Step 5 — Candidate Dossier:</b> Click any row in the results table to reveal its 2D chemical card, SMILES string, physicochemical metrics, and single-click links for deep inspection.", bullet_style))
    story.append(Spacer(1, 6))

    # Workflow 2
    story.append(Paragraph("Workflow B: Interactive 3D Protein-Ligand Pose Inspection", h2_style))
    story.append(Paragraph(
        "Module 05 (<code>/docking</code>) provides real-time WebGL visualization of computed binding modes:",
        body_style
    ))
    story.append(Paragraph("• <b>Navigation:</b> Left-click + drag to rotate molecule in 3D space; right-click + drag to pan; mouse wheel to zoom.", bullet_style))
    story.append(Paragraph("• <b>Style Presets:</b> Toggle between <b>Cartoon</b> (secondary structure backbone), <b>Sticks</b> (amino acid sidechains), and <b>Spheres</b> (van der Waals radii).", bullet_style))
    story.append(Paragraph("• <b>Surface & Spin:</b> Toggle <b>Surface</b> for solvent-accessible surface envelope; toggle <b>Spin</b> for continuous 360° orbital rotation.", bullet_style))
    story.append(Spacer(1, 6))

    # Workflow 3
    story.append(Paragraph("Workflow C: Wet-Lab Bioactivity & Selectivity Auditing", h2_style))
    story.append(Paragraph(
        "Module 02B (<code>/bioactivity</code>) prevents computational hallucination by anchoring predictions to verified experimental literature:",
        body_style
    ))
    story.append(Paragraph("• <b>Reference Inhibitors:</b> Compare against approved standards: Gefitinib, Erlotinib, Afatinib, and Osimertinib.", bullet_style))
    story.append(Paragraph("• <b>Assay Compartments:</b> Filter across Recombinant Enzyme Assays, Cellular Target Engagement, and Cell Growth Proliferation.", bullet_style))
    story.append(Paragraph("• <b>Strict Intra-Study Selectivity:</b> Selectivity ratios (e.g. Gefitinib Kd WT 53.5 nM vs L858R 2.6 nM = 20.58× mutant-selective) are only computed when assay conditions and protocols are directly comparable.", bullet_style))
    story.append(Spacer(1, 14))

    # ==================== SECTION 3: DEPLOYMENT ====================
    story.append(Paragraph("3. Local Deployment & Environment Setup", h1_style))
    story.append(Paragraph(
        "HumanMol AI is designed for seamless operation on Windows 10/11 or Linux workstations with minimal setup.",
        body_style
    ))

    setup_data = [
        [Paragraph("Component", table_header_style), Paragraph("Command / Script", table_header_style), Paragraph("Default Address", table_header_style)],
        [Paragraph("<b>One-Click Launcher</b>", table_cell_style), Paragraph("<code>.\\start_humanmol.ps1</code> or <code>start_humanmol.bat</code>", code_style), Paragraph("Opens Web Browser", table_cell_style)],
        [Paragraph("<b>FastAPI Engine</b>", table_cell_style), Paragraph("<code>python scientific-engine/main.py</code>", code_style), Paragraph("http://localhost:8000", table_cell_style)],
        [Paragraph("<b>Next.js Frontend</b>", table_cell_style), Paragraph("<code>cd frontend; npm run dev</code>", code_style), Paragraph("http://localhost:3000", table_cell_style)],
        [Paragraph("<b>OpenAPI Docs</b>", table_cell_style), Paragraph("Interactive Swagger UI", table_cell_style), Paragraph("http://localhost:8000/docs", table_cell_style)],
        [Paragraph("<b>Health Telemetry</b>", table_cell_style), Paragraph("Engine status & active database dialect", table_cell_style), Paragraph("http://localhost:8000/health", table_cell_style)],
    ]

    setup_table = Table(setup_data, colWidths=[110, 244, 150])
    setup_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(setup_table)
    story.append(Spacer(1, 14))

    # ==================== SECTION 4: RIGOR NOTICE ====================
    story.append(Paragraph("4. Scientific Rigor & Compliance Standards", h1_style))
    
    notice_text = (
        "<b>MANDATORY REGULATORY COMPLIANCE NOTICE:</b><br/>"
        "All computational outputs generated by HumanMol AI—including de novo structures, "
        "Chemprop QSAR predictions, AutoDock Vina binding scores (kcal/mol), and ADMETlab 3.0 toxicity "
        "profiles—represent in silico mathematical approximations. <b>Under no circumstances should "
        "computational docking scores be interpreted as clinical efficacy or proof of biological inhibition.</b> "
        "All candidate molecules require rigorous in vitro biochemical assay validation and in vivo wet-lab "
        "pharmacological testing prior to therapeutic development."
    )
    notice_table = Table(
        [[Paragraph(notice_text, callout_style)]],
        colWidths=[504],
    )
    notice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FECACA")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(notice_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "HumanMol_AI_User_Guide.pdf"
    generate_user_guide_pdf(out_file)
