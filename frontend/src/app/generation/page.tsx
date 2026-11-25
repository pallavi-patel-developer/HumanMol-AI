'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  RotateCw,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';
import { scientificApi } from '@/lib/api';
import { GenerationResponse, GeneratedMolecule } from '@/lib/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';
import { MoleculeCard2D } from '@/components/visualization/MoleculeCard2D';

export default function MoleculeGenerationPage() {
  const [numMolecules, setNumMolecules] = useState(10);
  const [seed, setSeed] = useState(42);
  const [loading, setLoading] = useState(false);
  const [generationData, setGenerationData] = useState<GenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ro5Only, setRo5Only] = useState(false);
  const [selectedMolecule, setSelectedMolecule] = useState<GeneratedMolecule | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await scientificApi.generateMolecules(numMolecules, seed);
      setGenerationData(data);
      if (data.molecules.length > 0) {
        setSelectedMolecule(data.molecules[0]);
      }
    } catch (err: any) {
      console.error('Generation failed:', err);
      setError(err.message || 'Molecule generation failed. Verify REINVENT4 service is active.');
    } finally {
      setLoading(false);
    }
  };

  const displayedMolecules = generationData?.molecules.filter(
    (m) => !ro5Only || m.lipinski_ro5
  ) || [];

  return (
    <div className="space-y-6">
      {/* Swiss Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-2 border-black bg-white p-5 shadow-brutal">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 border border-black bg-swiss-yellow text-black font-mono text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#000]">
              03
            </span>
            <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
              MODULE 03: MOLECULE GENERATION & OPTIMIZATION
            </span>
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-black">
            REINVENT4 Prior-Based De Novo Sampling
          </h1>
          <p className="text-xs font-mono text-swiss-muted">
            UNCONDITIONED CHEMICAL SAMPLING FROM PRETRAINED CHEMBL RNN PRIOR. NOT TARGET-CONDITIONED OR REWARD-OPTIMIZED FOR EGFR L858R.
          </p>
        </div>

        <ProvenanceBadge
          type="computational"
          source="REINVENT4 Prior Model"
          version="v4.9.34 (ChEMBL RNN Prior)"
        />
      </div>

      {/* Scientific Workflow Integrity Banner */}
      <div className="p-3 border-2 border-black bg-swiss-panel font-mono text-xs text-black shadow-brutal-sm space-y-1">
        <div className="flex items-center gap-2 font-black uppercase text-[11px] border-b border-black pb-1">
          <span className="w-2 h-2 bg-black inline-block"></span>
          <span>WORKFLOW CLASSIFICATION: PRIOR-BASED DE NOVO SAMPLING (UNCONDITIONED)</span>
        </div>
        <p className="text-[11px] leading-tight text-swiss-muted">
          This generation workflow performs probabilistic sampling across general drug-like chemical space from the ChEMBL/PubChem prior distribution. It is <strong>NOT</strong> target-conditioned and does <strong>NOT</strong> apply reward-based reinforcement learning optimization for EGFR L858R. Target specificity must be evaluated through downstream AutoDock Vina docking and bioactivity scoring.
        </p>
      </div>

      {/* Generation Control Panel */}
      <div className="p-6 border-2 border-black bg-white shadow-brutal space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block font-mono text-[11px] font-black uppercase text-black mb-1">
              MOLECULES TO SAMPLE (N)
            </label>
            <input
              type="number"
              min={1}
              max={50}
              value={numMolecules}
              onChange={(e) => setNumMolecules(parseInt(e.target.value) || 10)}
              className="w-full px-3 py-2 border-2 border-black bg-white font-mono text-xs font-bold text-black focus:bg-swiss-bg outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-[11px] font-black uppercase text-black mb-1">
              RANDOM SEED (EXACT REPRODUCIBILITY)
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value) || 42)}
              className="w-full px-3 py-2 border-2 border-black bg-white font-mono text-xs font-bold text-black focus:bg-swiss-bg outline-none"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-5 py-2.5 border-2 border-black bg-swiss-yellow hover:bg-[#d4e400] text-black font-mono text-xs font-black uppercase shadow-brutal-sm cursor-pointer disabled:opacity-50 transition-all"
            >
              {loading ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin text-black" />
                  <span>SAMPLING PRIOR...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-black" />
                  <span>SAMPLE DE NOVO MOLECULES</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between pt-3 border-t-2 border-black font-mono text-xs text-black gap-2">
          <span>CHECKPOINT: <strong className="bg-swiss-panel px-1.5 py-0.5 border border-black">reinvent.prior</strong></span>
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={ro5Only}
              onChange={(e) => setRo5Only(e.target.checked)}
              className="w-4 h-4 border-2 border-black accent-black rounded-none"
            />
            <span className="font-bold">FILTER TO LIPINSKI RO5 COMPLIANT ONLY</span>
          </label>
        </div>
      </div>

      {error && (
        <div className="p-4 border-2 border-black bg-[#fee2e2] text-black font-mono text-xs flex items-center gap-2 shadow-brutal-sm">
          <ShieldAlert className="w-5 h-5 flex-shrink-0 text-black" />
          <div>
            <span className="font-black uppercase block">GENERATION ENGINE EXCEPTION:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Generation Results */}
      {generationData && (
        <div className="space-y-6">
          {/* Metrics summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm font-mono">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">TOTAL SAMPLED</span>
              <span className="text-2xl font-black text-black">{generationData.total_generated}</span>
            </div>
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm font-mono">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">VALIDITY RATE</span>
              <span className="text-2xl font-black text-black">
                {((generationData.valid_count / generationData.total_generated) * 100).toFixed(0)}%
                <span className="text-xs text-swiss-muted ml-1">({generationData.valid_count}/{generationData.total_generated})</span>
              </span>
            </div>
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm font-mono">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">SAMPLING RUNTIME</span>
              <span className="text-2xl font-black text-black">
                {generationData.execution_time_seconds?.toFixed(3)}s
              </span>
            </div>
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm font-mono">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">RO5 COMPLIANT</span>
              <span className="text-2xl font-black text-black">
                {generationData.molecules.filter((m) => m.lipinski_ro5).length} / {generationData.total_generated}
              </span>
            </div>
          </div>

          {/* Molecule Inspection Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Table / List */}
            <div className="lg:col-span-2 overflow-x-auto border-2 border-black bg-white shadow-brutal-sm">
              <table className="science-table w-full">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>SMILES STRUCTURE</th>
                    <th>FORMULA</th>
                    <th>MW</th>
                    <th>LOGP</th>
                    <th>PRIOR NLL (LIKELIHOOD)*</th>
                    <th>RO5</th>
                  </tr>
                </thead>
                <tbody>
                  {displayedMolecules.map((mol, idx) => (
                    <tr
                      key={idx}
                      onClick={() => setSelectedMolecule(mol)}
                      className={`cursor-pointer transition-colors ${
                        selectedMolecule?.smiles === mol.smiles ? '!bg-swiss-yellow font-bold' : ''
                      }`}
                    >
                      <td className="font-mono text-xs font-bold text-swiss-muted">#{idx + 1}</td>
                      <td>
                        <div className="font-mono text-xs text-black max-w-[220px] truncate" title={mol.smiles}>
                          {mol.smiles}
                        </div>
                      </td>
                      <td className="font-mono text-xs text-black">{mol.formula || '—'}</td>
                      <td className="font-mono text-xs text-black">{mol.molecular_weight?.toFixed(1) || '—'}</td>
                      <td className="font-mono text-xs text-black">{mol.logp?.toFixed(2) || '—'}</td>
                      <td className="font-mono text-xs text-black">{mol.nll?.toFixed(2) || '—'}</td>
                      <td>
                        <span
                          className={`text-[9px] px-1.5 py-0.5 border border-black font-mono font-black uppercase ${
                            mol.lipinski_ro5
                              ? 'bg-[#a3e635] text-black'
                              : 'bg-[#f87171] text-black'
                          }`}
                        >
                          {mol.lipinski_ro5 ? 'PASS' : 'VIOLATION'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="p-2 border-t border-black bg-swiss-panel font-mono text-[10px] text-swiss-muted">
                * <strong>Prior NLL:</strong> Negative Log-Likelihood measures generative sequence likelihood under the ChEMBL RNN prior model. Lower NLL indicates common chemical syntax; it does NOT imply EGFR binding affinity, biological potency, or drug quality.
              </div>
            </div>

            {/* Selected Molecule Preview Card */}
            <div>
              {selectedMolecule ? (
                <div className="space-y-4">
                  <MoleculeCard2D
                    smiles={selectedMolecule.smiles}
                    name={`SAMPLED // ${selectedMolecule.formula || 'NOVEL'}`}
                    formula={selectedMolecule.formula}
                    molecularWeight={selectedMolecule.molecular_weight}
                    logp={selectedMolecule.logp}
                    tpsa={selectedMolecule.tpsa}
                    lipinskiRo5={selectedMolecule.lipinski_ro5}
                    highlighted={true}
                  />

                  {/* Forward actions */}
                  <div className="p-4 border-2 border-black bg-swiss-panel space-y-2 shadow-brutal-sm font-mono">
                    <h4 className="text-xs font-black uppercase text-black border-b border-black pb-1 mb-2">
                      DOWNSTREAM SCREENING WORKFLOWS
                    </h4>
                    <Link
                      href={`/properties?smiles=${encodeURIComponent(selectedMolecule.smiles)}`}
                      className="w-full flex items-center justify-between p-2 border border-black bg-white hover:bg-swiss-yellow text-xs font-bold text-black transition-colors"
                    >
                      <span>PREDICT PROPERTIES (CHEMPROP)</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                    <Link
                      href={`/docking?target=2ITZ&smiles=${encodeURIComponent(selectedMolecule.smiles)}`}
                      className="w-full flex items-center justify-between p-2 border border-black bg-white hover:bg-swiss-yellow text-xs font-bold text-black transition-colors"
                    >
                      <span>SIMULATE 3D DOCKING (VINA - 2ITZ)</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                    <Link
                      href={`/admet?smiles=${encodeURIComponent(selectedMolecule.smiles)}`}
                      className="w-full flex items-center justify-between p-2 border border-black bg-white hover:bg-swiss-yellow text-xs font-bold text-black transition-colors"
                    >
                      <span>PROFILE ADMET (ADMETLAB 3.0)</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="p-6 border-2 border-black bg-white text-center font-mono text-xs text-swiss-muted shadow-brutal-sm">
                  SELECT A GENERATED MOLECULE FROM THE TABLE TO INSPECT DETAILS.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
