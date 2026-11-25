'use client';

import React, { useEffect, useRef, useState } from 'react';
import { RotateCw, ZoomIn, Eye, AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  pdbId?: string;
  pdbUrl?: string;
  pdbqtContent?: string;
  title?: string;
  height?: string;
  initialStyle?: 'cartoon' | 'stick' | 'sphere';
}

declare global {
  interface Window {
    $3Dmol?: any;
  }
}

export const MoleculeViewer3D: React.FC<Props> = ({
  pdbId = '2ITZ',
  pdbUrl,
  pdbqtContent,
  title,
  height = '420px',
  initialStyle = 'cartoon',
}) => {
  // Dedicated unmanaged container for 3Dmol WebGL canvas.
  // Crucial: Must contain ZERO React children so 3Dmol never clobbers React VDOM nodes.
  const canvasHostRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStyle, setCurrentStyle] = useState<'cartoon' | 'stick' | 'sphere'>(initialStyle);
  const [isSpinning, setIsSpinning] = useState(false);
  const [surfaceActive, setSurfaceActive] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const abortController = new AbortController();

    const load3Dmol = async () => {
      if (typeof window === 'undefined') return;

      if (!window.$3Dmol) {
        const existingScript = document.getElementById('3dmol-script');
        if (!existingScript) {
          const script = document.createElement('script');
          script.id = '3dmol-script';
          script.src = 'https://3Dmol.org/build/3Dmol-min.js';
          script.async = true;
          document.head.appendChild(script);

          await new Promise<void>((resolve, reject) => {
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load 3Dmol.js molecular visualization library'));
          });
        } else {
          await new Promise<void>((resolve) => {
            const check = setInterval(() => {
              if (window.$3Dmol) {
                clearInterval(check);
                resolve();
              }
            }, 100);
          });
        }
      }

      if (isMounted) {
        initViewer(() => isMounted, abortController.signal);
      }
    };

    load3Dmol().catch((err) => {
      if (isMounted) {
        setError(err.message);
        setLoading(false);
      }
    });

    return () => {
      isMounted = false;
      abortController.abort();
      if (viewerRef.current) {
        try {
          viewerRef.current.spin(false);
          viewerRef.current.clear();
        } catch (e) {
          // ignore cleanup errors
        }
        viewerRef.current = null;
      }
      if (canvasHostRef.current) {
        canvasHostRef.current.innerHTML = '';
      }
    };
  }, [pdbId, pdbUrl, pdbqtContent]);

  const handleRetry = () => {
    const controller = new AbortController();
    initViewer(() => true, controller.signal);
  };

  const initViewer = async (isMountedCheck: () => boolean, signal: AbortSignal) => {
    if (!canvasHostRef.current || !window.$3Dmol) return;
    setLoading(true);
    setError(null);

    try {
      if (viewerRef.current) {
        try {
          viewerRef.current.spin(false);
          viewerRef.current.clear();
        } catch (e) {}
        viewerRef.current = null;
      }

      if (!isMountedCheck() || !canvasHostRef.current) return;
      canvasHostRef.current.innerHTML = '';
      const config = { backgroundColor: '#0a0e11' };
      const viewer = window.$3Dmol.createViewer(canvasHostRef.current, config);
      viewerRef.current = viewer;

      let receptorLoaded = false;
      const targetUrl = pdbUrl || (pdbId ? `https://files.rcsb.org/download/${pdbId}.pdb` : undefined);
      if (targetUrl) {
        try {
          const resp = await fetch(targetUrl, { signal });
          if (resp.ok && isMountedCheck() && viewerRef.current === viewer) {
            const data = await resp.text();
            if (data && data.includes('ATOM')) {
              viewer.addModel(data, 'pdb');
              applyStyle(viewer, currentStyle);
              receptorLoaded = true;
            }
          }
        } catch {
          // Non-fatal if offline or aborted: fallback to ligand alone
        }
      }

      if (!isMountedCheck() || viewerRef.current !== viewer) return;

      if (pdbqtContent && pdbqtContent.includes('ATOM')) {
        viewer.addModel(pdbqtContent, 'pdbqt');
        // Render ligand conformer in high-contrast cyan sticks
        viewer.setStyle({ resn: 'UNL' }, { stick: { colorscheme: 'cyanCarbon', radius: 0.22 } });
        if (!receptorLoaded) {
          viewer.setStyle({}, { stick: { colorscheme: 'cyanCarbon' } });
        }
      } else if (!receptorLoaded && targetUrl) {
        throw new Error(`Failed to download structure (${pdbId})`);
      }

      if (isMountedCheck() && viewerRef.current === viewer) {
        try {
          viewer.zoomTo();
          viewer.render();
        } catch (renderErr) {
          console.warn('3Dmol render safely caught:', renderErr);
        }
      }
      if (isMountedCheck()) {
        setLoading(false);
      }
    } catch (err: any) {
      if (!isMountedCheck()) return;
      console.error('Error rendering 3D molecule:', err);
      setError(err.message || 'Failed to render 3D molecular structure');
      setLoading(false);
    }
  };

  const applyStyle = (viewer: any, style: 'cartoon' | 'stick' | 'sphere') => {
    if (!viewer) return;
    if (style === 'cartoon') {
      viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
      viewer.setStyle({ hetflag: true }, { stick: { colorscheme: 'greenCarbon' } });
    } else if (style === 'stick') {
      viewer.setStyle({}, { stick: { colorscheme: 'amino' } });
    } else if (style === 'sphere') {
      viewer.setStyle({}, { sphere: { scale: 0.8, colorscheme: 'spectrum' } });
    }
  };

  const handleStyleChange = (style: 'cartoon' | 'stick' | 'sphere') => {
    setCurrentStyle(style);
    if (viewerRef.current) {
      applyStyle(viewerRef.current, style);
      viewerRef.current.render();
    }
  };

  const toggleSpin = () => {
    if (!viewerRef.current) return;
    if (!isSpinning) {
      viewerRef.current.spin('y', 1);
      setIsSpinning(true);
    } else {
      viewerRef.current.spin(false);
      setIsSpinning(false);
    }
  };

  const toggleSurface = () => {
    if (!viewerRef.current) return;
    if (!surfaceActive) {
      viewerRef.current.addSurface(window.$3Dmol.SurfaceType.VDW, {
        opacity: 0.65,
        color: 'white',
      });
      setSurfaceActive(true);
    } else {
      viewerRef.current.removeAllSurfaces();
      setSurfaceActive(false);
    }
    viewerRef.current.render();
  };

  const resetView = () => {
    if (viewerRef.current) {
      viewerRef.current.zoomTo();
      viewerRef.current.render();
    }
  };

  return (
    <div className="relative rounded-2xl border border-slate-200/80 bg-white shadow-sm overflow-hidden">
      {/* Modern Instrument Top Header */}
      <div className="flex flex-wrap items-center justify-between px-4 py-3 bg-slate-50/80 border-b border-slate-200/80 gap-2">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-lg bg-blue-50 border border-blue-200/60 flex items-center justify-center text-[10px] font-bold text-blue-600">
            3D
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-800">
            {title || `STRUCTURE_RENDER // ${pdbId}`}
          </span>
          <span className="rounded-full bg-slate-100 border border-slate-200 px-2 py-0.5 text-[10px] font-semibold text-slate-600 uppercase">
            WEBGL // 0.243
          </span>
        </div>

        {/* Modern Toolbar Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => handleStyleChange('cartoon')}
            className={`px-2.5 py-1 rounded-lg border text-xs font-semibold transition-all shadow-xs cursor-pointer ${
              currentStyle === 'cartoon'
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
            }`}
          >
            Cartoon
          </button>
          <button
            onClick={() => handleStyleChange('stick')}
            className={`px-2.5 py-1 rounded-lg border text-xs font-semibold transition-all shadow-xs cursor-pointer ${
              currentStyle === 'stick'
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
            }`}
          >
            Sticks
          </button>
          <button
            onClick={() => handleStyleChange('sphere')}
            className={`px-2.5 py-1 rounded-lg border text-xs font-semibold transition-all shadow-xs cursor-pointer ${
              currentStyle === 'sphere'
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
            }`}
          >
            Spheres
          </button>
          <button
            onClick={toggleSurface}
            className={`px-2.5 py-1 rounded-lg border text-xs font-semibold transition-all shadow-xs cursor-pointer ${
              surfaceActive
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
            }`}
          >
            Surface
          </button>
          <button
            onClick={toggleSpin}
            className={`p-1.5 rounded-lg border text-xs font-semibold transition-all shadow-xs cursor-pointer ${
              isSpinning ? 'bg-blue-600 text-white border-blue-600' : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
            }`}
            title="Auto-rotate 360°"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isSpinning ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={resetView}
            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition-all cursor-pointer"
            title="Reset View"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 3D WebGL Canvas Container */}
      <div
        style={{ height }}
        className="w-full relative flex items-center justify-center bg-[#0a0e11] overflow-hidden"
      >
        {/* Dedicated Unmanaged 3Dmol Canvas Mounting Element (ZERO React children) */}
        <div ref={canvasHostRef} className="w-full h-full relative" />

        {/* Static Non-DOM overlays managed purely by React */}
        <div className="absolute top-2 left-2 text-[10px] font-mono text-cyan-500/50 pointer-events-none select-none z-10">
          + [X:0 Y:0]
        </div>
        <div className="absolute bottom-2 right-2 text-[10px] font-mono text-cyan-500/50 pointer-events-none select-none z-10">
          + [FOV:45°]
        </div>

        {/* Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-[#0a0e11]/90 z-20 text-white pointer-events-none">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-white">
              INITIALIZING WEBGL // FETCHING ATOMIC COORDINATES...
            </span>
          </div>
        )}

        {/* Error Overlay */}
        {error && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 p-6 text-center bg-[#0a0e11]/95 z-20">
            <AlertCircle className="w-8 h-8 text-rose-500" />
            <p className="text-xs font-bold uppercase text-rose-400">STRUCTURE VISUALIZATION FAULT</p>
            <p className="text-xs text-slate-300 max-w-md">{error}</p>
            <button
              onClick={handleRetry}
              className="mt-2 px-3 py-1.5 rounded-xl border border-slate-600 bg-slate-900 hover:bg-slate-800 text-xs font-semibold text-white transition-all shadow-xs cursor-pointer"
            >
              RETRY RENDER
            </button>
          </div>
        )}
      </div>

      {/* Modern Bottom Technical Legend */}
      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200/80 text-[11px] text-slate-600 flex flex-wrap items-center justify-between gap-2">
        <span className="font-medium">
          INTERACTIONS: LEFT-CLICK + DRAG TO ROTATE • RIGHT-CLICK TO PAN • WHEEL TO ZOOM
        </span>
        <span className="rounded-full bg-slate-900 text-white px-2.5 py-0.5 font-bold uppercase text-[10px]">
          PDB: {pdbId}
        </span>
      </div>
    </div>
  );
};
