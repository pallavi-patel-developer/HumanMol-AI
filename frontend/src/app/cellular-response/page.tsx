'use client';

import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  AlertCircle,
  Dna,
} from 'lucide-react';
import { scientificApi } from '@/lib/api';
import { XPertStatusResponse } from '@/lib/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';

export default function CellularResponsePage() {
  const [status, setStatus] = useState<XPertStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await scientificApi.getXpertStatus();
      setStatus(data);
    } catch (err: any) {
      console.error('Failed to get XPert status:', err);
      setError(err.message || 'Failed to query XPert engine status.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="space-y-6">
      {/* Swiss Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-2 border-black bg-white p-5 shadow-brutal">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 border border-black bg-swiss-yellow text-black font-mono text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#000]">
              07
            </span>
            <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
              MODULE 07: HUMAN CELLULAR RESPONSE
            </span>
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-black">
            XPert Dual-Branch Transformer Engine
          </h1>
          <p className="text-xs font-mono text-swiss-muted">
            TRANSCRIPTOMIC PERTURBATION MODELING: PREDICTING DIFFERENTIAL EXPRESSION CHANGES (ΔE) ACROSS 978 L1000 LANDMARK GENES.
          </p>
        </div>

        <ProvenanceBadge
          type="computational"
          source="XPert Dual-Branch Transformer"
          version="SDPA CPU Fallback"
        />
      </div>

      {/* Prominent Operational Status Banner */}
      <div className="p-6 border-2 border-black bg-swiss-yellow text-black shadow-brutal space-y-3 font-mono">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 flex-shrink-0 text-black mt-0.5" />
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-sm font-black uppercase tracking-wider text-black">
                STATUS: ARCHITECTURE VERIFIED // LIVE INFERENCE UNAVAILABLE
              </h2>
              <span className="text-[10px] px-2 py-0.5 border border-black bg-black text-swiss-yellow font-black uppercase">
                AWAITING UPSTREAM CHECKPOINT
              </span>
            </div>
            <p className="text-xs leading-relaxed text-black font-bold">
              The XPert Dual-Branch Transformer model architecture and PyTorch SDPA (Scaled Dot-Product Attention) CPU fallback have been successfully integrated and verified in the backend. However, because the official XPert repository author has not yet released the public pretrained weights checkpoint, full transcriptomic perturbation inference is marked as <strong>UNAVAILABLE</strong> to ensure 100% scientific integrity and prevent fabricated biological predictions.
            </p>
          </div>
        </div>
      </div>

      {/* Engineering Diagnostic Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm space-y-2">
          <div className="flex items-center justify-between border-b border-black pb-1">
            <span className="text-xs text-swiss-muted font-bold uppercase">MODEL ARCHITECTURE</span>
            <CheckCircle2 className="w-4 h-4 text-black" />
          </div>
          <div className="text-sm font-black text-black">Dual-Branch Transformer</div>
          <p className="text-[11px] text-swiss-muted">
            Separate cross-attention branches for molecular SMILES graph and basal transcriptomic gene profile.
          </p>
        </div>

        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm space-y-2">
          <div className="flex items-center justify-between border-b border-black pb-1">
            <span className="text-xs text-swiss-muted font-bold uppercase">ATTENTION MECHANISM</span>
            <CheckCircle2 className="w-4 h-4 text-black" />
          </div>
          <div className="text-sm font-black text-black">PyTorch SDPA CPU Fallback</div>
          <p className="text-[11px] text-swiss-muted">
            FlashAttention-2 Windows incompatibility resolved via torch.nn.functional.scaled_dot_product_attention.
          </p>
        </div>

        <div className="p-4 border-2 border-black bg-white shadow-brutal-sm space-y-2">
          <div className="flex items-center justify-between border-b border-black pb-1">
            <span className="text-xs text-swiss-muted font-bold uppercase">INFERENCE READINESS</span>
            <AlertCircle className="w-4 h-4 text-black" />
          </div>
          <div className="text-sm font-black text-black">Pending Weights & GPU</div>
          <p className="text-[11px] text-swiss-muted">
            Awaiting official checkpoint release or transfer learning fine-tuning on LINCS L1000 dataset.
          </p>
        </div>
      </div>

      {/* Biological Pipeline Architecture Overview */}
      <div className="p-6 border-2 border-black bg-white shadow-brutal space-y-4 font-mono">
        <h3 className="text-xs font-black uppercase text-black flex items-center gap-2 border-b-2 border-black pb-2">
          <Dna className="w-4 h-4 text-black" />
          TRANSCRIPTOMIC PERTURBATION PIPELINE ARCHITECTURE
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 border-2 border-black bg-swiss-panel space-y-3">
            <h4 className="text-xs font-black uppercase text-black border-b border-black pb-1">
              INPUT VECTORS (DUAL-BRANCH)
            </h4>
            <div className="space-y-2 text-xs">
              <div className="p-2 border border-black bg-white">
                <span className="text-swiss-muted block text-[10px] font-bold uppercase">BRANCH 1: CHEMICAL MOLECULE</span>
                <span className="text-black font-black">SMILES graph atom/bond tokenization (D-MPNN / Transformer)</span>
              </div>
              <div className="p-2 border border-black bg-white">
                <span className="text-swiss-muted block text-[10px] font-bold uppercase">BRANCH 2: BASAL CELL STATE</span>
                <span className="text-black font-black">Pre-treatment basal expression vector (978 L1000 landmark genes)</span>
              </div>
              <div className="p-2 border border-black bg-white">
                <span className="text-swiss-muted block text-[10px] font-bold uppercase">CONDITIONS</span>
                <span className="text-black font-black">Dosage (e.g. 10.0 µM) + Exposure Time (e.g. 24 hours)</span>
              </div>
            </div>
          </div>

          <div className="p-4 border-2 border-black bg-swiss-panel space-y-3">
            <h4 className="text-xs font-black uppercase text-black border-b border-black pb-1">
              PREDICTED BIOLOGICAL OUTPUT
            </h4>
            <div className="space-y-2 text-xs">
              <div className="p-2 border border-black bg-white">
                <span className="text-swiss-muted block text-[10px] font-bold uppercase">DIFFERENTIAL EXPRESSION VECTOR</span>
                <span className="text-black font-black">Predicted z-scores (ΔE) across 978 landmark genes</span>
              </div>
              <div className="p-2 border border-black bg-white">
                <span className="text-swiss-muted block text-[10px] font-bold uppercase">CELL LINE SPECIFICITY</span>
                <span className="text-black font-black">MCF7 (Breast), A549 (Lung), PC3 (Prostate), VCAP</span>
              </div>
              <div className="p-2 border border-black bg-white">
                <span className="text-swiss-muted block text-[10px] font-bold uppercase">PATHWAY ENRICHMENT</span>
                <span className="text-black font-black">Gene Set Enrichment Analysis (GSEA) / Reactome mapping</span>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-2 text-[10px] text-swiss-muted font-bold uppercase border-t border-black">
          MODEL PATH: scientific_engine/cell_response/xpert/ • PYTORCH CPU SDPA FALLBACK ACTIVE
        </div>
      </div>
    </div>
  );
}
