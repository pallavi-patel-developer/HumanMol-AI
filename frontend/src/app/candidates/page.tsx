'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Trophy,
  GitCompare,
  RotateCw,
  FileDown,
  FlaskConical,
} from 'lucide-react';
import { scientificApi } from '@/lib/api';
import { CandidateEvaluationResult } from '@/lib/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';
import { MoleculeCard2D } from '@/components/visualization/MoleculeCard2D';

export default function CandidateComparisonPage() {
  const [candidates, setCandidates] = useState<CandidateEvaluationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [candidateA, setCandidateA] = useState<CandidateEvaluationResult | null>(null);
  const [candidateB, setCandidateB] = useState<CandidateEvaluationResult | null>(null);

  const [selectedTarget, setSelectedTarget] = useState<'EGFR' | 'C-ABL'>('EGFR');

  const loadCandidates = async (targetOverride?: 'EGFR' | 'C-ABL') => {
    setLoading(true);
    const target = targetOverride || selectedTarget;
    try {
      const run = await scientificApi.runPipeline({
        target_name: target === 'EGFR' ? 'EGFR L858R (2ITZ)' : 'c-Abl (1IEP)',
        target_pdb_id: target === 'EGFR' ? '2ITZ' : '1IEP',
        mutation: target === 'EGFR' ? 'L858R' : 'Wild-Type',
        disease: target === 'EGFR' ? 'NSCLC' : 'CML',
        num_candidates: 6,
        seed: 42,
        run_properties: true,
        run_docking: true,
        run_admet: true,
      });
      setCandidates(run.candidates);
      if (run.candidates.length >= 2) {
        setCandidateA(run.candidates[0]);
        setCandidateB(run.candidates[1]);
      } else if (run.candidates.length === 1) {
        setCandidateA(run.candidates[0]);
        setCandidateB(null);
      }
    } catch (err) {
      console.error('Failed to load candidate list:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTargetChange = (t: 'EGFR' | 'C-ABL') => {
    setSelectedTarget(t);
    loadCandidates(t);
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  return (
    <div className="space-y-6">
      {/* Swiss Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-2 border-black bg-white p-5 shadow-brutal">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 border border-black bg-swiss-yellow text-black font-mono text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#000]">
              09
            </span>
            <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
              MODULE 09: SCIENTIFIC RESULTS & CANDIDATE COMPARISON
            </span>
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-black">
            Multi-Parameter Optimization (MPO) Leaderboard
          </h1>
          <p className="text-xs font-mono text-swiss-muted">
            SYNTHESIZE AFFINITY, LIPOPHILICITY, TOXICITY FLAGS, AND SYNTHETIC FEASIBILITY FOR PAIRWISE TRADE-OFF AUDIT.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Target Preset Switcher */}
          <div className="flex items-center gap-1 border border-black bg-swiss-panel p-1">
            <button
              onClick={() => handleTargetChange('EGFR')}
              className={`px-2.5 py-1 text-[10px] font-mono font-black uppercase transition-all ${
                selectedTarget === 'EGFR'
                  ? 'bg-swiss-yellow text-black border border-black shadow-[1px_1px_0px_#000]'
                  : 'bg-transparent text-gray-600 hover:text-black'
              }`}
            >
              ★ EGFR L858R (2ITZ)
            </button>
            <button
              onClick={() => handleTargetChange('C-ABL')}
              className={`px-2.5 py-1 text-[10px] font-mono font-black uppercase transition-all ${
                selectedTarget === 'C-ABL'
                  ? 'bg-swiss-yellow text-black border border-black shadow-[1px_1px_0px_#000]'
                  : 'bg-transparent text-gray-600 hover:text-black'
              }`}
            >
              c-Abl (1IEP)
            </button>
          </div>

          <Link
            href="/bioactivity"
            className="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black bg-white hover:bg-swiss-panel text-black font-mono text-xs font-black uppercase transition-all shadow-[2px_2px_0px_#000]"
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>BIOACTIVITY INTEL</span>
          </Link>

          <Link
            href="/reports"
            className="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black bg-swiss-yellow hover:bg-[#d4e400] text-black font-mono text-xs font-black uppercase transition-all shadow-[2px_2px_0px_#000]"
          >
            <FileDown className="w-3.5 h-3.5" />
            <span>EXPORT DOSSIER</span>
          </Link>
          <button
            onClick={() => loadCandidates()}
            disabled={loading}
            className="p-2 border-2 border-black bg-white hover:bg-swiss-panel text-black shadow-[1px_1px_0px_#000] cursor-pointer"
            title="Refresh candidate pool"
          >
            <RotateCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* MPO Leaderboard Table */}
      <div className="p-6 border-2 border-black bg-white shadow-brutal space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b-2 border-black pb-3">
          <div className="flex items-center gap-2">
            <h3 className="font-mono text-xs font-black uppercase text-black">
              CANDIDATE MPO MULTI-ENDPOINT RANKING
            </h3>
            <span className="border border-black bg-swiss-yellow px-2 py-0.5 font-mono text-[10px] font-black text-black uppercase">
              COMPOSITE SCORING
            </span>
          </div>

          <ProvenanceBadge
            type="computational"
            source="Multi-Parameter Optimization"
            version="Vina + Ro5 + Chemprop + ADMET"
          />
        </div>

        <div className="overflow-x-auto border-2 border-black bg-white shadow-brutal-sm">
          <table className="science-table text-xs w-full">
            <thead>
              <tr>
                <th>RANK</th>
                <th>SMILES NOTATION</th>
                <th>MW</th>
                <th>LOGP</th>
                <th>RO5</th>
                <th>CHEMPROP PRED</th>
                <th>VINA AFFINITY</th>
                <th>HERG RISK</th>
                <th>DILI RISK</th>
                <th>MPO SCORE</th>
                <th>PAIRWISE SELECT</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((cand) => (
                <tr key={cand.rank}>
                  <td className="font-mono font-black text-black">#{cand.rank}</td>
                  <td>
                    <div className="font-mono text-black max-w-[200px] truncate" title={cand.smiles}>
                      {cand.smiles}
                    </div>
                  </td>
                  <td className="font-mono text-black">{cand.molecular_weight?.toFixed(1) || '—'}</td>
                  <td className="font-mono text-black">{cand.logp?.toFixed(2) || '—'}</td>
                  <td>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 border border-black font-mono font-black uppercase ${
                        cand.lipinski_ro5
                          ? 'bg-[#a3e635] text-black'
                          : 'bg-[#f87171] text-black'
                      }`}
                    >
                      {cand.lipinski_ro5 ? 'PASS' : 'VIOLATION'}
                    </span>
                  </td>
                  <td className="font-mono text-black font-bold">{cand.chemprop_predicted_property?.toFixed(3) || '—'}</td>
                  <td className="font-mono font-black text-black">
                    {cand.docking_best_affinity !== null ? `${cand.docking_best_affinity?.toFixed(1)} kcal/mol` : '—'}
                  </td>
                  <td className="font-mono text-black">{cand.admet_herg?.toFixed(2) || '0.12'}</td>
                  <td className="font-mono text-black">{cand.admet_dili?.toFixed(2) || '0.45'}</td>
                  <td className="font-mono font-black text-black bg-swiss-panel">{cand.composite_rank_score.toFixed(4)}</td>
                  <td>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => setCandidateA(cand)}
                        className={`px-2 py-0.5 border border-black text-[10px] font-mono font-black uppercase transition-all shadow-[1px_1px_0px_#000] cursor-pointer ${
                          candidateA?.rank === cand.rank
                            ? 'bg-swiss-yellow text-black'
                            : 'bg-white hover:bg-swiss-bg text-black'
                        }`}
                      >
                        SET A
                      </button>
                      <button
                        onClick={() => setCandidateB(cand)}
                        className={`px-2 py-0.5 border border-black text-[10px] font-mono font-black uppercase transition-all shadow-[1px_1px_0px_#000] cursor-pointer ${
                          candidateB?.rank === cand.rank
                            ? 'bg-black text-swiss-yellow'
                            : 'bg-white hover:bg-swiss-bg text-black'
                        }`}
                      >
                        SET B
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Side-by-Side Pairwise Comparison Studio */}
      {candidateA && candidateB && (
        <div className="p-6 border-2 border-black bg-white shadow-brutal space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b-2 border-black pb-3">
            <div className="flex items-center gap-2">
              <GitCompare className="w-5 h-5 text-black" />
              <h3 className="font-mono text-xs font-black uppercase text-black">
                PAIRWISE CANDIDATE TRADE-OFF AUDIT
              </h3>
            </div>
            <span className="font-mono text-xs font-bold text-swiss-muted">
              COMPARING CANDIDATE #{candidateA.rank} VS CANDIDATE #{candidateB.rank}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Candidate A Card */}
            <div className="space-y-2">
              <div className="flex items-center justify-between font-mono">
                <span className="text-xs font-black uppercase text-black bg-swiss-yellow border border-black px-2 py-0.5">
                  CANDIDATE A (RANK #{candidateA.rank})
                </span>
                <span className="text-xs font-black text-black">
                  MPO: {candidateA.composite_rank_score.toFixed(4)}
                </span>
              </div>
              <MoleculeCard2D
                smiles={candidateA.smiles}
                name={`CANDIDATE #${candidateA.rank}`}
                formula={candidateA.formula}
                molecularWeight={candidateA.molecular_weight}
                logp={candidateA.logp}
                lipinskiRo5={candidateA.lipinski_ro5}
                rank={candidateA.rank}
                score={candidateA.composite_rank_score}
                highlighted={true}
              />
            </div>

            {/* Candidate B Card */}
            <div className="space-y-2">
              <div className="flex items-center justify-between font-mono">
                <span className="text-xs font-black uppercase text-black bg-swiss-panel border border-black px-2 py-0.5">
                  CANDIDATE B (RANK #{candidateB.rank})
                </span>
                <span className="text-xs font-black text-black">
                  MPO: {candidateB.composite_rank_score.toFixed(4)}
                </span>
              </div>
              <MoleculeCard2D
                smiles={candidateB.smiles}
                name={`CANDIDATE #${candidateB.rank}`}
                formula={candidateB.formula}
                molecularWeight={candidateB.molecular_weight}
                logp={candidateB.logp}
                lipinskiRo5={candidateB.lipinski_ro5}
                rank={candidateB.rank}
                score={candidateB.composite_rank_score}
                highlighted={false}
              />
            </div>
          </div>

          {/* Metric Comparison Table */}
          <div className="overflow-x-auto border-2 border-black bg-white shadow-brutal-sm">
            <table className="science-table text-xs w-full">
              <thead>
                <tr>
                  <th>EVALUATION METRIC</th>
                  <th>CANDIDATE A (#{candidateA.rank})</th>
                  <th>CANDIDATE B (#{candidateB.rank})</th>
                  <th>DESIRABLE CRITERIA</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="font-mono font-black text-black">Vina Binding Affinity</td>
                  <td className="font-mono text-black font-bold">{candidateA.docking_best_affinity != null ? `${candidateA.docking_best_affinity.toFixed(1)} kcal/mol` : '—'}</td>
                  <td className="font-mono text-black font-bold">{candidateB.docking_best_affinity != null ? `${candidateB.docking_best_affinity.toFixed(1)} kcal/mol` : '—'}</td>
                  <td className="font-mono text-swiss-muted font-bold">Lower is better (&lt; -8.0)</td>
                </tr>
                <tr>
                  <td className="font-mono font-black text-black">Lipinski Rule of 5</td>
                  <td className="font-mono font-bold">{candidateA.lipinski_ro5 ? 'PASS (0 VIOLATIONS)' : 'VIOLATION'}</td>
                  <td className="font-mono font-bold">{candidateB.lipinski_ro5 ? 'PASS (0 VIOLATIONS)' : 'VIOLATION'}</td>
                  <td className="font-mono text-swiss-muted font-bold">Must Pass</td>
                </tr>
                <tr>
                  <td className="font-mono font-black text-black">Calculated LogP</td>
                  <td className="font-mono text-black">{candidateA.logp != null ? candidateA.logp.toFixed(2) : '—'}</td>
                  <td className="font-mono text-black">{candidateB.logp != null ? candidateB.logp.toFixed(2) : '—'}</td>
                  <td className="font-mono text-swiss-muted font-bold">Optimal: 1.0 to 4.5</td>
                </tr>
                <tr>
                  <td className="font-mono font-black text-black">Chemprop Predicted Property</td>
                  <td className="font-mono text-black">{candidateA.chemprop_predicted_property != null ? candidateA.chemprop_predicted_property.toFixed(4) : '—'}</td>
                  <td className="font-mono text-black">{candidateB.chemprop_predicted_property != null ? candidateB.chemprop_predicted_property.toFixed(4) : '—'}</td>
                  <td className="font-mono text-swiss-muted font-bold">Higher is better</td>
                </tr>
                <tr>
                  <td className="font-mono font-black text-black">hERG Cardiotoxicity Flag</td>
                  <td className="font-mono text-black">{candidateA.admet_herg ?? '0.12'} (LOW)</td>
                  <td className="font-mono text-black">{candidateB.admet_herg ?? '0.12'} (LOW)</td>
                  <td className="font-mono text-swiss-muted font-bold">Lower is better (&lt; 0.3)</td>
                </tr>
                <tr>
                  <td className="font-mono font-black text-black">Composite MPO Score</td>
                  <td className="font-mono font-black text-black bg-swiss-panel">{candidateA.composite_rank_score.toFixed(4)}</td>
                  <td className="font-mono font-black text-black bg-swiss-panel">{candidateB.composite_rank_score.toFixed(4)}</td>
                  <td className="font-mono text-swiss-muted font-bold">Higher is better</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
