'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { FileCode2, CheckCircle2 } from 'lucide-react';

export function IngestionScene() {
  const { ref, progress } = useScrollReveal(0.3);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const fadeOut = Math.max(0, 1 - (progress - 0.66) * 3);
  const sceneOpacity = Math.min(fadeIn, fadeOut);

  
  const steps = [
    'MIME PARSED',
    'HEADERS EXTRACTED',
    'BODY EXTRACTED',
    'LINKS EXTRACTED',
    'INDICATORS EXTRACTED'
  ];

  return (
    <section id="scene-03" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center md:justify-between px-4 md:px-24" style={{ opacity: sceneOpacity }}>
        
        {/* Narrative Left */}
        <div className="w-full md:w-1/3 mb-6 md:mb-0 text-center md:text-left">
          <h3 className="text-3xl font-bold mb-4">Ingestion</h3>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
            ThreatTrace AI analyzes the technical structure, parsing raw MIME data into structured forensic artifacts.
          </p>
        </div>

        {/* Visual Right */}
        <div className="w-full md:w-1/2 flex flex-col items-center">
          
          <div 
            className="w-full max-w-sm bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-6 shadow-2xl transition-all duration-500"
            style={{ opacity: Math.min(1, progress * 4) }}
          >
            <div className="flex items-center gap-4 mb-8 pb-6 border-b border-slate-200 dark:border-slate-800">
              <div className="w-12 h-12 bg-blue-950 rounded flex items-center justify-center text-blue-500">
                <FileCode2 className="w-6 h-6" />
              </div>
              <div>
                <div className="font-mono text-sm text-slate-700 dark:text-slate-300">suspicious-email.eml</div>
                <div className="text-xs text-slate-500">{tourData.incident.size} • ANALYZING...</div>
              </div>
            </div>

            <div className="space-y-4">
              {steps.map((step, idx) => {
                // Determine if this step is complete based on scroll progress
                const stepThreshold = 0.2 + (idx * 0.15);
                const isComplete = progress > stepThreshold;
                
                return (
                  <div 
                    key={step} 
                    className={`flex items-center gap-3 text-sm font-mono transition-all duration-300 ${
                      isComplete ? 'text-green-400' : 'text-slate-700'
                    }`}
                  >
                    <CheckCircle2 className={`w-4 h-4 ${isComplete ? 'opacity-100' : 'opacity-20'}`} />
                    {step}
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
