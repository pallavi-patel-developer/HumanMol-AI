'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Activity,
  Search,
  ArrowRight,
  ShieldAlert,
  Dna,
  GitBranch,
  Layers,
} from 'lucide-react';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';

interface DiseaseEntry {
  id: string;
  name: string;
  category: string;
  icdCode: string;
  primaryTargets: { symbol: string; accession: string; role: string; pdbId: string }[];
  pathways: string[];
  hallmarks: string[];
  resistanceMutations: string[];
  approvedDrugs: string[];
  description: string;
}

const CURATED_DISEASES: DiseaseEntry[] = [
  {
    id: 'cml',
    name: 'Chronic Myeloid Leukemia (CML)',
    category: 'Hematologic Oncology',
    icdCode: 'C92.1',
    primaryTargets: [
      { symbol: 'ABL1', accession: 'P00519', role: 'Constitutive tyrosine kinase driver (BCR-ABL1 fusion)', pdbId: '1IEP' },
      { symbol: 'SRC', accession: 'P12931', role: 'Downstream survival signaling kinase', pdbId: '1Y57' },
    ],
    pathways: ['RAF/MAP kinase cascade', 'PI3K/AKT Signaling in Cancer', 'Signaling by Receptor Tyrosine Kinases'],
    hallmarks: ['Sustained proliferative signaling', 'Evading growth suppressors', 'Resisting cell death'],
    resistanceMutations: ['T315I (Gatekeeper mutation resistant to 1st/2nd gen TKIs)', 'E255K', 'Y253H', 'F317L'],
    approvedDrugs: ['Imatinib (Gleevec)', 'Dasatinib (Sprycel)', 'Nilotinib (Tasigna)', 'Ponatinib (Iclusig)', 'Asciminib'],
    description: 'A myeloproliferative neoplasm characterized by the Philadelphia chromosome t(9;22)(q34;q11) translocation producing the constitutively active BCR-ABL1 oncogenic fusion kinase.',
  },
  {
    id: 'nsclc-egfr',
    name: 'Non-Small Cell Lung Cancer (EGFR-Mutant NSCLC)',
    category: 'Thoracic Oncology',
    icdCode: 'C34.9',
    primaryTargets: [
      { symbol: 'EGFR', accession: 'P00533', role: 'ErbB family receptor tyrosine kinase driver (L858R kinase domain)', pdbId: '2ITZ' },
      { symbol: 'MET', accession: 'P08581', role: 'Bypass resistance receptor kinase', pdbId: '2WGJ' },
    ],
    pathways: ['EGFR Signaling Pathway', 'MAPK family signaling cascades', 'PIP3 activates AKT signaling'],
    hallmarks: ['Sustained proliferative signaling', 'Inducing angiogenesis', 'Activating invasion & metastasis'],
    resistanceMutations: ['T790M (Exon 20 gatekeeper resistance to gefitinib/erlotinib)', 'C797S (Exon 20 resistance to osimertinib)'],
    approvedDrugs: ['Gefitinib (Iressa)', 'Erlotinib (Tarceva)', 'Osimertinib (Tagrisso)', 'Afatinib'],
    description: 'Adenocarcinoma of the lung harboring activating somatic mutations in EGFR kinase domain (Exon 19 del, L858R point mutation) conferring oncogene addiction.',
  },
  {
    id: 'melanoma-braf',
    name: 'Cutaneous Malignant Melanoma (BRAF V600E)',
    category: 'Dermatologic Oncology',
    icdCode: 'C43.9',
    primaryTargets: [
      { symbol: 'BRAF', accession: 'P15056', role: 'Serine/threonine-protein kinase catalytic driver', pdbId: '4MNE' },
      { symbol: 'MEK1 (MAP2K1)', accession: 'Q02750', role: 'Downstream MAPK pathway dual-specificity kinase', pdbId: '3PP1' },
    ],
    pathways: ['Oncogenic MAPK signaling', 'Cell Cycle checkpoints', 'Transcriptional regulation by AP-1'],
    hallmarks: ['Sustained proliferative signaling', 'Resisting cell death', 'Reprogramming energy metabolism'],
    resistanceMutations: ['MEK1 C121S', 'BRAF splicing variants (p61BRAF-V600E)', 'NRAS Q61K'],
    approvedDrugs: ['Vemurafenib (Zelboraf)', 'Dabrafenib (Tafinlar)', 'Trametinib (Mekinist)', 'Encorafenib'],
    description: 'High-grade cutaneous melanoma driven by constitutively activating V600E/K mutations in the BRAF kinase activating the hyper-proliferative MAPK/ERK cascade.',
  },
  {
    id: 'ad',
    name: "Alzheimer's Disease (Neurodegeneration)",
    category: 'Neurodegenerative Disorders',
    icdCode: 'G30.9',
    primaryTargets: [
      { symbol: 'MAPT (Tau)', accession: 'P10636', role: 'Microtubule-associated protein hyperphosphorylation', pdbId: '6TJO' },
      { symbol: 'BACE1', accession: 'P56817', role: 'Beta-secretase 1 amyloidogenic cleavage', pdbId: '1W50' },
      { symbol: 'GSK3B', accession: 'P49841', role: 'Glycogen synthase kinase-3 beta tau kinase', pdbId: '1PYX' },
    ],
    pathways: ['Amyloid fiber formation', 'Alzheimer disease pathway', 'Neuronal death signaling'],
    hallmarks: ['Synaptic loss', 'Neurofibrillary tangle accumulation', 'Amyloid-beta oligomerization'],
    resistanceMutations: ['Abeta Arctic E22G mutation', 'Swedish APP KM670/671NL'],
    approvedDrugs: ['Donepezil (Aricept)', 'Memantine (Namenda)', 'Lecanemab (Leqembi)', 'Donanemab'],
    description: 'Progressive neurodegenerative disorder characterized by cortical atrophy, extracellular amyloid-beta plaque deposition, and intraneuronal hyperphosphorylated tau neurofibrillary tangles.',
  },
];

