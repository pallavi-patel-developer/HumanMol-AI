'use client';

import React, { useState } from 'react';
import { Copy, Check, ShieldCheck, ShieldAlert } from 'lucide-react';

interface Props {
  smiles: string;
  name?: string;
  formula?: string | null;
  molecularWeight?: number | null;
  logp?: number | null;
  tpsa?: number | null;
  lipinskiRo5?: boolean | null;
  rank?: number;
  score?: number;
  highlighted?: boolean;
}

export const MoleculeCard2D: React.FC<Props> = ({
  smiles,
  name,
  formula,
  molecularWeight,
  logp,
  tpsa,
  lipinskiRo5,
  rank,
  score,
  highlighted = false,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(smiles);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`p-5 rounded-2xl border transition-all ${
        highlighted
          ? 'bg-blue-50/40 border-blue-400 shadow-md ring-2 ring-blue-500/20'
          : 'bg-white border-slate-200/80 shadow-sm hover:shadow-md hover:border-slate-300'
      }`}
    >
      {/* Top Header & Rank Badge */}
      <div className="flex items-start justify-between gap-3 mb-3 border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2.5">
          {rank !== undefined && (
            <div className="w-8 h-8 rounded-xl bg-blue-50 border border-blue-200/60 text-blue-600 font-bold text-xs flex items-center justify-center">
              #{rank}
            </div>
          )}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              {name || (formula ? `CANDIDATE // ${formula}` : 'MOLECULAR_ENTITY')}
            </h4>
            {score !== undefined && (
              <span className="text-[11px] font-medium text-slate-500 block mt-0.5">
                MPO_SCORE: <span className="text-slate-900 font-bold">{score.toFixed(3)}</span>
              </span>
            )}
          </div>
        </div>

        {/* Lipinski Ro5 Compliance Badge */}
        {lipinskiRo5 !== undefined && lipinskiRo5 !== null && (
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold ${
              lipinskiRo5
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/70'
                : 'bg-rose-50 text-rose-700 border border-rose-200/70'
            }`}
          >
            {lipinskiRo5 ? (
              <>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                RO5 PASS
              </>
            ) : (
              <>
                <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                RO5 VIOLATION
              </>
            )}
          </span>
        )}
      </div>

      {/* SMILES Display with Copy */}
      <div className="relative mb-3 group">
        <div className="p-2.5 rounded-xl border border-slate-200 bg-slate-50 font-mono text-[11px] font-medium text-slate-700 break-all select-all pr-8">
          {smiles}
        </div>
        <button
          onClick={handleCopy}
          title="Copy SMILES string"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-all shadow-xs cursor-pointer"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-600 font-bold" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
        </button>
      </div>

      {/* Physicochemical Properties Grid */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="p-2.5 rounded-xl border border-slate-100 bg-slate-50">
          <span className="text-[10px] font-semibold text-slate-400 block uppercase">MW (g/mol)</span>
          <span className="font-bold text-slate-800 text-sm mt-0.5 block">
            {molecularWeight ? `${molecularWeight.toFixed(1)}` : '—'}
          </span>
        </div>
        <div className="p-2.5 rounded-xl border border-slate-100 bg-slate-50">
          <span className="text-[10px] font-semibold text-slate-400 block uppercase">LogP</span>
          <span className="font-bold text-slate-800 text-sm mt-0.5 block">
            {logp !== undefined && logp !== null ? logp.toFixed(2) : '—'}
          </span>
        </div>
        <div className="p-2.5 rounded-xl border border-slate-100 bg-slate-50">
          <span className="text-[10px] font-semibold text-slate-400 block uppercase">TPSA (Å²)</span>
          <span className="font-bold text-slate-800 text-sm mt-0.5 block">
            {tpsa !== undefined && tpsa !== null ? `${tpsa.toFixed(1)}` : '—'}
          </span>
        </div>
      </div>
    </div>
  );
};
