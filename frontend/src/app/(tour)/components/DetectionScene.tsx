'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { ShieldAlert } from 'lucide-react';

export function DetectionScene() {
  const { ref, progress } = useScrollReveal(0.3);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const sceneOpacity = fadeIn;

  const { detection } = tourData;

  // Derive score based on progress
  const scoreProgress = Math.max(0, Math.min(1, (progress - 0.2) / 0.6));
  const displayedScore = Math.floor(scoreProgress * detection.riskScore);

  return (
    <section id="scene-04" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center md:justify-between px-4 md:px-24" style={{ opacity: sceneOpacity }}>
        
        {/* Narrative Left */}
        <div className="w-full md:w-1/3 mb-6 md:mb-0 text-center md:text-left">
          <h3 className="text-3xl font-bold mb-4">Threat Detection</h3>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            Every signal is evaluated by the AI engine. As evidence mounts, the risk score dynamically increases, leading to a high-confidence classification.
          </p>
        </div>

        {/* Visual Right */}
        <div className="w-full md:w-1/2 flex flex-col items-center">
          
          <div className="w-full max-w-md">
            {/* Score Ring */}
            <div className="flex flex-col items-center mb-12">
              <div className="relative w-40 h-40 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
                  <circle 
                    cx="50" cy="50" r="45" 
                    fill="none" 
                    stroke={displayedScore > 70 ? '#ef4444' : displayedScore > 40 ? '#f59e0b' : '#3b82f6'} 
                    strokeWidth="8"
                    strokeDasharray="283"
                    strokeDashoffset={283 - (283 * displayedScore) / 100}
                    className="transition-all duration-300 ease-out"
                  />
                </svg>
                <div className="absolute flex flex-col items-center top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full z-10">
                  <span className="text-5xl font-black font-mono bg-gradient-to-br from-red-400 to-red-600 bg-clip-text text-transparent drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]">
                    {displayedScore}
                  </span>
                  <span className="text-[10px] text-red-400 font-bold uppercase tracking-[0.2em] mt-1 drop-shadow-sm">
                    Risk
                  </span>
                </div>
              </div>
              
              <div 
                className={`mt-6 flex items-center gap-2 px-4 py-1.5 rounded-full border transition-all duration-500 ${
                  progress > 0.8 ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'opacity-0 scale-95'
                }`}
              >
                <ShieldAlert className="w-4 h-4" />
                <span className="text-sm font-semibold tracking-wider">{detection.classification}</span>
              </div>
            </div>

            {/* Signals List */}
            <div className="space-y-3">
              {detection.signals.map((signal, idx) => {
                const signalThreshold = 0.2 + (idx * 0.1);
                const isVisible = progress > signalThreshold;
                
                return (
                  <div 
                    key={signal.id}
                    className={`flex items-center justify-between p-3 rounded bg-slate-100/70 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 transition-all duration-500 transform ${
                      isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'
                    }`}
                  >
                    <span className="text-xs font-mono text-slate-600 dark:text-slate-400">{signal.label}</span>
                    <span className="text-sm font-medium text-slate-800 dark:text-slate-200">{signal.evidence}</span>
                  </div>
                );
              })}
            </div>
          </div>
          
        </div>
      </div>
    </section>
  );
}