export default function DiseaseIntelligencePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDisease, setSelectedDisease] = useState<DiseaseEntry>(CURATED_DISEASES[0]);

  const filteredDiseases = CURATED_DISEASES.filter(
    (d) =>
      d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.primaryTargets.some((t) => t.symbol.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Swiss Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-2 border-black bg-white p-5 shadow-brutal">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 border border-black bg-swiss-yellow text-black font-mono text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#000]">
              01
            </span>
            <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
              MODULE 01: DISEASE INTELLIGENCE
            </span>
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-black">
            Target & Pathology Association
          </h1>
          <p className="text-xs font-mono text-swiss-muted">
            MAP CLINICAL INDICATIONS TO VALIDATED MOLECULAR TARGETS, RESISTANCE MUTATIONS, AND ONCOGENIC HALLMARKS.
          </p>
        </div>

        <ProvenanceBadge
          type="database"
          source="Curated Pathology Knowledge Base"
          version="ICD-11 / OMIM"
        />
      </div>

      {/* Disease Search & Explorer Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Search & Disease List */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 text-black absolute left-3 top-3 pointer-events-none" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="SEARCH DISEASES, TARGETS, ICD..."
              className="w-full pl-9 pr-3 py-2 border-2 border-black bg-white font-mono text-xs font-bold text-black focus:bg-swiss-panel outline-none shadow-brutal-sm"
            />
          </div>

          <div className="space-y-2">
            {filteredDiseases.map((disease) => {
              const isSelected = selectedDisease.id === disease.id;
              return (
                <div
                  key={disease.id}
                  onClick={() => setSelectedDisease(disease)}
                  className={`p-3.5 border-2 border-black cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-swiss-yellow text-black shadow-brutal font-bold'
                      : 'bg-white hover:bg-swiss-panel text-black shadow-brutal-sm hover:-translate-x-0.5 hover:-translate-y-0.5'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-mono font-black px-1.5 py-0.5 border border-black bg-white text-black">
                      {disease.icdCode}
                    </span>
                    <span className="text-[10px] font-mono font-bold text-swiss-muted">{disease.category}</span>
                  </div>
                  <h3 className="text-xs font-mono font-black uppercase mb-1">{disease.name}</h3>
                  <div className="flex items-center gap-1.5 text-[10px] font-mono">
                    <span className="text-swiss-muted">TARGETS:</span>
                    {disease.primaryTargets.map((t) => (
                      <span key={t.symbol} className="px-1 border border-black bg-swiss-panel font-black">
                        {t.symbol}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Columns: Selected Disease Detailed Profile */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 border-2 border-black bg-white shadow-brutal space-y-6">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b-2 border-black pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-xl font-black uppercase text-black">{selectedDisease.name}</h2>
                  <span className="font-mono text-xs font-black px-2 py-0.5 border border-black bg-swiss-yellow text-black">
                    {selectedDisease.icdCode}
                  </span>
                </div>
                <p className="font-mono text-xs font-bold text-swiss-muted">{selectedDisease.category}</p>
              </div>

              <div className="flex items-center gap-2">
                <Link
                  href={`/targets?query=${selectedDisease.primaryTargets[0]?.symbol || ''}`}
                  className="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black bg-swiss-yellow hover:bg-[#d4e400] text-black font-mono text-xs font-black uppercase transition-all shadow-[2px_2px_0px_#000]"
                >
                  <span>EXPLORE TARGET ({selectedDisease.primaryTargets[0]?.symbol})</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            <p className="font-mono text-xs leading-relaxed text-black bg-swiss-bg p-3 border border-black">
              {selectedDisease.description}
            </p>

            {/* Primary Molecular Targets */}
            <div className="space-y-3">
              <h3 className="font-mono text-xs font-black uppercase text-black flex items-center gap-2 border-b border-black pb-1">
                <Dna className="w-4 h-4 text-black" />
                VALIDATED MOLECULAR TARGETS & PDB RECEPTORS
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {selectedDisease.primaryTargets.map((target) => (
                  <div
                    key={target.symbol}
                    className="p-3.5 border-2 border-black bg-swiss-panel space-y-2 shadow-brutal-sm"
                  >
                    <div className="flex items-center justify-between border-b border-black pb-1">
                      <span className="font-mono font-black text-sm text-black">{target.symbol}</span>
                      <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 border border-black bg-white text-black">
                        UNIPROT: {target.accession}
                      </span>
                    </div>
                    <p className="font-mono text-[11px] text-black">{target.role}</p>
                    <div className="flex items-center justify-between pt-1 font-mono text-[11px] border-t border-black/30">
                      <span>PDB: <strong className="text-black font-black">{target.pdbId}</strong></span>
                      <Link
                        href={`/docking?target=${target.symbol}&pdbId=${target.pdbId}`}
                        className="px-2 py-0.5 border border-black bg-white hover:bg-swiss-yellow text-black font-bold uppercase flex items-center gap-1"
                      >
                        <span>DOCK TARGET</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Resistance Mutations */}
            <div className="space-y-2">
              <h3 className="font-mono text-xs font-black uppercase text-black flex items-center gap-2 border-b border-black pb-1">
                <ShieldAlert className="w-4 h-4 text-black" />
                CLINICAL RESISTANCE MUTATIONS
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedDisease.resistanceMutations.map((mut) => (
                  <span
                    key={mut}
                    className="px-2.5 py-1 border border-black bg-[#fee2e2] text-black font-mono text-xs font-bold shadow-[1px_1px_0px_#000]"
                  >
                    {mut}
                  </span>
                ))}
              </div>
            </div>

            {/* Pathways & Hallmarks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h3 className="font-mono text-xs font-black uppercase text-black flex items-center gap-2 border-b border-black pb-1">
                  <GitBranch className="w-4 h-4 text-black" />
                  DYSREGULATED REACTOME PATHWAYS
                </h3>
                <ul className="space-y-1.5 font-mono text-xs text-black">
                  {selectedDisease.pathways.map((pw) => (
                    <li key={pw} className="flex items-center gap-2 p-1.5 border border-black bg-white">
                      <span className="w-2 h-2 bg-black flex-shrink-0" />
                      <span>{pw}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <h3 className="font-mono text-xs font-black uppercase text-black flex items-center gap-2 border-b border-black pb-1">
                  <Layers className="w-4 h-4 text-black" />
                  HALLMARKS OF DISEASE
                </h3>
                <ul className="space-y-1.5 font-mono text-xs text-black">
                  {selectedDisease.hallmarks.map((hm) => (
                    <li key={hm} className="flex items-center gap-2 p-1.5 border border-black bg-white">
                      <span className="w-2 h-2 bg-swiss-yellow border border-black flex-shrink-0" />
                      <span>{hm}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Approved Benchmark Therapeutics */}
            <div className="space-y-2 pt-2 border-t-2 border-black">
              <h3 className="font-mono text-xs font-black uppercase text-black">
                APPROVED STANDARD-OF-CARE SMALL MOLECULES
              </h3>
              <div className="flex flex-wrap gap-2">
                {selectedDisease.approvedDrugs.map((drug) => (
                  <span
                    key={drug}
                    className="px-2.5 py-1 border border-black bg-swiss-panel text-black font-mono text-xs font-bold shadow-[1px_1px_0px_#000]"
                  >
                    {drug}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
