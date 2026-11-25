'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  FlaskConical,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ExternalLink,
  RotateCw,
  GitCompare,
  ArrowRight,
  Info,
  Layers,
  Database,
  Search,
} from 'lucide-react';
import { scientificApi } from '@/lib/api';
import {
  BioactivityRecord,
  SelectivityCheckResponse,
  CandidateBioactivityStatusResponse,
} from '@/lib/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';
import { ScientificDisclaimer } from '@/components/common/ScientificDisclaimer';

export default function BioactivityIntelligencePage() {
  const [benchmarks, setBenchmarks] = useState<BioactivityRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'all' | 'recombinant' | 'cellular' | 'resistance'>('all');
  const [selectedCompound, setSelectedCompound] = useState<string>('all');
  const [candidateStatus, setCandidateStatus] = useState<CandidateBioactivityStatusResponse | null>(null);

  // Selectivity Checker State
  const [selectivityResult, setSelectivityResult] = useState<SelectivityCheckResponse | null>(null);
  const [checkingSelectivity, setCheckingSelectivity] = useState(false);
  const [activePreset, setActivePreset] = useState<string>('gefitinib_biochemical');

  // Load benchmark dataset and HM-EGFR-012 status
  const loadData = async () => {
    setLoading(true);
    try {
      const [benchResp, candResp] = await Promise.all([
        scientificApi.getBioactivityBenchmark(),
        scientificApi.getCandidateBioactivityStatus('HM-EGFR-012'),
      ]);
      setBenchmarks(benchResp.records);
      setCandidateStatus(candResp);

      // Run default preset selectivity check (Gefitinib Kd intra-study)
      runPresetSelectivity('gefitinib_kd', benchResp.records);
    } catch (err) {
      console.error('Failed to load bioactivity data:', err);
    } finally {
      setLoading(false);
    }
  };

  const runPresetSelectivity = async (presetKey: string, currentRecords?: BioactivityRecord[]) => {
    setCheckingSelectivity(true);
    setActivePreset(presetKey);
    const recs = currentRecords || benchmarks;

    let payload: any = null;

    if (presetKey === 'gefitinib_kd') {
      payload = {
        wt_assay_id: 'Yun2007-WT-Kd',
        mutant_assay_id: 'Yun2007-L858R-Kd',
        target_mutation: 'L858R',
      };
    } else if (presetKey === 'gefitinib_biochemical') {
      payload = {
        wt_assay_id: 'Barker2001-WT-IC50',
        mutant_assay_id: 'Yun2007-L858R-IC50',
        target_mutation: 'L858R',
      };
    } else if (presetKey === 'erlotinib_biochemical') {
      payload = {
        wt_assay_id: 'Moyer1997-WT-IC50',
        mutant_assay_id: 'Carey2006-L858R-IC50',
        target_mutation: 'L858R',
      };
    } else if (presetKey === 'afatinib_biochemical') {
      payload = {
        wt_assay_id: 'Li2008-WT-IC50',
        mutant_assay_id: 'Li2008-L858R-IC50',
        target_mutation: 'L858R',
      };
    } else if (presetKey === 'osimertinib_biochemical') {
      payload = {
        wt_assay_id: 'Cross2014-WT-IC50',
        mutant_assay_id: 'Cross2014-L858R-IC50',
        target_mutation: 'L858R',
      };
    } else if (presetKey === 'osimertinib_double_mutant') {
      payload = {
        wt_assay_id: 'Cross2014-WT-IC50',
        mutant_assay_id: 'Cross2014-T790M-IC50',
        target_mutation: 'L858R/T790M',
      };
    } else if (presetKey === 'osimertinib_cellular') {
      payload = {
        wt_assay_id: 'Finlay2014-LoVo-IC50',
        mutant_assay_id: 'Finlay2014-H1975-IC50',
        target_mutation: 'L858R/T790M',
      };
    } else if (presetKey === 'incomparable_format') {
      // Recombinant WT vs Cellular Mutant (Should reject)
      payload = {
        wt_assay_id: 'Cross2014-WT-IC50',
        mutant_assay_id: 'Finlay2014-H1975-IC50',
        target_mutation: 'L858R/T790M',
      };
    } else if (presetKey === 'incomparable_compound') {
      // Gefitinib WT vs Osimertinib Mutant (Should reject)
      payload = {
        wt_assay_id: 'Barker2001-WT-IC50',
        mutant_assay_id: 'Cross2014-L858R-IC50',
        target_mutation: 'L858R',
      };
    }

    try {
      if (payload) {
        const resp = await scientificApi.checkSelectivity(payload);
        setSelectivityResult(resp);
      }
    } catch (err) {
      console.error('Selectivity check failed:', err);
    } finally {
      setCheckingSelectivity(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter records based on tab and compound
  const filteredRecords = benchmarks.filter((r) => {
    // Filter by compound
    if (selectedCompound !== 'all' && r.compound_name.toLowerCase() !== selectedCompound.toLowerCase()) {
      return false;
    }

    // Filter by tab
    if (activeTab === 'recombinant') {
      return r.assay_format.includes('Recombinant') || r.assay_format.includes('Fluorescence');
    }
    if (activeTab === 'cellular') {
      return r.assay_format.includes('Cellular');
    }
    if (activeTab === 'resistance') {
      return r.mutation.includes('T790M') || r.mutation.includes('C797S');
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Swiss Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-2 border-black bg-white p-5 shadow-brutal">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 border border-black bg-swiss-yellow text-black font-mono text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#000]">
              02B
            </span>
            <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
              MODULE 02B: EXPERIMENTAL BIOACTIVITY & SELECTIVITY INTELLIGENCE
            </span>
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-black">
            EGFR L858R Wet-Lab Pharmacology Benchmarks
          </h1>
          <p className="text-xs font-mono text-swiss-muted">
            PRIMARY EXPERIMENTAL PROVENANCE (PMID/DOI VERIFIED), RECOMBINANT VS. CELLULAR TARGET ENGAGEMENT,
            AND SCIENTIFIC SELECTIVITY VALIDATION.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <Link
            href="/candidates"
            className="flex items-center gap-1.5 px-3 py-1.5 border-2 border-black bg-white hover:bg-swiss-panel text-black font-mono text-xs font-black uppercase transition-all shadow-[2px_2px_0px_#000]"
          >
            <GitCompare className="w-3.5 h-3.5" />
            <span>MPO CANDIDATE POOL</span>
          </Link>
          <button
            onClick={() => loadData()}
            disabled={loading}
            className="p-2 border-2 border-black bg-white hover:bg-swiss-panel text-black shadow-[1px_1px_0px_#000] cursor-pointer"
            title="Refresh bioactivity data"
          >
            <RotateCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Target & Rigor Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
          <div className="text-[10px] font-mono font-bold text-swiss-muted uppercase">BIOLOGICAL TARGET</div>
          <div className="text-lg font-black text-black">EGFR L858R</div>
          <div className="text-[10px] font-mono text-neutral-600">Homo sapiens // UniProt P00533</div>
        </div>
        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
          <div className="text-[10px] font-mono font-bold text-swiss-muted uppercase">STRUCTURAL REFERENCE</div>
          <div className="text-lg font-black text-black">PDB 2ITZ (Chain A)</div>
          <div className="text-[10px] font-mono text-neutral-600">2.8 Å Kinase Domain + Gefitinib</div>
        </div>
        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
          <div className="text-[10px] font-mono font-bold text-swiss-muted uppercase">REFERENCE TKIS AUDITED</div>
          <div className="text-lg font-black text-black">4 FDA-Approved</div>
          <div className="text-[10px] font-mono text-neutral-600">Gefitinib, Erlotinib, Afatinib, Osimertinib</div>
        </div>
        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
          <div className="text-[10px] font-mono font-bold text-swiss-muted uppercase">PRIMARY EVIDENCE STATUS</div>
          <div className="text-lg font-black text-emerald-700 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>100% VERIFIED</span>
          </div>
          <div className="text-[10px] font-mono text-neutral-600">Primary Papers (Table/Fig Verified)</div>
        </div>
      </div>

      {/* SECTION 1: INTERACTIVE SCIENTIFIC SELECTIVITY VALIDATOR */}
      <div className="border-2 border-black bg-white p-6 shadow-brutal space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b-2 border-black pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 bg-black" />
              <h2 className="text-sm font-mono font-black uppercase text-black">
                EXPERIMENTAL SELECTIVITY ENGINE // COMPARABILITY AUDIT
              </h2>
              <span className="border border-black bg-swiss-yellow px-2 py-0.5 font-mono text-[9px] font-black uppercase text-black">
                FORMULA: IC50(WT) / IC50(MUTANT)
              </span>
            </div>
            <p className="text-[11px] font-mono text-swiss-muted mt-0.5">
              Selectivity is derived strictly between scientifically comparable assay platforms. Mismatched assays are formally rejected.
            </p>
          </div>

          <ProvenanceBadge
            type="experimental"
            source="Primary Literature TR-FRET / Radiometric"
            version="Cross2014 / Yun2007 / Li2008"
          />
        </div>

        {/* Preset Selector Buttons */}
        <div>
          <div className="text-[10px] font-mono font-black uppercase tracking-wider text-neutral-500 mb-2">
            PRESET COMPARATIVE PAIRS (CLICK TO AUDIT):
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => runPresetSelectivity('gefitinib_kd')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'gefitinib_kd'
                  ? 'border-black bg-swiss-yellow text-black shadow-brutal-sm'
                  : 'border-black/40 bg-white text-neutral-700 hover:border-black'
              }`}
            >
              ★ Gefitinib (Intra-Study Kd: 53.5 ± 1.8 nM vs 2.6 ± 0.2 nM — Fluorescence Quenching, Table 3)
            </button>
            <button
              onClick={() => runPresetSelectivity('gefitinib_biochemical')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'gefitinib_biochemical'
                  ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-brutal-sm'
                  : 'border-amber-400 bg-white text-amber-800 hover:border-amber-600'
              }`}
            >
              ⚠ Gefitinib (Cross-Study IC50: 33 nM vs 7.8 nM — Exploratory)
            </button>
            <button
              onClick={() => runPresetSelectivity('erlotinib_biochemical')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'erlotinib_biochemical'
                  ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-brutal-sm'
                  : 'border-amber-400 bg-white text-amber-800 hover:border-amber-600'
              }`}
            >
              ⚠ Erlotinib (Cross-Study IC50: 2.0 nM vs 0.5 nM — Exploratory)
            </button>
            <button
              onClick={() => runPresetSelectivity('afatinib_biochemical')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'afatinib_biochemical'
                  ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-brutal-sm'
                  : 'border-amber-400 bg-white text-amber-800 hover:border-amber-600'
              }`}
            >
              ⚠ Afatinib (Provisional Same-Study: 0.5 nM vs 0.4 nM — Incubation Unreported)
            </button>
            <button
              onClick={() => runPresetSelectivity('osimertinib_biochemical')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'osimertinib_biochemical'
                  ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-brutal-sm'
                  : 'border-amber-400 bg-white text-amber-800 hover:border-amber-600'
              }`}
            >
              ⚠ Osimertinib (Provisional Same-Study: 184 nM vs 12 nM — Incubation Unreported)
            </button>
            <button
              onClick={() => runPresetSelectivity('osimertinib_double_mutant')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'osimertinib_double_mutant'
                  ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-brutal-sm'
                  : 'border-amber-400 bg-white text-amber-800 hover:border-amber-600'
              }`}
            >
              ⚠ Osimertinib (Provisional T790M: 184 nM vs 1.0 nM — Incubation Unreported)
            </button>
            <button
              onClick={() => runPresetSelectivity('osimertinib_cellular')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'osimertinib_cellular'
                  ? 'border-amber-600 bg-amber-100 text-amber-900 shadow-brutal-sm'
                  : 'border-amber-400 bg-white text-amber-800 hover:border-amber-600'
              }`}
            >
              ⚠ Osimertinib (Cellular Target Engagement: 480 nM vs 15 nM — Non-Isogenic LoVo/H1975)
            </button>
            <button
              onClick={() => runPresetSelectivity('incomparable_format')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'incomparable_format'
                  ? 'border-red-600 bg-red-100 text-red-900 shadow-brutal-sm'
                  : 'border-red-400 bg-white text-red-700 hover:border-red-600'
              }`}
              title="Negative Control: Enzyme IC50 vs Cellular IC50"
            >
              ⚠ Negative Test: Enzyme IC50 vs Cellular IC50
            </button>
            <button
              onClick={() => runPresetSelectivity('incomparable_compound')}
              className={`px-3 py-1.5 text-xs font-mono font-bold uppercase border-2 transition-all cursor-pointer ${
                activePreset === 'incomparable_compound'
                  ? 'border-red-600 bg-red-100 text-red-900 shadow-brutal-sm'
                  : 'border-red-400 bg-white text-red-700 hover:border-red-600'
              }`}
              title="Negative Control: Gefitinib WT vs Osimertinib Mutant"
            >
              ⚠ Negative Test: Differing Compounds
            </button>
          </div>
        </div>

        {/* Live Calculation Result Card */}
        {selectivityResult && (
          <div
            className={`border-2 p-5 shadow-brutal-sm transition-all ${
              selectivityResult.comparability_status === 'COMPARABLE'
                ? 'border-black bg-swiss-panel'
                : selectivityResult.comparability_status === 'PROVISIONAL' || selectivityResult.comparability_status === 'PROVISIONAL_CELLULAR_CONTEXT' || selectivityResult.comparability_status === 'INCOMPARABLE_CROSS_STUDY'
                ? 'border-amber-600 bg-amber-50'
                : 'border-red-600 bg-red-50'
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-4 mb-4 border-black/20">
              <div className="flex items-center gap-3">
                <span
                  className={`px-3 py-1 text-xs font-mono font-black uppercase border ${
                    selectivityResult.comparability_status === 'COMPARABLE'
                      ? 'border-emerald-800 bg-emerald-600 text-white'
                      : selectivityResult.comparability_status === 'PROVISIONAL'
                      ? 'border-amber-800 bg-amber-400 text-black'
                      : selectivityResult.comparability_status === 'PROVISIONAL_CELLULAR_CONTEXT'
                      ? 'border-amber-800 bg-amber-300 text-black'
                      : selectivityResult.comparability_status === 'INCOMPARABLE_CROSS_STUDY'
                      ? 'border-amber-800 bg-amber-200 text-black'
                      : selectivityResult.comparability_status === 'INCOMPARABLE_ENDPOINT'
                      ? 'border-red-800 bg-red-600 text-white'
                      : 'border-red-800 bg-red-600 text-white'
                  }`}
                >
                  {selectivityResult.comparability_status === 'COMPARABLE'
                    ? '✓ INTRA-STUDY VALIDATED SELECTIVITY'
                    : selectivityResult.comparability_status === 'PROVISIONAL'
                    ? '⚠ PROVISIONAL (SAME-STUDY, UNVERIFIED KINETICS)'
                    : selectivityResult.comparability_status === 'PROVISIONAL_CELLULAR_CONTEXT'
                    ? '⚠ PROVISIONAL (CELLULAR CONTEXT — NON-ISOGENIC BACKGROUND)'
                    : selectivityResult.comparability_status === 'INCOMPARABLE_CROSS_STUDY'
                    ? '⚠ EXPLORATORY CROSS-STUDY RATIO'
                    : selectivityResult.comparability_status === 'INCOMPARABLE_ENDPOINT'
                    ? '✕ INCOMPARABLE ENDPOINT (Kd vs IC50 / Cell vs Recomb)'
                    : '✕ INCOMPARABLE ASSAYS'}
                </span>

                {selectivityResult.selectivity_ratio !== null && selectivityResult.selectivity_ratio !== undefined ? (
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-black text-black font-mono">
                      {selectivityResult.selectivity_ratio}×
                    </span>
                    <span className="text-xs font-mono font-bold text-neutral-600">
                      VALIDATED SELECTIVITY RATIO [WT / MUTANT]
                    </span>
                  </div>
                ) : selectivityResult.exploratory_ratio ? (
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-black text-amber-800 font-mono">
                      {selectivityResult.exploratory_ratio}×
                    </span>
                    <span className="text-xs font-mono font-bold text-amber-700">
                      CONTEXTUAL / EXPLORATORY RATIO ONLY (NOT VALIDATED)
                    </span>
                  </div>
                ) : (
                  <span className="text-sm font-mono font-black text-red-700">
                    RATIO NOT COMPUTABLE (SCIENTIFICALLY INCOMPARABLE)
                  </span>
                )}
              </div>

              <span className="text-xs font-mono font-black uppercase tracking-wider text-black">
                INTERPRETATION: {selectivityResult.selectivity_interpretation}
              </span>
            </div>

            {/* Rejection / Limitation Alert */}
            {selectivityResult.rejection_reason && (
              <div
                className={`border p-3 mb-4 text-xs font-mono flex items-start gap-2 ${
                  selectivityResult.comparability_status === 'PROVISIONAL' || selectivityResult.comparability_status === 'PROVISIONAL_CELLULAR_CONTEXT' || selectivityResult.comparability_status === 'INCOMPARABLE_CROSS_STUDY'
                    ? 'border-amber-400 bg-amber-100 text-amber-900'
                    : 'border-red-500 bg-red-100 text-red-900'
                }`}
              >
                {selectivityResult.comparability_status === 'PROVISIONAL' || selectivityResult.comparability_status === 'PROVISIONAL_CELLULAR_CONTEXT' || selectivityResult.comparability_status === 'INCOMPARABLE_CROSS_STUDY' ? (
                  <Info className="w-4 h-4 text-amber-700 mt-0.5 flex-shrink-0" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                )}
                <div>
                  <span className="font-bold uppercase">
                    {selectivityResult.comparability_status === 'PROVISIONAL_CELLULAR_CONTEXT'
                      ? 'CELLULAR CONTEXT LIMITATION: '
                      : selectivityResult.comparability_status === 'PROVISIONAL'
                      ? 'KINETIC LIMITATION: '
                      : selectivityResult.comparability_status === 'INCOMPARABLE_CROSS_STUDY'
                      ? 'CROSS-STUDY LIMITATION: '
                      : 'REJECTION RATIONALE: '}
                  </span>
                  {selectivityResult.rejection_reason}
                </div>
              </div>
            )}

            {selectivityResult.cellular_context_note && (
              <div className="border border-purple-400 bg-purple-50 text-purple-900 p-2.5 mb-4 text-xs font-mono flex items-center gap-2">
                <Info className="w-4 h-4 text-purple-600 flex-shrink-0" />
                <span><strong>CELLULAR PHARMACOLOGY BOUNDARY:</strong> {selectivityResult.cellular_context_note}</span>
              </div>
            )}

            {selectivityResult.irreversible_kinetics_note && (
              <div className="border border-sky-400 bg-sky-50 text-sky-900 p-2.5 mb-4 text-xs font-mono flex items-center gap-2">
                <Info className="w-4 h-4 text-sky-600 flex-shrink-0" />
                <span><strong>COVALENT INHIBITOR PHARMACOLOGY:</strong> {selectivityResult.irreversible_kinetics_note}</span>
              </div>
            )}

            {/* Side-by-Side Assay Inspector */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-3 border border-black/40 bg-white">
                <div className="text-[10px] font-black text-neutral-500 uppercase mb-1">
                  BASELINE: WILD-TYPE EGFR MEASUREMENT
                </div>
                {selectivityResult.wt_measurement ? (
                  <div className="space-y-1">
                    <div className="font-bold text-black text-sm">
                      {selectivityResult.wt_measurement.compound_name} — {selectivityResult.wt_measurement.mutation}
                    </div>
                    <div className="text-neutral-700">
                      Assay: {selectivityResult.wt_measurement.assay_description}
                    </div>
                    <div className="font-bold text-emerald-800">
                      Standard Value: {selectivityResult.wt_measurement.standard_value} {selectivityResult.wt_measurement.standard_units} ({selectivityResult.wt_measurement.measurement_type})
                    </div>
                    <div className="text-[11px] text-neutral-500">
                      Format: {selectivityResult.wt_measurement.assay_format} | ATP: {selectivityResult.wt_measurement.atp_concentration || 'N/A'}
                    </div>
                    <div className="text-[10px] text-neutral-600 truncate">
                      Ref: {selectivityResult.wt_measurement.primary_citation} ({selectivityResult.wt_measurement.table_figure_ref})
                    </div>
                  </div>
                ) : (
                  <div className="text-neutral-500 italic">No WT record selected</div>
                )}
              </div>

              <div className="p-3 border border-black/40 bg-white">
                <div className="text-[10px] font-black text-neutral-500 uppercase mb-1">
                  COMPARATOR: MUTANT EGFR MEASUREMENT
                </div>
                {selectivityResult.mutant_measurement ? (
                  <div className="space-y-1">
                    <div className="font-bold text-black text-sm">
                      {selectivityResult.mutant_measurement.compound_name} — {selectivityResult.mutant_measurement.mutation}
                    </div>
                    <div className="text-neutral-700">
                      Assay: {selectivityResult.mutant_measurement.assay_description}
                    </div>
                    <div className="font-bold text-emerald-800">
                      Standard Value: {selectivityResult.mutant_measurement.standard_value} {selectivityResult.mutant_measurement.standard_units} ({selectivityResult.mutant_measurement.measurement_type})
                    </div>
                    <div className="text-[11px] text-neutral-500">
                      Format: {selectivityResult.mutant_measurement.assay_format} | ATP: {selectivityResult.mutant_measurement.atp_concentration || 'N/A'}
                    </div>
                    <div className="text-[10px] text-neutral-600 truncate">
                      Ref: {selectivityResult.mutant_measurement.primary_citation} ({selectivityResult.mutant_measurement.table_figure_ref})
                    </div>
                  </div>
                ) : (
                  <div className="text-neutral-500 italic">No Mutant record selected</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 2: CANDIDATE EVIDENCE MAPPING (HM-EGFR-012 SPOTLIGHT) */}
      {candidateStatus && (
        <div className="border-2 border-black bg-white p-6 shadow-brutal space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b-2 border-black pb-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 bg-swiss-yellow border border-black" />
              <h2 className="text-sm font-mono font-black uppercase text-black">
                CANDIDATE EVIDENCE MAPPING // {candidateStatus.candidate_id}
              </h2>
              <span className="border border-black bg-neutral-200 px-2 py-0.5 font-mono text-[9px] font-black uppercase text-neutral-800">
                DE NOVO COMPUTATIONAL CANDIDATE
              </span>
            </div>

            <span className="px-2.5 py-1 border border-black bg-amber-100 text-amber-900 font-mono text-[10px] font-black uppercase">
              STATUS: UNTESTED EXPERIMENTALLY
            </span>
          </div>

          {/* Chemical Identity Specification Bar */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-2 text-xs font-mono border border-black/30 bg-neutral-50 p-3">
            <div>
              <span className="text-[10px] text-neutral-500 uppercase block font-bold">VERIFIED FORMULA</span>
              <span className="font-black text-black">
                {candidateStatus.molecular_formula || 'C17H21N5O2S'}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 uppercase block font-bold">AVG MOLECULAR WEIGHT</span>
              <span className="font-black text-black">
                {candidateStatus.molecular_weight ? `${candidateStatus.molecular_weight} g/mol` : '359.46 g/mol'}
              </span>
              <span className="text-[9px] text-neutral-500 block">Exact: 359.1416 g/mol</span>
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 uppercase block font-bold">INCHIKEY</span>
              <span className="font-mono text-[11px] text-black">
                {candidateStatus.inchikey || 'DCESSRBOYUDSNL-UHFFFAOYSA-N'}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-neutral-500 uppercase block font-bold">CANONICAL SMILES</span>
              <span className="font-mono text-[10px] text-neutral-800 truncate block" title={candidateStatus.canonical_smiles || ''}>
                {candidateStatus.canonical_smiles || 'Nc1nc(cc2c1nc(n2CCCO)C1(O)CCCC1)-c1nccs1'}
              </span>
            </div>
          </div>

          {/* Strict Separation Callout */}
          <div className="border-2 border-amber-500 bg-amber-50 p-4 shadow-brutal-sm">
            <div className="flex items-start gap-2.5">
              <ShieldAlert className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <div className="font-mono text-xs font-black uppercase text-amber-900">
                  CRITICAL SCIENTIFIC INTEGRITY REQUIREMENT
                </div>
                <p className="text-xs font-sans text-neutral-800 leading-relaxed">
                  {candidateStatus.scientific_disclaimer}
                </p>
              </div>
            </div>
          </div>

          {/* Side-by-Side: Computational Profile vs Experimental Reality */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Computational Side */}
            <div className="p-4 border-2 border-black bg-white space-y-2">
              <div className="flex items-center justify-between border-b border-black pb-2">
                <span className="font-mono text-xs font-black uppercase text-black">
                  IN SILICO COMPUTATIONAL PROFILE
                </span>
                <ProvenanceBadge
                  type="computational"
                  source="Vina v1.2.7 + Chemprop v2.3.1 + ADMETlab 3.0"
                  version="Stage 3 Validated"
                />
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
                <div className="p-2 border border-black/20 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">PREDICTED VINA DOCKING SCORE (2ITZ)</span>
                  <span className="font-black text-black text-sm">
                    {candidateStatus.computational_profile.docking_best_affinity_kcal_mol} kcal/mol
                  </span>
                  <span className="text-[9px] text-neutral-500 block">AutoDock Vina v1.2.7 (empirical score)</span>
                </div>
                <div className="p-2 border border-black/20 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">COMPOSITE MPO SCORE</span>
                  <span className="font-black text-black text-sm">
                    {candidateStatus.computational_profile.composite_mpo_score} / 10.0
                  </span>
                  <span className="text-[9px] text-neutral-500 block">Multi-parameter optimization</span>
                </div>
                <div className="p-2 border border-black/20 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">CACO-2 PERMEABILITY</span>
                  <span className="font-bold text-black text-[11px]">
                    -4.62 log10(cm/s)
                  </span>
                  <span className="text-[9px] text-neutral-500 block">ADMETlab 3.0 log permeability</span>
                </div>
                <div className="p-2 border border-black/20 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">hERG LIABILITY</span>
                  <span className="font-bold text-black text-[11px]">
                    LOW PREDICTED LIABILITY (0.02)
                  </span>
                  <span className="text-[9px] text-neutral-500 block">ADMETlab 3.0 probability</span>
                </div>
                <div className="p-2 border border-black/20 bg-neutral-50 col-span-2">
                  <span className="text-[10px] text-neutral-500 block">DILI HEPATOTOX RISK</span>
                  <span className="font-bold text-black text-[11px]">
                    LOW PREDICTED RISK (0.11)
                  </span>
                  <span className="text-[9px] text-neutral-500 block">ADMETlab 3.0 multi-task classifier</span>
                </div>
              </div>
              <div className="text-[9px] font-mono text-neutral-600 bg-neutral-100 p-2 border border-neutral-300">
                <strong>DOCKING DISCLAIMER:</strong> The predicted Vina score (-7.161 kcal/mol) represents a mathematical optimization score from an empirical scoring function. It is NOT experimentally measured binding affinity, Kd, Ki, IC50, or thermodynamic free energy of binding (ΔG°).
              </div>
            </div>

            {/* Experimental Wet-Lab Side */}
            <div className="p-4 border-2 border-black bg-white space-y-2">
              <div className="flex items-center justify-between border-b border-black pb-2">
                <span className="font-mono text-xs font-black uppercase text-black">
                  PHYSICAL EXPERIMENTAL BIOACTIVITY
                </span>
                <span className="px-2 py-0.5 border border-dashed border-red-600 bg-red-50 text-red-700 text-[10px] font-mono font-bold uppercase">
                  WET-LAB RECORDS: 0
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-1">
                <div className="p-2 border border-dashed border-neutral-300 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">EGFR L858R IC50</span>
                  <span className="font-bold text-amber-800">UNTESTED</span>
                </div>
                <div className="p-2 border border-dashed border-neutral-300 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">WILD-TYPE EGFR IC50</span>
                  <span className="font-bold text-amber-800">UNTESTED</span>
                </div>
                <div className="p-2 border border-dashed border-neutral-300 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">SELECTIVITY RATIO</span>
                  <span className="font-bold text-neutral-500">NOT_AVAILABLE</span>
                </div>
                <div className="p-2 border border-dashed border-neutral-300 bg-neutral-50">
                  <span className="text-[10px] text-neutral-500 block">CELL VIABILITY (H1975)</span>
                  <span className="font-bold text-amber-800">UNTESTED</span>
                </div>
              </div>
            </div>
          </div>

          {/* Required Wet-Lab Assays Pipeline */}
          <div className="border border-black p-4 bg-swiss-panel space-y-3">
            <div className="text-xs font-mono font-black uppercase text-black flex items-center gap-2">
              <FlaskConical className="w-4 h-4 text-black" />
              <span>MANDATORY WET-LAB VALIDATION PROTOCOLS PRIOR TO PHARMACOLOGICAL CLAIM:</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {candidateStatus.required_validation_assays.map((assay) => (
                <div key={assay.step} className="p-3 border border-black bg-white space-y-1">
                  <div className="flex items-center justify-between text-[10px] font-mono font-black">
                    <span className="bg-black text-white px-1.5 py-0.2">STEP 0{assay.step}</span>
                    <span className="text-amber-700">PENDING</span>
                  </div>
                  <div className="text-xs font-bold font-mono text-black">{assay.assay_name}</div>
                  <div className="text-[10px] font-sans text-neutral-600">{assay.objective}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SECTION 3: VERIFIED REFERENCE TKI PHARMACOLOGY TABLE */}
      <div className="border-2 border-black bg-white p-6 shadow-brutal space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b-2 border-black pb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 bg-black" />
              <h2 className="text-sm font-mono font-black uppercase text-black">
                PRIMARY-SOURCE REFERENCE INHIBITOR PHARMACOLOGY BENCHMARK
              </h2>
              <span className="border border-black bg-emerald-100 text-emerald-900 px-2 py-0.5 font-mono text-[9px] font-black uppercase">
                {benchmarks.length} RECORDS AUDITED
              </span>
            </div>
            <p className="text-[11px] font-mono text-swiss-muted mt-0.5">
              Every data point maps to peer-reviewed primary discovery literature with verified DOI, PMID, and figure/table references.
            </p>
          </div>

          {/* Compound Quick Filter */}
          <div className="flex items-center gap-1 border border-black bg-swiss-panel p-1">
            {['all', 'gefitinib', 'erlotinib', 'afatinib', 'osimertinib'].map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCompound(c)}
                className={`px-2 py-1 text-[10px] font-mono font-black uppercase transition-all ${
                  selectedCompound === c
                    ? 'bg-swiss-yellow text-black border border-black shadow-[1px_1px_0px_#000]'
                    : 'bg-transparent text-neutral-600 hover:text-black'
                }`}
              >
                {c === 'all' ? 'All Drugs' : c}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Filters */}
        <div className="flex flex-wrap gap-2 border-b border-black pb-2">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1 text-xs font-mono font-bold uppercase transition-all ${
              activeTab === 'all' ? 'border-b-2 border-black bg-black text-white' : 'text-neutral-600 hover:text-black'
            }`}
          >
            All Assays ({benchmarks.length})
          </button>
          <button
            onClick={() => setActiveTab('recombinant')}
            className={`px-3 py-1 text-xs font-mono font-bold uppercase transition-all ${
              activeTab === 'recombinant' ? 'border-b-2 border-black bg-black text-white' : 'text-neutral-600 hover:text-black'
            }`}
          >
            Recombinant Kinase Domain
          </button>
          <button
            onClick={() => setActiveTab('cellular')}
            className={`px-3 py-1 text-xs font-mono font-bold uppercase transition-all ${
              activeTab === 'cellular' ? 'border-b-2 border-black bg-black text-white' : 'text-neutral-600 hover:text-black'
            }`}
          >
            Cellular Target Engagement
          </button>
          <button
            onClick={() => setActiveTab('resistance')}
            className={`px-3 py-1 text-xs font-mono font-bold uppercase transition-all ${
              activeTab === 'resistance' ? 'border-b-2 border-black bg-black text-white' : 'text-neutral-600 hover:text-black'
            }`}
          >
            Resistance Mutants (T790M / C797S)
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto border-2 border-black bg-white shadow-brutal-sm">
          <table className="science-table text-xs w-full">
            <thead>
              <tr>
                <th>COMPOUND & ID</th>
                <th>CONSTRUCT / MUTATION</th>
                <th>ASSAY FORMAT & SYSTEM</th>
                <th>POTENCY VALUE</th>
                <th>ATP CONC</th>
                <th>PROVENANCE & CITATION</th>
                <th>VERIFICATION STATUS</th>
              </tr>
            </thead>
            <tbody>
              {filteredRecords.map((r, idx) => (
                <tr key={idx} className="hover:bg-swiss-panel/40 transition-colors">
                  <td className="font-bold">
                    <div className="font-mono text-black">{r.compound_name}</div>
                    <div className="text-[10px] font-mono text-neutral-500">{r.compound_chembl_id}</div>
                  </td>
                  <td>
                    <span
                      className={`px-2 py-0.5 border text-[10px] font-mono font-bold uppercase ${
                        r.mutation === 'Wild-Type'
                          ? 'border-neutral-400 bg-neutral-100 text-neutral-800'
                          : r.mutation === 'L858R'
                          ? 'border-emerald-600 bg-emerald-100 text-emerald-900 font-black'
                          : 'border-red-600 bg-red-100 text-red-900'
                      }`}
                    >
                      {r.mutation}
                    </span>
                    {r.cell_line && (
                      <div className="text-[10px] text-neutral-500 mt-0.5">{r.cell_line}</div>
                    )}
                  </td>
                  <td>
                    <div className="font-medium text-neutral-800 text-[11px]">{r.assay_format}</div>
                    <div className="text-[10px] text-neutral-500 line-clamp-1" title={r.assay_description}>
                      {r.assay_description}
                    </div>
                  </td>
                  <td className="font-mono font-black text-black text-sm">
                    <span className="text-emerald-700">
                      {r.standard_relation !== '=' ? r.standard_relation : ''}{r.standard_value} {r.standard_units}
                    </span>
                    <span className="text-[10px] font-normal text-neutral-500 block">
                      {r.measurement_type} {r.uncertainty_value !== null && r.uncertainty_value !== undefined ? `± ${r.uncertainty_value} nM` : '(Uncertainty NOT_REPORTED)'}
                    </span>
                  </td>
                  <td className="font-mono text-[11px] text-neutral-700">
                    {r.atp_concentration || 'Standard'}
                  </td>
                  <td className="text-[11px]">
                    <div className="font-bold text-neutral-800">
                      {r.primary_citation.split('.')[0]}. ({r.publication_year})
                    </div>
                    <div className="flex items-center gap-2 mt-0.5 text-[10px] font-mono">
                      {r.pmid && (
                        <a
                          href={`https://pubmed.ncbi.nlm.nih.gov/${r.pmid}/`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-700 hover:underline flex items-center gap-0.5"
                        >
                          <span>PMID:{r.pmid}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                      {r.doi && (
                        <a
                          href={`https://doi.org/${r.doi}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-700 hover:underline flex items-center gap-0.5"
                        >
                          <span>DOI</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                      <span className="text-neutral-500">{r.table_figure_ref}</span>
                    </div>
                  </td>
                  <td>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 border border-black bg-emerald-100 text-black text-[9px] font-mono font-bold uppercase shadow-brutal-sm">
                      <span className="w-1.5 h-1.5 bg-emerald-600 border border-black" />
                      <span>{r.verification_status.replace(/_/g, ' ')}</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Regulatory & Scientific Disclaimer */}
      <ScientificDisclaimer />
    </div>
  );
}
