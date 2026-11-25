"""
HumanMol AI - Beginner & Non-Biologist User Guide PDF Generator
Creates an illustrated, easy-to-understand, publication-quality PDF guide with embedded diagrams.
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
    Image as RLImage,
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
            self.drawString(54, 750, "HumanMol AI  |  Beginner & Non-Biologist User Guide")
            self.drawRightString(558, 750, "Plain English Edition  -  v1.0")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 45, 558, 45)

        self.drawString(54, 32, "HumanMol AI  -  AI-Driven Medicine Discovery for Everyone")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def generate_beginners_guide_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Valora SaaS Color Palette
    c_primary = colors.HexColor("#2563EB")     # Vibrant Blue
    c_dark = colors.HexColor("#0F172A")        # Slate-900
    c_body = colors.HexColor("#334155")        # Slate-700
    c_muted = colors.HexColor("#64748B")       # Slate-500
    c_border = colors.HexColor("#E2E8F0")      # Slate-200
    c_bg_subtle = colors.HexColor("#F8FAFC")   # Slate-50
    c_card_border = colors.HexColor("#CBD5E1") # Slate-300
    c_accent_green = colors.HexColor("#059669")# Emerald-600

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=c_dark,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=c_dark,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=c_body,
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3.5,
    )

    callout_style = ParagraphStyle(
        "Callout_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=c_dark,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=c_body,
    )

    story = []

    # ==================== PAGE 1: COVER & INTRODUCTION ====================
    story.append(Paragraph("HumanMol AI — Beginner's Guide", title_style))
    story.append(Paragraph("A Plain-English Visual Guide to AI Drug Discovery (No Biology Background Required)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=10))

    # Welcome Card
    intro_p = (
        "<b>Welcome!</b> If you have never studied biology, chemistry, or bioinformatics, you are in the right place. "
        "This guide explains exactly what <b>HumanMol AI</b> does, how medicines are discovered on a computer, and how "
        "you can run real AI drug discovery experiments in just 3 clicks. Every term is explained using simple everyday analogies."
    )
    intro_table = Table([[Paragraph(intro_p, callout_style)]], colWidths=[504])
    intro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(intro_table)
    story.append(Spacer(1, 10))

    # Section 1: The Everyday Analogy
    story.append(Paragraph("1. The Everyday Analogy: How Cancer Drugs Work", h1_style))
    story.append(Paragraph(
        "Imagine your body is a bustling city made of trillions of tiny buildings called <b>cells</b>. "
        "Inside each cell are microscopic machines made of protein that control growth, division, and repair.",
        body_style
    ))
    story.append(Paragraph(
        "• <b>The Broken Switch:</b> In Non-Small Cell Lung Cancer, a specific protein switch named <b>EGFR</b> suffers an accidental typo (mutation <b>L858R</b>). "
        "This typo jams the switch permanently to <b>'ON'</b>, ordering the cells to multiply uncontrollably into a tumor.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>The Key (Drug):</b> To stop the cancer, we need a small chemical molecule that acts like a <b>custom key</b>. "
        "It slides into the keyhole (the active binding pocket) of the broken EGFR switch and turns it off.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>The Traditional Problem:</b> Finding this key in a physical laboratory usually takes <b>10 to 15 years</b>, tests millions of random chemicals, and costs over <b>$2.6 Billion</b>.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>What HumanMol AI Does:</b> Instead of testing physical chemicals by hand, HumanMol AI uses supercomputers and deep learning neural networks "
        "to design brand-new keys from scratch, test if they fit the lock in 3D, and check if they are safe to swallow as pills—all in seconds.",
        bullet_style
    ))
    story.append(Spacer(1, 6))

    # Figure 1: The Drug Discovery Journey
    if os.path.exists("docs/assets/fig1_journey.png"):
        story.append(RLImage("docs/assets/fig1_journey.png", width=504, height=126))
        story.append(Spacer(1, 10))

    # ==================== PAGE 2: THE BEGINNER'S DICTIONARY ====================
    story.append(PageBreak())
    story.append(Paragraph("2. The Beginner's Dictionary: Key Terms in Plain English", h1_style))
    story.append(Paragraph(
        "When using HumanMol AI, you will encounter scientific words. Here is your cheat sheet translating them into plain language:",
        body_style
    ))

    dictionary_data = [
        [Paragraph("Scientific Term", table_header_style), Paragraph("Everyday Translation", table_header_style), Paragraph("Why It Matters in HumanMol AI", table_header_style)],
        [
            Paragraph("<b>Target Protein</b><br/>(e.g., EGFR, c-Abl)", table_cell_style),
            Paragraph("The broken lock inside cancer cells.", table_cell_style),
            Paragraph("This is the exact protein our AI designs molecules to shut down.", table_cell_style)
        ],
        [
            Paragraph("<b>Mutation</b><br/>(e.g., L858R)", table_cell_style),
            Paragraph("A genetic typo that jammed the lock.", table_cell_style),
            Paragraph("L858R is the mutation found in ~40% of lung cancer patients.", table_cell_style)
        ],
        [
            Paragraph("<b>Ligand / Candidate</b>", table_cell_style),
            Paragraph("The potential drug key.", table_cell_style),
            Paragraph("The new chemical molecule created by the AI generator.", table_cell_style)
        ],
        [
            Paragraph("<b>SMILES String</b>", table_cell_style),
            Paragraph("A chemical molecule written as text code.", table_cell_style),
            Paragraph("Example: <code>CC1=C(C=C...</code> lets computers read 3D chemicals like words.", table_cell_style)
        ],
        [
            Paragraph("<b>Molecular Docking</b><br/>(AutoDock Vina)", table_cell_style),
            Paragraph("3D digital puzzle testing.", table_cell_style),
            Paragraph("The computer tests how snugly the key fits inside the protein keyhole.", table_cell_style)
        ],
        [
            Paragraph("<b>Docking Score</b><br/>(kcal/mol)", table_cell_style),
            Paragraph("Binding strength score.<br/><b>More negative = Tighter grip!</b>", table_cell_style),
            Paragraph("-8.5 kcal/mol is much stronger than -5.0 kcal/mol. Tighter binding means a better blocker.", table_cell_style)
        ],
        [
            Paragraph("<b>Lipinski's Rule of 5</b><br/>(Ro5 Pass / Violation)", table_cell_style),
            Paragraph("Can you swallow this as an oral pill?", table_cell_style),
            Paragraph("A 4-part rule checking size and weight so medicine can be taken as a pill rather than injection.", table_cell_style)
        ],
        [
            Paragraph("<b>ADMET Profile</b>", table_cell_style),
            Paragraph("The body's safety and delivery test.", table_cell_style),
            Paragraph("Absorption, Distribution, Metabolism, Excretion, and Toxicity. Ensures drug isn't poisonous to heart or liver.", table_cell_style)
        ],
        [
            Paragraph("<b>MPO Score</b><br/>(0.000 to 1.000)", table_cell_style),
            Paragraph("Overall Report Card Grade.<br/><b>Higher is better!</b>", table_cell_style),
            Paragraph("Composite score combining potency, safety, and oral pill qualities. 0.7+ is a top candidate.", table_cell_style)
        ],
        [
            Paragraph("<b>In Silico vs Wet-Lab</b>", table_cell_style),
            Paragraph("Computer simulation vs Physical test tubes.", table_cell_style),
            Paragraph("HumanMol AI is in silico (simulation). Real scientists must still test candidates in physical wet-labs.", table_cell_style)
        ]
    ]

    dict_table = Table(dictionary_data, colWidths=[105, 155, 244])
    dict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(dict_table)
    story.append(Spacer(1, 10))

    # Figure 2: The Lock & Key Docking
    if os.path.exists("docs/assets/fig2_docking.png"):
        story.append(RLImage("docs/assets/fig2_docking.png", width=504, height=161))
        story.append(Spacer(1, 10))

    # ==================== PAGE 3: ADMET SAFETY & STEP-BY-STEP UI ====================
    story.append(PageBreak())
    story.append(Paragraph("3. Why Safety (ADMET) Matters Before Lab Testing", h1_style))
    story.append(Paragraph(
        "A chemical might stick to a cancer protein like superglue, but if it damages the human heart or is destroyed by the liver, "
        "it can never be given to patients. HumanMol AI runs <b>ADMETlab 3.0</b> across 119 safety checkpoints:",
        body_style
    ))

    # Figure 4: ADMET
    if os.path.exists("docs/assets/fig4_admet.png"):
        story.append(RLImage("docs/assets/fig4_admet.png", width=504, height=121))
        story.append(Spacer(1, 10))

    story.append(Paragraph("4. Step-by-Step Walkthrough: Running Your First Discovery in 60 Seconds", h1_style))
    story.append(Paragraph(
        "Follow these 5 simple steps on your screen to generate and test new candidate molecules:",
        body_style
    ))

    # Figure 3: UI Steps
    if os.path.exists("docs/assets/fig3_ui_steps.png"):
        story.append(RLImage("docs/assets/fig3_ui_steps.png", width=504, height=161))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Step 1 — Start the Software:</b> Double-click <code>start_humanmol.bat</code> or run <code>.\\start_humanmol.ps1</code>. Your browser automatically opens <code>http://localhost:3000</code>.", bullet_style))
    story.append(Paragraph("<b>Step 2 — Pick a Target:</b> In the 'Unified Candidate Discovery Pipeline' card, click the quick button <b>EGFR (2ITZ)</b>.", bullet_style))
    story.append(Paragraph("<b>Step 3 — Choose Number of Candidates:</b> Set candidates to <b>5</b> (or up to 20). Leave reproducibility seed as 42.", bullet_style))
    story.append(Paragraph("<b>Step 4 — Keep Engines Enabled:</b> Ensure all three checkboxes (Chemprop, Vina 3D Docking, ADMETlab) are checked.", bullet_style))
    story.append(Paragraph("<b>Step 5 — Hit Launch:</b> Click the bright blue button <b>LAUNCH DISCOVERY PIPELINE</b>.", bullet_style))
    story.append(Spacer(1, 10))

    # ==================== PAGE 4: READING RESULTS & FAQ ====================
    story.append(PageBreak())
    story.append(Paragraph("5. How to Read Your Results Table", h1_style))
    story.append(Paragraph(
        "Once the AI finishes computing (typically 5–15 seconds), a clean table appears with your candidates. Here is how to evaluate them:",
        body_style
    ))

    cols_data = [
        [Paragraph("Table Column", table_header_style), Paragraph("What It Shows", table_header_style), Paragraph("What You Want to See", table_header_style)],
        [
            Paragraph("<b>RANK</b>", table_cell_style),
            Paragraph("Candidate standing (#1 to #5)", table_cell_style),
            Paragraph("<b>#1</b> is the overall best molecule selected by AI.", table_cell_style)
        ],
        [
            Paragraph("<b>STRUCTURE / SMILES</b>", table_cell_style),
            Paragraph("Chemical text code", table_cell_style),
            Paragraph("Click to copy. Used to view 2D/3D structure.", table_cell_style)
        ],
        [
            Paragraph("<b>RO5 (Rule of 5)</b>", table_cell_style),
            Paragraph("Oral drug-likeness check", table_cell_style),
            Paragraph("Look for green <b>PASS</b> badge (can be made into a pill).", table_cell_style)
        ],
        [
            Paragraph("<b>VINA AFFINITY</b>", table_cell_style),
            Paragraph("How tightly it sticks in 3D", table_cell_style),
            Paragraph("Look for <b>negative numbers</b> (e.g. <b>-7.5 to -9.0 kcal/mol</b>). More negative is better!", table_cell_style)
        ],
        [
            Paragraph("<b>ADMET (HERG / DILI)</b>", table_cell_style),
            Paragraph("Heart and liver toxicity risks", table_cell_style),
            Paragraph("Lower risk score is safer for human health.", table_cell_style)
        ],
        [
            Paragraph("<b>MPO SCORE</b>", table_cell_style),
            Paragraph("The composite final grade", table_cell_style),
            Paragraph("Higher score (e.g. <b>0.700+</b>) means a well-rounded drug candidate.", table_cell_style)
        ],
    ]

    cols_table = Table(cols_data, colWidths=[120, 160, 224])
    cols_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_bg_subtle),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(cols_table)
    story.append(Spacer(1, 10))

    # Section 6: Frequently Asked Questions
    story.append(Paragraph("6. Frequently Asked Questions (FAQ) for Beginners", h1_style))
    story.append(Paragraph("<b>Q: Can I synthesize or take these molecules as medicine right now?</b><br/>"
                           "<b>A: NO.</b> These are virtual computer predictions. Before any molecule can be given to patients, professional chemists must synthesize it in a physical chemistry lab, test it in cell cultures, and conduct multi-year clinical trials.", body_style))
    story.append(Paragraph("<b>Q: What does the 3D viewer do?</b><br/>"
                           "<b>A:</b> In Module 05 (Molecular Docking), the 3D viewer lets you inspect the physical 3D interaction. Left-click and drag your mouse to rotate the protein, use your mouse wheel to zoom in on the binding pocket, and toggle 'Surface' to see the outer envelope of the cancer protein.", body_style))
    story.append(Paragraph("<b>Q: Why do we test both Mutant EGFR and Wild-Type EGFR?</b><br/>"
                           "<b>A:</b> A great cancer medicine must kill the cancer cells (Mutant) while leaving healthy normal cells (Wild-Type) unharmed. This is called <b>Selectivity</b>. HumanMol AI benchmarks reference drugs like Gefitinib and Osimertinib to compare mutant vs normal selectivity.", body_style))
    story.append(Spacer(1, 10))

    # Section 7: Regulatory Notice
    story.append(Paragraph("7. Scientific Rigor Notice", h1_style))
    disclaimer_p = (
        "<b>Important Notice for All Users:</b> HumanMol AI produces in silico mathematical approximations. "
        "A high docking score or high MPO grade does not guarantee therapeutic cure or biological inhibition. "
        "Always interpret computer predictions as preliminary hypotheses that guide real-world laboratory experiments."
    )
    disclaimer_table = Table([[Paragraph(disclaimer_p, callout_style)]], colWidths=[504])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(disclaimer_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Beginner's Guide PDF: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "HumanMol_AI_Beginners_Guide.pdf"
    generate_beginners_guide_pdf(out_file)
