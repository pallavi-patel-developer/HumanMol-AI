import type { Metadata } from 'next';
import './globals.css';
import { Header } from '@/components/common/Header';
import { Sidebar } from '@/components/common/Sidebar';
import { ScientificDisclaimer } from '@/components/common/ScientificDisclaimer';

export const metadata: Metadata = {
  title: 'HumanMol AI | Disease-to-Molecule Discovery & Biological Intelligence',
  description:
    'Comprehensive AI-driven computational biology and de novo molecular discovery platform integrating REINVENT4, Chemprop D-MPNN, AutoDock Vina, ADMETlab 3.0, UniProt, ChEMBL, and Reactome.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#F8FAFC] text-slate-900 font-sans min-h-screen flex flex-col antialiased selection:bg-blue-600 selection:text-white">
        {/* Top Modern SaaS Header */}
        <Header />

        {/* Main Application Layout */}
        <div className="flex flex-1 overflow-hidden relative">
          {/* Left Modern Sidebar */}
          <Sidebar />

          {/* Center Main Workspace */}
          <main className="flex-1 overflow-y-auto p-6 md:p-8 w-full space-y-8 bg-[#F8FAFC]">
            <div className="max-w-7xl mx-auto space-y-8">
              {children}
              <div className="pt-6 border-t border-slate-200/80">
                <ScientificDisclaimer />
              </div>
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
