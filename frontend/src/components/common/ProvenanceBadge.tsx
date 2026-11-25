'use client';

import React from 'react';

interface Props {
  type: 'computational' | 'experimental' | 'hybrid' | 'database';
  source: string;
  version?: string;
  confidence?: string | number;
  className?: string;
}

export const ProvenanceBadge: React.FC<Props> = ({
  type,
  source,
  version,
  confidence,
  className = '',
}) => {
  if (type === 'experimental') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-blue-200 bg-blue-50 text-blue-700 text-[11px] font-semibold ${className}`}
        title="Wet-lab experimental observation"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
        <span>EXP: {source}</span>
        {version && <span className="text-blue-600/80 font-normal">[{version}]</span>}
      </span>
    );
  }

  if (type === 'database') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-slate-200 bg-white text-slate-800 text-[11px] font-semibold shadow-xs ${className}`}
        title="Curated biological database record"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
        <span>DB: {source}</span>
        {version && <span className="text-slate-500 font-normal">[{version}]</span>}
      </span>
    );
  }

  if (type === 'hybrid') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-blue-300 bg-blue-100/60 text-blue-800 text-[11px] font-semibold ${className}`}
        title="Federated literature and preprint synthesis"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
        <span>HYBRID: {source}</span>
        {version && <span className="text-blue-700/80 font-normal">[{version}]</span>}
      </span>
    );
  }

  // Default: computational
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-slate-200 bg-slate-50 text-slate-700 text-[11px] font-semibold ${className}`}
      title="In silico predictive calculation"
    >
      <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
      <span>IN SILICO: {source}</span>
      {confidence !== undefined && (
        <span className="text-slate-500 font-normal">({confidence})</span>
      )}
    </span>
  );
};
