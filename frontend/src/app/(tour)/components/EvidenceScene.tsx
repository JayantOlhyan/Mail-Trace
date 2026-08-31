'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { Lock, FileCheck } from 'lucide-react';

export function EvidenceScene() {
  const { ref, progress } = useScrollReveal(0.3);
  const { case: caseData } = tourData;

  const showItems = progress > 0.2;
  const packagingProgress = Math.min(100, Math.max(0, (progress - 0.5) * 200)); // 0 to 100 between 0.5 and 1.0
  const isComplete = packagingProgress >= 100;

  return (
    <section id="scene-12" className="relative min-h-[150vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center md:justify-between px-4 md:px-24">
        
        {/* Narrative Left */}
        <div className="hidden md:block w-1/3">
          <h3 className="text-3xl font-bold mb-4">Evidence Preservation</h3>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            All artifacts, intelligence graphs, and analyst notes are cryptographically hashed and sealed into an integrity-verifiable evidence package.
          </p>
        </div>

        {/* Visual Right */}
        <div className="w-full md:w-1/2 flex flex-col items-center">
          <div className="w-full max-w-md bg-slate-100/60 dark:bg-slate-900/40 backdrop-blur-xl border border-slate-300 dark:border-slate-700/50 rounded-xl overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)] transition-colors duration-500">
            <div className="p-5 border-b border-slate-300 dark:border-slate-700/50 flex items-center justify-between bg-slate-200 dark:bg-slate-800/30">
              <div className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-emerald-400" />
                <span className="font-bold tracking-wide text-slate-900 dark:text-slate-100">Verifiable Evidence</span>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-950/50 px-2 py-1 rounded-full border border-emerald-800/50">SECURED</span>
            </div>
            
            <div className="p-6">
              <div className="flex items-center justify-between mb-6 border-b border-slate-300 dark:border-slate-700/50 pb-4">
                <div>
                  <div className="text-xs text-slate-600 dark:text-slate-400 font-mono tracking-widest mb-1">CASE ID</div>
                  <div className="font-mono text-lg text-slate-900 dark:text-slate-100">{caseData.id}</div>
                </div>
                <FileCheck className={`w-6 h-6 ${isComplete ? 'text-emerald-400' : 'text-slate-500'}`} />
              </div>

              {/* Evidence Items */}
              <div className="space-y-2 mb-8">
                {caseData.evidenceItems.map((item, idx) => {
                  const itemVisible = showItems && progress > (0.2 + idx * 0.03);
                  return (
                    <div 
                      key={idx}
                      className={`flex items-center gap-2 text-sm font-mono transition-all duration-300 transform ${itemVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'}`}
                    >
                      <span className="text-blue-500">✓</span>
                      <span className="text-slate-700 dark:text-slate-300">{item}</span>
                    </div>
                  );
                })}
              </div>

              {/* Packaging Progress */}
              <div className={`transition-all duration-500 ${progress > 0.4 ? 'opacity-100' : 'opacity-0'}`}>
                <div className="flex justify-between text-xs font-mono mb-2">
                  <span className="text-slate-600 dark:text-slate-400">{isComplete ? 'SEALED' : 'PRESERVING EVIDENCE...'}</span>
                  <span className={isComplete ? 'text-emerald-400 font-bold' : 'text-slate-700 dark:text-slate-300'}>{Math.floor(packagingProgress)}%</span>
                </div>
                <div className="w-full h-2 bg-slate-200 dark:bg-slate-800/50 rounded overflow-hidden border border-slate-300 dark:border-slate-700/50">
                  <div 
                    className={`h-full transition-all duration-100 ${isComplete ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-blue-500'}`} 
                    style={{ width: `${packagingProgress}%` }}
                  />
                </div>

                {/* SHA-256 Verified indicator */}
                <div className={`mt-4 flex items-center justify-center gap-2 p-2 bg-emerald-950/30 border border-emerald-900/50 rounded transition-all duration-500 transform ${isComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}>
                  <Lock className="w-4 h-4 text-emerald-500" />
                  <span className="text-xs font-mono text-emerald-400 tracking-wider">SHA-256 INTEGRITY VERIFIED</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
