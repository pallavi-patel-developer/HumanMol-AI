'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, ChevronDown, Sparkles } from 'lucide-react';

interface NavItem {
  id: string;
  name: string;
  href: string;
  code: string;
  tag?: string;
}

const navSections: { title: string; items: NavItem[] }[] = [
  {
    title: 'OVERVIEW',
    items: [
      { id: '00', name: 'EXECUTIVE DASHBOARD', href: '/', code: 'DASH' },
    ],
  },
  {
    title: 'BIOLOGICAL TARGETING',
    items: [
      { id: '01', name: 'DISEASE INTELLIGENCE', href: '/disease-intelligence', code: 'DIS-01', tag: 'ICD-11' },
      { id: '02', name: 'TARGET DISCOVERY', href: '/targets', code: 'TGT-02', tag: 'UNIPROT' },
      { id: '02B', name: 'BIOACTIVITY INTEL', href: '/bioactivity', code: 'BIO-02B', tag: 'WET-LAB EXP' },
    ],
  },
  {
    title: 'COMPUTATIONAL ENGINES',
    items: [
      { id: '03', name: 'MOLECULE GENERATION', href: '/generation', code: 'GEN-03', tag: 'REINVENT4' },
      { id: '04', name: 'MOLECULAR PROPERTIES', href: '/properties', code: 'PRP-04', tag: 'CHEMPROP' },
      { id: '05', name: 'MOLECULAR DOCKING', href: '/docking', code: 'DCK-05', tag: 'VINA 3D' },
      { id: '06', name: 'ADMET & TOXICITY', href: '/admet', code: 'TOX-06', tag: '119 ENDPOINTS' },
      { id: '07', name: 'CELLULAR RESPONSE', href: '/cellular-response', code: 'CEL-07', tag: 'XPERT CPU' },
    ],
  },
  {
    title: 'DECISION & REPORTS',
    items: [
      { id: '08', name: 'RESEARCH EVIDENCE', href: '/research-evidence', code: 'EVD-08', tag: 'PUBMED' },
      { id: '09', name: 'CANDIDATE EXPLORER', href: '/candidates', code: 'CMP-09', tag: 'MPO RANK' },
      { id: '10', name: 'RESEARCH REPORTS', href: '/reports', code: 'RPT-10', tag: 'DOSSIER' },
    ],
  },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <aside className="w-64 md:w-72 border-r border-slate-200/80 bg-white min-h-[calc(100vh-77px)] flex flex-col justify-between flex-shrink-0 select-none">
      <div className="p-4 space-y-4">
        {/* Search Input Box (Valora Reference Style) */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search modules..."
            className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-slate-700 placeholder-slate-400 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all outline-none"
          />
        </div>

        {/* Navigation Sections */}
        <div className="space-y-4">
          {navSections.map((section, sIdx) => {
            const filteredItems = section.items.filter((item) =>
              item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
              item.code.toLowerCase().includes(searchQuery.toLowerCase())
            );

            if (filteredItems.length === 0) return null;

            return (
              <div key={sIdx} className="space-y-1">
                <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 tracking-wider px-3 mb-1">
                  <span>{section.title}</span>
                  <span className="text-[10px] text-slate-300">{filteredItems.length}</span>
                </div>
                <nav className="space-y-0.5">
                  {filteredItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={`flex items-center justify-between px-3 py-2 rounded-xl transition-all text-xs ${
                          isActive
                            ? 'bg-blue-50 text-blue-600 font-semibold shadow-xs'
                            : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-medium'
                        }`}
                      >
                        <div className="flex items-center gap-2.5 min-w-0">
                          <span className={`text-[11px] font-mono font-bold ${isActive ? 'text-blue-600' : 'text-slate-400'}`}>
                            {item.id}
                          </span>
                          <span className="truncate text-xs tracking-tight">
                            {item.name}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          {item.tag && (
                            <span
                              className={`text-[9px] font-semibold px-2 py-0.5 rounded-full ${
                                isActive
                                  ? 'bg-blue-100 text-blue-700'
                                  : 'bg-slate-100 text-slate-500'
                              }`}
                            >
                              {item.tag}
                            </span>
                          )}
                        </div>
                      </Link>
                    );
                  })}
                </nav>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Technical Spec & Pass Tier */}
      <div className="border-t border-slate-100 bg-white p-4 space-y-3">
        <div className="rounded-xl p-3 bg-slate-50 border border-slate-200/60 text-xs space-y-1.5">
          <div className="flex items-center justify-between font-semibold text-slate-800">
            <span className="text-[11px] tracking-wide text-slate-600">PASS TIER // CLEARANCE</span>
            <span className="bg-blue-50 text-blue-700 border border-blue-200/60 px-2 py-0.5 rounded-full text-[10px] font-bold">
              ID-GX7
            </span>
          </div>
          <div className="text-[11px] text-slate-500 leading-snug">
            HUMANMOL FULL RESEARCH SUITE
            <br />
            ORBITRA-5 // ACCESS NODE: CIVILIAN
          </div>
        </div>

        <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium px-1">
          <span>MEASURE: 0.243</span>
          <span>BUILD: v1.0.0-PROD</span>
        </div>
      </div>
    </aside>
  );
};
