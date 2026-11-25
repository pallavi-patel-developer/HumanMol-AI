'use client';

import React from 'react';
import { ShieldAlert } from 'lucide-react';

interface Props {
  className?: string;
  compact?: boolean;
}

export const ScientificDisclaimer: React.FC<Props> = ({ className = '', compact = false }) => {
  if (compact) {
    return (
      <div className={`flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 text-xs ${className}`}>
        <span className="bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full font-bold text-[10px]">
          NOTICE
        </span>
        <span className="font-medium">In silico mathematical approximation. Requires experimental wet-lab validation.</span>
      </div>
    );
  }

  return (
    <div className={`rounded-2xl border border-slate-200/80 bg-white text-slate-900 text-xs shadow-sm p-5 space-y-2.5 ${className}`}>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2">
          <span className="bg-blue-50 text-blue-700 border border-blue-200/70 px-2.5 py-0.5 rounded-full font-bold text-[11px] tracking-wide">
            REGULATORY // SCIENTIFIC RIGOR NOTICE
          </span>
          <span className="text-[11px] font-semibold text-slate-500">
            CLEARANCE SPEC: IN-SILICO-APPROX
          </span>
        </div>
        <span className="text-[11px] text-slate-400 font-medium">PROTOCOL: ISO-BIO-2026</span>
      </div>

      <p className="text-xs leading-relaxed text-slate-600 font-medium">
        Computational predictions (including property predictions, ADMET profiles, and docking affinity scores) represent in silico mathematical approximations. Never interpret docking scores as proof of biological inhibition or clinical efficacy. Never classify generated molecules as safe or therapeutically effective without wet-lab in vitro assays and in vivo experimental validation.
      </p>
    </div>
  );
};
