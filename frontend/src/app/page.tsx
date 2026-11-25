'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Play,
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Cpu,
  Database,
  Layers,
  Maximize2,
  ExternalLink,
} from 'lucide-react';
import { scientificApi } from '@/lib/api';
import { PipelineRunResponse, CandidateEvaluationResult } from '@/lib/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';
import { MoleculeCard2D } from '@/components/visualization/MoleculeCard2D';

export default function Dashboard() {
  const [targetName, setTargetName] = useState('EGFR L858R');
  const [numCandidates, setNumCandidates] = useState(5);
  const [seed, setSeed] = useState(42);
  const [runProperties, setRunProperties] = useState(true);
  const [runDocking, setRunDocking] = useState(true);
  const [runAdmet, setRunAdmet] = useState(true);

  const [loading, setLoading] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<PipelineRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateEvaluationResult | null>(null);

  const handleLaunchPipeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const isEgfr = targetName.toUpperCase().includes('EGFR') || targetName.toUpperCase().includes('2ITZ') || targetName.toUpperCase().includes('L858R');
      const result = await scientificApi.runPipeline({
        target_name: isEgfr ? 'EGFR L858R Kinase Domain (2ITZ)' : 'c-Abl Kinase Domain (1IEP)',
        target_protein: isEgfr ? 'EGFR' : 'c-Abl',
        disease: isEgfr ? 'NSCLC' : 'CML',
        mutation: isEgfr ? 'L858R' : 'Wild-Type',
        target_pdb_id: isEgfr ? '2ITZ' : '1IEP',
        num_candidates: numCandidates,
        seed,
        run_properties: runProperties,
        run_docking: runDocking,
        run_admet: runAdmet,
      });
      setPipelineResult(result);
      if (result.candidates.length > 0) {
        setSelectedCandidate(result.candidates[0]);
      }
    } catch (err: any) {
      console.error('Pipeline failed:', err);
      setError(err.message || 'Pipeline execution failed. Ensure FastAPI engine is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Modern SaaS Hero Banner */}
      <section className="rounded-2xl border border-slate-200/80 bg-white shadow-sm p-6 md:p-8 relative">
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
          <div className="space-y-4 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-blue-50 text-blue-700 border border-blue-200/60 px-3 py-0.5 text-xs font-semibold">
                NOVA-1 // DISCOVERY RUNNER
              </span>
              <span className="rounded-full bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-0.5 text-xs font-medium">
                SPEC: DE NOVO TRANSLATIONAL BIOINFORMATICS
              </span>
              <span className="text-xs text-slate-400 font-medium">
                ACCESS NODE: ORBITRA 5 // 0.243
              </span>
            </div>

            <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 leading-tight">
              HumanMol AI Discovery Platform
            </h1>

            <p className="text-sm font-normal leading-relaxed text-slate-600 max-w-2xl">
              Unified translational bioinformatics architecture orchestrating de novo molecular sampling (REINVENT4), neural graph regression (Chemprop D-MPNN), structural protein-ligand docking (AutoDock Vina), multi-endpoint pharmacokinetics (ADMETlab 3.0), and biological evidence mapping.
            </p>

            {/* Micro-Spec Engine Chips */}
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] font-semibold text-slate-700">
                <Cpu className="w-3.5 h-3.5 text-blue-600" />
                <span>REINVENT4 PRIOR</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] font-semibold text-slate-700">
                <Cpu className="w-3.5 h-3.5 text-blue-600" />
                <span>CHEMPROP D-MPNN</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] font-semibold text-slate-700">
                <Maximize2 className="w-3.5 h-3.5 text-blue-600" />
                <span>AUTODOCK VINA 3D</span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] font-semibold text-slate-700">
                <Database className="w-3.5 h-3.5 text-blue-600" />
                <span>ADMETLAB 3.0 (119 ENDPOINTS)</span>
              </div>
            </div>
          </div>

          {/* Right Boxed Indicator */}
          <div className="hidden lg:flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-50 border border-slate-200/80 self-start min-w-[140px] text-center">
            <span className="text-[11px] font-semibold uppercase text-slate-400 tracking-wider block mb-1">
              ENGINE TIER
            </span>
            <span className="text-3xl font-bold text-slate-900 tracking-tight">
              [74]
            </span>
            <span className="border-t border-slate-200 w-full my-2.5" />
            <span className="text-[10px] font-bold text-emerald-600 uppercase flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              STATUS: NOMINAL
            </span>
          </div>
        </div>
      </section>

      {/* Unified Pipeline Execution Workspace */}
      <section className="rounded-2xl border border-slate-200/80 bg-white shadow-sm p-6 md:p-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-7 h-7 rounded-lg bg-blue-50 border border-blue-200/60 text-blue-600 font-bold text-xs flex items-center justify-center">
                01
              </span>
              <h2 className="text-xl font-bold tracking-tight text-slate-900">
                Unified Candidate Discovery Pipeline
              </h2>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              AUTOMATED BATCH EXECUTION: DE NOVO SAMPLING → CHEMPROP SCREEN → AUTODOCK VINA → ADMET PROFILING
            </p>
          </div>

          <button
            onClick={handleLaunchPipeline}
            disabled={loading}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs uppercase shadow-sm transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin text-white" />
                <span>EXECUTING PIPELINE...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white text-white" />
                <span>LAUNCH DISCOVERY PIPELINE</span>
              </>
            )}
          </button>
        </div>

        {/* Pipeline Controls Form */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-slate-50 p-5 rounded-2xl border border-slate-200/70">
          <div>
            <label className="block text-[11px] font-semibold uppercase text-slate-700 mb-1.5">
              BIOLOGICAL TARGET
            </label>
            <input
              type="text"
              value={targetName}
              onChange={(e) => setTargetName(e.target.value)}
              placeholder="e.g. EGFR L858R, c-Abl"
              className="w-full px-3 py-2 border border-slate-200 bg-white rounded-xl text-xs font-medium text-slate-800 outline-none"
            />
            <div className="flex gap-1.5 mt-2">
              <button
                type="button"
                onClick={() => setTargetName('EGFR L858R')}
                className={`text-[10px] px-2.5 py-1 rounded-lg border font-semibold cursor-pointer transition-colors ${
                  targetName.toUpperCase().includes('EGFR') ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                EGFR (2ITZ)
              </button>
              <button
                type="button"
                onClick={() => setTargetName('c-Abl')}
                className={`text-[10px] px-2.5 py-1 rounded-lg border font-semibold cursor-pointer transition-colors ${
                  targetName.toUpperCase().includes('ABL') ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                c-Abl (1IEP)
              </button>
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold uppercase text-slate-700 mb-1.5">
              CANDIDATES TO GENERATE
            </label>
            <input
              type="number"
              min={1}
              max={20}
              value={numCandidates}
              onChange={(e) => setNumCandidates(parseInt(e.target.value) || 5)}
              className="w-full px-3 py-2 border border-slate-200 bg-white rounded-xl text-xs font-medium text-slate-800 outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold uppercase text-slate-700 mb-1.5">
              REPRODUCIBILITY SEED
            </label>
            <input
              type="number"
              value={seed}
              onChange={(e) => setSeed(parseInt(e.target.value) || 42)}
              className="w-full px-3 py-2 border border-slate-200 bg-white rounded-xl text-xs font-medium text-slate-800 outline-none"
            />
          </div>

          <div className="flex flex-col justify-end gap-2 text-xs font-medium text-slate-700">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={runProperties}
                onChange={(e) => setRunProperties(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span>CHEMPROP D-MPNN SCREEN</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={runDocking}
                onChange={(e) => setRunDocking(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span>AUTODOCK VINA 3D DOCKING</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={runAdmet}
                onChange={(e) => setRunAdmet(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <span>ADMETLAB 3.0 PROFILING</span>
            </label>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-600" />
            <div>
              <span className="font-bold uppercase block">FAULT DETECTED:</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Pipeline Output Data */}
        {pipelineResult && (
          <div className="space-y-6 pt-4 border-t border-slate-100">
            <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-4 rounded-xl border border-slate-200/70">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                <div>
                  <h3 className="text-xs font-bold uppercase text-slate-900">
                    PIPELINE BATCH COMPLETE // TARGET: {pipelineResult.target_name}
                  </h3>
                  <span className="text-[11px] text-slate-500 font-medium block mt-0.5">
                    RUN_ID: {pipelineResult.run_id} • DURATION: {pipelineResult.execution_time_seconds?.toFixed(2)}s • TOTAL: {pipelineResult.total_generated} • VALID: {pipelineResult.valid_count}
                  </span>
                </div>
              </div>

              <ProvenanceBadge
                type="computational"
                source="Multi-Engine Pipeline"
                version="v1.0"
              />
            </div>

            {/* Results Table */}
            <div className="overflow-x-auto rounded-2xl border border-slate-200/80 bg-white shadow-sm">
              <table className="science-table w-full">
                <thead>
                  <tr>
                    <th>RANK</th>
                    <th>STRUCTURE / SMILES</th>
                    <th>FORMULA & MW</th>
                    <th>LOGP</th>
                    <th>RO5</th>
                    <th>CHEMPROP PROPERTY</th>
                    <th>VINA AFFINITY</th>
                    <th>ADMET (HERG / DILI)</th>
                    <th>MPO SCORE</th>
                  </tr>
                </thead>
                <tbody>
                  {pipelineResult.candidates.map((cand) => (
                    <tr
                      key={cand.rank}
                      onClick={() => setSelectedCandidate(cand)}
                      className={`cursor-pointer transition-colors ${
                        selectedCandidate?.rank === cand.rank ? '!bg-blue-50/70 font-semibold' : ''
                      }`}
                    >
                      <td className="font-bold text-slate-900">#{cand.rank}</td>
                      <td>
                        <div className="font-mono text-xs text-slate-800 max-w-[200px] truncate" title={cand.smiles}>
                          {cand.smiles}
                        </div>
                      </td>
                      <td className="text-xs text-slate-800">
                        {cand.formula || '—'} <span className="text-slate-400">({cand.molecular_weight?.toFixed(1) || '—'})</span>
                      </td>
                      <td className="text-xs text-slate-800">
                        {cand.logp != null ? cand.logp.toFixed(2) : '—'}
                      </td>
                      <td>
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                            cand.lipinski_ro5
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : 'bg-rose-50 text-rose-700 border border-rose-200'
                          }`}
                        >
                          {cand.lipinski_ro5 ? 'PASS' : 'VIOLATION'}
                        </span>
                      </td>
                      <td className="text-slate-900 font-semibold text-xs">
                        {cand.chemprop_status === 'NOT_RUN' ? (
                          <span className="text-[11px] text-slate-400">NOT RUN</span>
                        ) : cand.chemprop_status === 'FAILED' ? (
                          <span className="text-[10px] text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full font-semibold border border-rose-200" title={cand.chemprop_error || 'Prediction failed'}>FAILED</span>
                        ) : cand.chemprop_predicted_property != null ? (
                          cand.chemprop_predicted_property.toFixed(4)
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="text-xs font-bold text-slate-900">
                        {cand.docking_status === 'NOT_RUN' ? (
                          <span className="text-[11px] text-slate-400">NOT RUN</span>
                        ) : cand.docking_status === 'FAILED' ? (
                          <span className="text-[10px] text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full font-semibold border border-rose-200" title={cand.docking_error || 'Docking failed'}>FAILED</span>
                        ) : cand.docking_best_affinity != null ? (
                          `${cand.docking_best_affinity.toFixed(1)} kcal/mol`
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="text-xs text-slate-800">
                        {cand.admet_status === 'NOT_RUN' ? (
                          <span className="text-[11px] text-slate-400">NOT RUN</span>
                        ) : cand.admet_status === 'FAILED' ? (
                          <span className="text-[10px] text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full font-semibold border border-rose-200" title={cand.admet_error || 'Profiling failed'}>FAILED</span>
                        ) : (cand.admet_herg != null || cand.admet_dili != null) ? (
                          `HERG: ${cand.admet_herg != null ? cand.admet_herg.toFixed(2) : '—'} | DILI: ${cand.admet_dili != null ? cand.admet_dili.toFixed(2) : '—'}`
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="font-bold text-xs text-blue-600 bg-blue-50/30">
                        {cand.composite_rank_score.toFixed(3)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Selected Candidate Detailed Inspection */}
            {selectedCandidate && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <MoleculeCard2D
                  smiles={selectedCandidate.smiles}
                  name={`LEAD CANDIDATE #${selectedCandidate.rank} (${targetName})`}
                  formula={selectedCandidate.formula}
                  molecularWeight={selectedCandidate.molecular_weight}
                  logp={selectedCandidate.logp}
                  lipinskiRo5={selectedCandidate.lipinski_ro5}
                  rank={selectedCandidate.rank}
                  score={selectedCandidate.composite_rank_score}
                  highlighted={true}
                />

                <div className="p-6 rounded-2xl border border-slate-200/80 bg-slate-50/70 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-200/70 pb-3">
                    <span className="text-xs font-bold uppercase text-slate-800">
                      COMPUTATIONAL EVALUATION DOSSIER
                    </span>
                    <span className="bg-blue-50 text-blue-700 border border-blue-200/60 px-2.5 py-0.5 rounded-full text-xs font-bold">
                      RANK #{selectedCandidate.rank}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-xl border border-slate-200 bg-white">
                      <span className="text-[10px] text-slate-400 uppercase block font-semibold">PREDICTED VINA DOCKING SCORE</span>
                      <span className="font-bold text-slate-900 text-sm mt-0.5 block">
                        {selectedCandidate.docking_status === 'NOT_RUN'
                          ? 'NOT RUN'
                          : selectedCandidate.docking_status === 'FAILED'
                          ? 'FAILED'
                          : selectedCandidate.docking_best_affinity != null
                          ? `${selectedCandidate.docking_best_affinity.toFixed(1)} kcal/mol`
                          : 'N/A'}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl border border-slate-200 bg-white">
                      <span className="text-[10px] text-slate-400 uppercase block font-semibold">CHEMPROP D-MPNN</span>
                      <span className="font-bold text-slate-900 text-sm mt-0.5 block">
                        {selectedCandidate.chemprop_status === 'NOT_RUN'
                          ? 'NOT RUN'
                          : selectedCandidate.chemprop_status === 'FAILED'
                          ? 'FAILED'
                          : selectedCandidate.chemprop_predicted_property != null
                          ? selectedCandidate.chemprop_predicted_property.toFixed(4)
                          : 'N/A'}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl border border-slate-200 bg-white">
                      <span className="text-[10px] text-slate-400 uppercase block font-semibold">CACO-2 PERMEABILITY</span>
                      <span className="font-bold text-slate-900 text-xs mt-0.5 block">
                        {selectedCandidate.admet_status === 'NOT_RUN'
                          ? 'NOT RUN'
                          : selectedCandidate.admet_status === 'FAILED'
                          ? 'FAILED'
                          : selectedCandidate.admet_caco2 != null
                          ? `${Number(selectedCandidate.admet_caco2).toFixed(2)} log10(cm/s)`
                          : 'Local/Pending'}
                      </span>
                    </div>
                    <div className="p-3 rounded-xl border border-slate-200 bg-white">
                      <span className="text-[10px] text-slate-400 uppercase block font-semibold">COMPOSITE MPO SCORE</span>
                      <span className="font-bold text-slate-900 text-sm mt-0.5 block">
                        {selectedCandidate.composite_rank_score.toFixed(4)}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center justify-between pt-3 border-t border-slate-200/70 gap-2">
                    <Link
                      href={`/docking?target=${targetName}&smiles=${encodeURIComponent(selectedCandidate.smiles)}`}
                      className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-100 text-slate-800 text-xs font-semibold uppercase transition-all shadow-xs flex items-center gap-1.5"
                    >
                      <span>INSPECT 3D BINDING POSES</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                    </Link>
                    <Link
                      href={`/candidates`}
                      className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-100 text-slate-800 text-xs font-semibold uppercase transition-all shadow-xs flex items-center gap-1.5"
                    >
                      <span>CANDIDATE COMPARISON</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                    </Link>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {/* 10 Specialized Scientific Workspaces Directory */}
      <section className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-lg bg-blue-50 border border-blue-200/60 text-blue-600 text-xs font-bold flex items-center justify-center">
              M
            </span>
            <h2 className="text-xl font-bold tracking-tight text-slate-900">
              Specialized Scientific Workspaces
            </h2>
          </div>
          <span className="rounded-full bg-slate-100 border border-slate-200 px-3 py-0.5 text-xs font-semibold text-slate-700">
            10 CONNECTED ENGINES
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Module 01 */}
          <Link
            href="/disease-intelligence"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 01
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Disease Intelligence
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                Etiology exploration, target associations, resistance mutations, and phenotypic indication mapping.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>DB: OMIM / DisGeNET</span>
              <span>[DISEASE-BIO]</span>
            </div>
          </Link>

          {/* Module 02 */}
          <Link
            href="/targets"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 02
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Biological Target Explorer
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                UniProt KB entries, ChEMBL bioactivities, Reactome pathways, and AlphaFold / RCSB crystal structures.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>UNIPROT + CHEMBL</span>
              <span>[TARGET-EXP]</span>
            </div>
          </Link>

          {/* Module 03 */}
          <Link
            href="/generation"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 03
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Molecule Generation
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                REINVENT4 de novo sampling with official ChEMBL prior, NLL log-likelihood scoring, and Lipinski filtering.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>REINVENT4 // PYTORCH</span>
              <span>[DE NOVO]</span>
            </div>
          </Link>

          {/* Module 04 */}
          <Link
            href="/properties"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 04
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Molecular Properties
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                Chemprop Directed Message Passing Neural Network (D-MPNN) molecular property estimation and featurization.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>CHEMPROP D-MPNN</span>
              <span>[PROPERTY-AI]</span>
            </div>
          </Link>

          {/* Module 05 */}
          <Link
            href="/docking"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 05
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Molecular Docking
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                AutoDock Vina simulation, binding affinity in kcal/mol, binding modes, RMSD, and 3D pose visualization.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>AUTODOCK VINA 1.2</span>
              <span>[3D-DOCK]</span>
            </div>
          </Link>

          {/* Module 06 */}
          <Link
            href="/admet"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 06
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                ADMET & Toxicity
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                ADMETlab 3.0 profiling across 119 endpoints (Absorption, Distribution, Metabolism, Excretion, Toxicity).
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>ADMETLAB 3.0 // 119 EP</span>
              <span>[PK-TOX]</span>
            </div>
          </Link>

          {/* Module 07 */}
          <Link
            href="/cellular-response"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 07
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Cellular Response
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                XPert Dual-Branch Transformer architecture, transcriptomic perturbation tracking, and GPU readiness.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>XPERT ARCHITECTURE</span>
              <span>[CELL-PERT]</span>
            </div>
          </Link>

          {/* Module 08 */}
          <Link
            href="/research-evidence"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 08
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Research Evidence
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                PubMed peer-reviewed literature mining + arXiv computational preprints with direct PDF access.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>PUBMED + ARXIV</span>
              <span>[LIT-EVID]</span>
            </div>
          </Link>

          {/* Module 09 */}
          <Link
            href="/candidates"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 09
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Candidate Comparison
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                Multi-parameter optimization leaderboard, pairwise molecule comparison, and uncertainty metrics.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>MPO LEADERBOARD</span>
              <span>[CAND-EVAL]</span>
            </div>
          </Link>

          {/* Module 10 */}
          <Link
            href="/reports"
            className="p-5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md transition-all group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-2.5">
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg border border-blue-100">
                  MODULE 10
                </span>
                <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="text-sm font-bold text-slate-900 mb-1">
                Research Dossier Reports
              </h3>
              <p className="text-xs text-slate-500 font-normal leading-relaxed">
                Export comprehensive research dossiers to PDF, Markdown, and JSON with complete model provenance.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between text-[11px] text-slate-500 font-medium">
              <span>EXPORT ENGINE</span>
              <span>[DOSSIER]</span>
            </div>
          </Link>
        </div>
      </section>
    </div>
  );
}
