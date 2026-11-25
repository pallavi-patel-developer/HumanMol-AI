"""
Generates high-resolution explanatory infographics for the HumanMol AI Beginner's Guide.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("docs/assets", exist_ok=True)

# -------------------------------------------------------------------------
# Figure 1: The Drug Discovery Journey (From Disease to Cure)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 2.5), dpi=300)
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")
ax.axis('off')

steps = [
    ("1. Disease\nTarget", "Find the broken\ncell protein\n(e.g. EGFR)", "#3B82F6"),
    ("2. AI Molecule\nSampling", "REINVENT4 creates\nmillions of new\nchemical keys", "#8B5CF6"),
    ("3. Lock-and-Key\nDocking", "AutoDock Vina tests\nhow tightly the key\nfits the lock", "#10B981"),
    ("4. Safety &\nADMET", "Check heart, liver,\nand body delivery\nproperties", "#F59E0B"),
    ("5. Best Lead\nCandidate", "Top-ranked molecule\nsent to wet-lab for\nreal verification", "#EF4444")
]

for i, (title, desc, color) in enumerate(steps):
    x = 0.05 + i * 0.19
    # Card box
    rect = patches.FancyBboxPatch((x, 0.15), 0.16, 0.7, boxstyle="round,pad=0.03", 
                                  edgecolor="#CBD5E1", facecolor="white", linewidth=1.5)
    ax.add_patch(rect)
    
    # Top badge bar
    badge = patches.FancyBboxPatch((x+0.01, 0.72), 0.14, 0.10, boxstyle="round,pad=0.01",
                                  facecolor=color, edgecolor="none")
    ax.add_patch(badge)
    ax.text(x+0.08, 0.77, f"STEP 0{i+1}", color="white", fontsize=7.5, weight="bold", ha="center", va="center")
    
    # Title
    ax.text(x+0.08, 0.58, title, color="#0F172A", fontsize=8.5, weight="bold", ha="center", va="center")
    # Description
    ax.text(x+0.08, 0.32, desc, color="#475569", fontsize=6.5, ha="center", va="center")
    
    # Arrow between cards
    if i < 4:
        ax.annotate("", xy=(x + 0.185, 0.5), xytext=(x + 0.165, 0.5),
                    arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2, mutation_scale=15))

plt.tight_layout()
plt.savefig("docs/assets/fig1_journey.png", bbox_inches='tight')
plt.close()
print("Saved fig1_journey.png")

# -------------------------------------------------------------------------
# Figure 2: The Lock-and-Key Concept (What is Docking?)
# -------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.2), dpi=300)
fig.patch.set_facecolor("#F8FAFC")

# Left: Explanation of Lock & Key
ax1.set_facecolor("white")
ax1.set_title("The Biological Lock & Key Analogy", fontsize=10, weight="bold", color="#0F172A", pad=10)
ax1.axis('off')

# Protein (Lock) representation
protein_box = patches.FancyBboxPatch((0.1, 0.2), 0.45, 0.65, boxstyle="round,pad=0.05",
                                     facecolor="#E0E7FF", edgecolor="#6366F1", linewidth=2)
ax1.add_patch(protein_box)
# Pocket cutout
pocket = patches.FancyBboxPatch((0.45, 0.35), 0.2, 0.35, boxstyle="round,pad=0.02",
                                facecolor="#F8FAFC", edgecolor="#6366F1", linewidth=2, linestyle="--")
ax1.add_patch(pocket)

ax1.text(0.3, 0.5, "Cancer Protein\n(The 'Lock')\ne.g., EGFR L858R", color="#3730A3", weight="bold", fontsize=8.5, ha="center")
ax1.text(0.55, 0.28, "Binding Pocket\n(Active Site)", color="#4F46E5", fontsize=7, ha="center")

# Drug Molecule (Key)
drug_box = patches.FancyBboxPatch((0.72, 0.4), 0.22, 0.25, boxstyle="round,pad=0.03",
                                  facecolor="#FEF3C7", edgecolor="#D97706", linewidth=2)
ax1.add_patch(drug_box)
ax1.text(0.83, 0.525, "Drug Candidate\n(The 'Key')", color="#92400E", weight="bold", fontsize=8, ha="center")

# Right: How AutoDock Vina computes affinity
ax2.set_facecolor("white")
ax2.set_title("How to Read Docking Scores (AutoDock Vina)", fontsize=10, weight="bold", color="#0F172A", pad=10)
ax2.axis('off')

scores = [
    ("-10.5 kcal/mol", "Extremely Strong Binding", "Perfect lock fit, tight molecular grip", "#059669"),
    ("-8.2 kcal/mol", "Good Drug-like Binding", "Strong candidate for wet-lab testing", "#2563EB"),
    ("-5.1 kcal/mol", "Weak Binding", "Loose fit, easily falls off target", "#D97706"),
    ("-2.0 kcal/mol", "No Significant Binding", "Fails to block cancer protein", "#DC2626")
]

for idx, (val, label, subtext, clr) in enumerate(scores):
    y = 0.78 - idx * 0.23
    r = patches.FancyBboxPatch((0.05, y-0.08), 0.9, 0.18, boxstyle="round,pad=0.02",
                               facecolor="#F8FAFC", edgecolor="#E2E8F0", linewidth=1)
    ax2.add_patch(r)
    ax2.text(0.1, y+0.01, val, color=clr, weight="bold", fontsize=9)
    ax2.text(0.42, y+0.01, label, color="#0F172A", weight="bold", fontsize=8)
    ax2.text(0.42, y-0.05, subtext, color="#64748B", fontsize=6.5)

plt.tight_layout()
plt.savefig("docs/assets/fig2_docking.png", bbox_inches='tight')
plt.close()
print("Saved fig2_docking.png")

# -------------------------------------------------------------------------
# Figure 3: UI Click-by-Click Guide
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 3.2), dpi=300)
fig.patch.set_facecolor("#F8FAFC")
ax.set_facecolor("white")
ax.axis('off')
ax.set_title("How to Run a Discovery Pipeline in the HumanMol Dashboard", fontsize=11, weight="bold", color="#0F172A", pad=10)

ui_steps = [
    ("[1] SELECT TARGET", "Click quick button:\n'EGFR (2ITZ)'\nor 'c-Abl (1IEP)'", "#2563EB"),
    ("[2] SET CANDIDATES", "Default is 5.\nAI generates 5\noptimized molecules", "#2563EB"),
    ("[3] TURN ON ENGINES", "Leave all 3 checked:\n- Chemprop (Properties)\n- Vina (3D Docking)\n- ADMETlab (Safety)", "#2563EB"),
    ("[4] CLICK LAUNCH", "Hit blue button:\n'LAUNCH DISCOVERY\nPIPELINE'", "#059669"),
    ("[5] READ MPO RANK", "Review Table:\nRank #1 = Best\nComposite Score", "#7C3AED")
]

for i, (title, desc, clr) in enumerate(ui_steps):
    x = 0.03 + i * 0.195
    box = patches.FancyBboxPatch((x, 0.15), 0.175, 0.72, boxstyle="round,pad=0.03",
                                facecolor="#F8FAFC", edgecolor=clr, linewidth=1.5)
    ax.add_patch(box)
    
    top_badge = patches.Rectangle((x, 0.74), 0.175, 0.13, facecolor=clr, edgecolor="none")
    ax.add_patch(top_badge)
    ax.text(x+0.0875, 0.805, title, color="white", fontsize=7.5, weight="bold", ha="center", va="center")
    
    ax.text(x+0.0875, 0.45, desc, color="#334155", fontsize=7.5, ha="center", va="center", multialignment='center')

plt.tight_layout()
plt.savefig("docs/assets/fig3_ui_steps.png", bbox_inches='tight')
plt.close()
print("Saved fig3_ui_steps.png")

# -------------------------------------------------------------------------
# Figure 4: What is ADMET? (The Pill's Journey in the Body)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 2.4), dpi=300)
fig.patch.set_facecolor("#F8FAFC")
ax.set_facecolor("white")
ax.axis('off')
ax.set_title("ADMET: The 5 Critical Tests for a Safe Medicine", fontsize=10, weight="bold", color="#0F172A", pad=8)

admet_items = [
    ("A", "Absorption", "Does the drug get\nfrom stomach into\nthe bloodstream?", "#3B82F6"),
    ("D", "Distribution", "Does the drug reach\nthe tumor tissue\nand lung cells?", "#8B5CF6"),
    ("M", "Metabolism", "Does the liver\nprocess the drug\nsafely without toxins?", "#10B981"),
    ("E", "Excretion", "Can the kidneys\nflush waste products\nout safely?", "#F59E0B"),
    ("T", "Toxicity", "Is it toxic to heart\n(hERG) or liver (DILI)?\nLower risk is best!", "#EF4444")
]

for i, (letter, name, text, clr) in enumerate(admet_items):
    x = 0.04 + i * 0.192
    box = patches.FancyBboxPatch((x, 0.12), 0.17, 0.74, boxstyle="round,pad=0.03",
                                facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.2)
    ax.add_patch(box)
    
    circle = patches.Circle((x+0.085, 0.72), 0.08, facecolor=clr, edgecolor="none")
    ax.add_patch(circle)
    ax.text(x+0.085, 0.72, letter, color="white", fontsize=11, weight="bold", ha="center", va="center")
    
    ax.text(x+0.085, 0.52, name, color="#0F172A", fontsize=8.5, weight="bold", ha="center")
    ax.text(x+0.085, 0.28, text, color="#475569", fontsize=6.5, ha="center", multialignment='center')

plt.tight_layout()
plt.savefig("docs/assets/fig4_admet.png", bbox_inches='tight')
plt.close()
print("Saved fig4_admet.png")
