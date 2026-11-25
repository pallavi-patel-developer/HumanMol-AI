'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { scientificApi } from '@/lib/api';
import { HealthResponse } from '@/lib/types';
import { ArrowUpRight, RefreshCw, Bell, Sparkles, Activity } from 'lucide-react';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<string>('');

  const checkHealth = async () => {
    setLoading(true);
    try {
      const data = await scientificApi.getHealth();
      setHealth(data);
      setLastChecked(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Health check failed:', err);
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="border-b border-slate-200/80 bg-white sticky top-0 z-50 shadow-[0_1px_2px_rgba(0,0,0,0.03)]">
      {/* Top subtle micro metadata bar */}
      <div className="border-b border-slate-100 px-6 py-1 text-[11px] font-sans font-medium text-slate-500 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="font-semibold text-slate-700">SPEC-REF: HM-BIO-2026</span>
          <span className="hidden md:inline text-slate-400">•</span>
          <span className="hidden md:inline text-slate-500">SYSTEM: REINVENT4 // CHEMPROP // VINA // ADMETLAB</span>
          <span className="hidden lg:inline text-slate-400">•</span>
          <span className="hidden lg:inline text-slate-500">NODE: CIVILIAN TIER // 0.243</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs">
            <span className={`inline-block w-2 h-2 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`} />
            <span className="font-semibold text-slate-700">ENGINE CORE: {health?.status === 'healthy' ? 'ACTIVE' : 'STANDBY'}</span>
          </span>
          <span className="text-slate-300">|</span>
          <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full text-[10px] font-semibold">AUTH: ID-GX7</span>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="px-6 py-3 flex items-center justify-between gap-4">
        {/* Left: Brand Identity */}
        <div className="flex items-center gap-4">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold shadow-sm shadow-blue-500/20 group-hover:bg-blue-700 transition-colors">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">HUMANMOL</span>
                <span className="bg-blue-50 text-blue-700 border border-blue-200/60 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                  AI // NOVA-1
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Disease-to-Molecule Discovery Platform
              </p>
            </div>
          </Link>
        </div>

        {/* Center: System Status Metrics */}
        <div className="hidden lg:flex items-center gap-3">
          {/* FastAPI Engine Status */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200/70">
            <span className={`w-2 h-2 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-red-500'}`} />
            <div className="text-left">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">FASTAPI ENGINE</div>
              <div className="text-xs font-semibold text-slate-800">
                {health?.status === 'healthy' ? 'PORT 8000 // ONLINE' : 'PORT 8000 // OFFLINE'}
              </div>
            </div>
          </div>

          {/* Database Dialect */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200/70">
            <Activity className="w-3.5 h-3.5 text-slate-400" />
            <div className="text-left">
              <div className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">DATA PERSISTENCE</div>
              <div className="text-xs font-semibold text-slate-800">
                {health?.database?.active_backend === 'postgresql'
                  ? 'POSTGRESQL // 5432'
                  : 'SQLITE // HUMANMOL.DB'}
              </div>
            </div>
          </div>

          {/* Refresh Action */}
          <button
            onClick={checkHealth}
            disabled={loading}
            title={lastChecked ? `Checked: ${lastChecked}` : 'Refresh'}
            className="p-2 rounded-xl border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>

        {/* Right: API Spec, Notification Bell & User Avatar (matching reference UI) */}
        <div className="flex items-center gap-3">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-300 transition-all shadow-xs"
          >
            <span>API SPEC</span>
            <ArrowUpRight className="w-3.5 h-3.5 text-slate-400" />
          </a>

          {/* Notification Bell */}
          <button
            type="button"
            className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors relative cursor-pointer"
            title="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-600" />
          </button>

          {/* User Profile Avatar */}
          <div className="flex items-center gap-2 pl-1">
            <div className="w-9 h-9 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs ring-2 ring-slate-100 shadow-xs cursor-pointer select-none">
              HM
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
