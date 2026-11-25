'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  BookOpen,
  Search,
  RotateCw,
  ExternalLink,
  FileText,
  AlertCircle,
  FlaskConical,
  Cpu,
} from 'lucide-react';
import { scientificApi } from '@/lib/api';
import { EvidenceSearchResponse } from '@/lib/types';
import { ProvenanceBadge } from '@/components/common/ProvenanceBadge';

function ResearchEvidenceContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('query') || 'EGFR tyrosine kinase inhibitor resistance';

  const [query, setQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [evidenceData, setEvidenceData] = useState<EvidenceSearchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'pubmed' | 'arxiv'>('all');

  const handleSearch = async (searchTerm: string) => {
    if (!searchTerm.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await scientificApi.searchEvidence(searchTerm, 5, 5);
      setEvidenceData(data);
    } catch (err: any) {
      console.error('Evidence search failed:', err);
      setError(err.message || 'Evidence search failed. Verify network connectivity to NCBI and arXiv.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(initialQuery);
  }, [initialQuery]);

  return (
    <div className="space-y-6">
      {/* Swiss Editorial Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-2 border-black bg-white p-5 shadow-brutal">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-6 h-6 border border-black bg-swiss-yellow text-black font-mono text-xs font-black flex items-center justify-center shadow-[1px_1px_0px_#000]">
              08
            </span>
            <span className="font-mono text-xs font-black uppercase tracking-wider text-black">
              MODULE 08: RESEARCH EVIDENCE INTELLIGENCE
            </span>
          </div>
          <h1 className="text-2xl font-black uppercase tracking-tight text-black">
            Scientific Literature & Preprint Synthesis
          </h1>
          <p className="text-xs font-mono text-swiss-muted">
            REAL-TIME LITERATURE RETRIEVAL: PUBMED PEER-REVIEWED EVIDENCE + ARXIV COMPUTATIONAL PREPRINTS WITH DIRECT PDF ACCESS.
          </p>
        </div>

        <ProvenanceBadge
          type="hybrid"
          source="NCBI PubMed + arXiv Preprints"
          version="Live Literature API"
        />
      </div>

      {/* Search Input */}
      <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch(query);
          }}
          className="flex flex-col sm:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-black absolute left-3 top-3 pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="SEARCH PUBMED & ARXIV (E.G. EGFR T790M RESISTANCE, BCR-ABL1 ASCIMINIB)..."
              className="w-full pl-9 pr-3 py-2 border-2 border-black bg-white font-mono text-xs font-bold text-black focus:bg-swiss-bg outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2 border-2 border-black bg-swiss-yellow hover:bg-[#d4e400] text-black font-mono text-xs font-black uppercase shadow-brutal-sm cursor-pointer disabled:opacity-50 transition-all"
          >
            {loading ? <RotateCw className="w-4 h-4 animate-spin text-black" /> : <Search className="w-4 h-4 text-black" />}
            <span>RETRIEVE LITERATURE</span>
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 border-2 border-black bg-[#fee2e2] text-black font-mono text-xs flex items-center gap-2 shadow-brutal-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-black" />
          <div>
            <span className="font-black uppercase block">LITERATURE RETRIEVAL FAULT:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Results View */}
      {evidenceData && (
        <div className="space-y-6">
          {/* Summary Counts */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">QUERY TARGET</span>
              <span className="text-sm font-black text-black truncate block">{evidenceData.query}</span>
            </div>
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">PEER-REVIEWED PAPERS</span>
              <span className="text-xl font-black text-black">
                {evidenceData.experimental_sources_count} PubMed
              </span>
            </div>
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">PREPRINT PAPERS</span>
              <span className="text-xl font-black text-black">
                {evidenceData.computational_preprints_count} arXiv
              </span>
            </div>
            <div className="p-4 border-2 border-black bg-white shadow-brutal-sm">
              <span className="text-[10px] text-swiss-muted uppercase tracking-wider block font-bold">RETRIEVAL RUNTIME</span>
              <span className="text-xl font-black text-black">
                {evidenceData.execution_time_seconds?.toFixed(2)}s
              </span>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex flex-wrap items-center gap-2 border-b-2 border-black pb-2">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 border-2 border-black font-mono text-xs font-black uppercase transition-all cursor-pointer shadow-[1px_1px_0px_#000] ${
                activeTab === 'all'
                  ? 'bg-swiss-yellow text-black'
                  : 'bg-white hover:bg-swiss-panel text-black'
              }`}
            >
              All Evidence ({evidenceData.pubmed_evidence.length + evidenceData.arxiv_preprints.length})
            </button>
            <button
              onClick={() => setActiveTab('pubmed')}
              className={`px-3 py-1.5 border-2 border-black font-mono text-xs font-black uppercase transition-all cursor-pointer shadow-[1px_1px_0px_#000] ${
                activeTab === 'pubmed'
                  ? 'bg-swiss-yellow text-black'
                  : 'bg-white hover:bg-swiss-panel text-black'
              }`}
            >
              PubMed Peer-Reviewed ({evidenceData.pubmed_evidence.length})
            </button>
            <button
              onClick={() => setActiveTab('arxiv')}
              className={`px-3 py-1.5 border-2 border-black font-mono text-xs font-black uppercase transition-all cursor-pointer shadow-[1px_1px_0px_#000] ${
                activeTab === 'arxiv'
                  ? 'bg-swiss-yellow text-black'
                  : 'bg-white hover:bg-swiss-panel text-black'
              }`}
            >
              arXiv Preprints ({evidenceData.arxiv_preprints.length})
            </button>
          </div>

          {/* Articles Listing */}
          <div className="space-y-4">
            {/* PubMed Section */}
            {(activeTab === 'all' || activeTab === 'pubmed') && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-black">
                  <span className="font-black uppercase flex items-center gap-1.5">
                    <FlaskConical className="w-4 h-4 text-black" />
                    PUBMED PEER-REVIEWED BIOMEDICAL EVIDENCE
                  </span>
                  <ProvenanceBadge type="experimental" source="NLM PubMed" version="Medline" />
                </div>

                <div className="space-y-3">
                  {evidenceData.pubmed_evidence.map((article) => (
                    <div
                      key={article.pmid}
                      className="p-5 border-2 border-black bg-white space-y-2 hover:bg-swiss-panel transition-all shadow-brutal-sm font-mono"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-black pb-1.5">
                        <span className="text-[10px] font-mono font-black px-2 py-0.5 border border-black bg-swiss-yellow text-black">
                          PMID: {article.pmid}
                        </span>
                        <span className="text-[11px] font-bold text-swiss-muted">
                          {article.journal} • {article.pub_date}
                        </span>
                      </div>

                      <h3 className="text-sm font-black uppercase text-black leading-snug">
                        {article.title}
                      </h3>

                      {article.authors && (
                        <p className="text-[11px] text-swiss-muted font-bold">
                          AUTHORS: {article.authors.slice(0, 5).join(', ')}
                          {article.authors.length > 5 ? ' et al.' : ''}
                        </p>
                      )}

                      {article.abstract && (
                        <p className="text-xs text-black leading-relaxed line-clamp-3 bg-swiss-bg p-2.5 border border-black">
                          {article.abstract}
                        </p>
                      )}

                      <div className="flex items-center justify-between pt-2 border-t border-black text-xs">
                        <span className="text-swiss-muted font-bold text-[11px]">
                          DOI: {article.doi || 'N/A'}
                        </span>
                        <a
                          href={article.url || `https://pubmed.ncbi.nlm.nih.gov/${article.pmid}/`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 border border-black bg-white hover:bg-swiss-yellow text-black font-bold uppercase inline-flex items-center gap-1 shadow-[1px_1px_0px_#000]"
                        >
                          <span>OPEN PUBMED ARTICLE</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* arXiv Section */}
            {(activeTab === 'all' || activeTab === 'arxiv') && (
              <div className="space-y-3 pt-4">
                <div className="flex items-center justify-between text-xs font-mono text-black">
                  <span className="font-black uppercase flex items-center gap-1.5">
                    <Cpu className="w-4 h-4 text-black" />
                    ARXIV COMPUTATIONAL BIOLOGY & BIOPHYSICS PREPRINTS
                  </span>
                  <ProvenanceBadge type="computational" source="arXiv.org e-Print" version="Cornell University" />
                </div>

                <div className="space-y-3">
                  {evidenceData.arxiv_preprints.map((paper) => (
                    <div
                      key={paper.arxiv_id}
                      className="p-5 border-2 border-black bg-white space-y-2 hover:bg-swiss-panel transition-all shadow-brutal-sm font-mono"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-black pb-1.5">
                        <span className="text-[10px] font-mono font-black px-2 py-0.5 border border-black bg-swiss-panel text-black">
                          ARXIV: {paper.arxiv_id}
                        </span>
                        <span className="text-[11px] font-bold text-swiss-muted">
                          CATEGORY: {paper.primary_category || 'q-bio.BM'} • {paper.published?.split('T')[0]}
                        </span>
                      </div>

                      <h3 className="text-sm font-black uppercase text-black leading-snug">
                        {paper.title}
                      </h3>

                      {paper.authors && (
                        <p className="text-[11px] text-swiss-muted font-bold">
                          AUTHORS: {paper.authors.slice(0, 5).join(', ')}
                          {paper.authors.length > 5 ? ' et al.' : ''}
                        </p>
                      )}

                      {paper.summary && (
                        <p className="text-xs text-black leading-relaxed line-clamp-3 bg-swiss-bg p-2.5 border border-black">
                          {paper.summary}
                        </p>
                      )}

                      <div className="flex items-center justify-between pt-2 border-t border-black text-xs">
                        <span className="text-[10px] px-2 py-0.5 border border-black bg-[#fef08a] text-black font-black uppercase">
                          PREPRINT (NOT PEER-REVIEWED)
                        </span>
                        {paper.pdf_url && (
                          <a
                            href={paper.pdf_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2.5 py-1 border border-black bg-white hover:bg-swiss-yellow text-black font-bold uppercase inline-flex items-center gap-1 shadow-[1px_1px_0px_#000]"
                          >
                            <FileText className="w-3.5 h-3.5" />
                            <span>DOWNLOAD FULL PDF</span>
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ResearchEvidencePage() {
  return (
    <React.Suspense fallback={<div className="p-8 text-center text-xs text-black font-mono font-bold bg-white border-2 border-black shadow-brutal">INITIALIZING RESEARCH EVIDENCE...</div>}>
      <ResearchEvidenceContent />
    </React.Suspense>
  );
}
