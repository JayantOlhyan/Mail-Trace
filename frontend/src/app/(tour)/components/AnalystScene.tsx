'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { UserCheck, Bot } from 'lucide-react';

export function AnalystScene() {
  const { ref, progress } = useScrollReveal(0.4);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const fadeOut = Math.max(0, 1 - (progress - 0.66) * 3);
  const sceneOpacity = Math.min(fadeIn, fadeOut);

  const selectedVerdict: string | null = progress > 0.6 ? 'phishing' : null;

  return (
    <section id="scene-11" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center px-4" style={{ opacity: sceneOpacity }}>
        
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">AI ASSISTS. ANALYST DECIDES.</h2>
          <p className="text-slate-600 dark:text-slate-400 max-w-xl mx-auto">
            ThreatTrace AI provides the assessment, but human analysts retain final control over the verdict.
          </p>
        </div>

        <div className="w-full max-w-2xl grid md:grid-cols-2 gap-8">
          
          {/* AI Assessment */}
          <div className={`bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg p-6 transition-all duration-700 ${progress > 0.2 ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-8'}`}>
            <div className="flex items-center gap-3 mb-6 text-slate-600 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800 pb-4">
              <Bot className="w-5 h-5" />
              <span className="font-mono text-sm tracking-widest">AI ASSESSMENT</span>
            </div>
            
            <div className="text-center py-6">
              <div className="text-4xl font-bold text-red-500 mb-2">91 / 100</div>
              <div className="text-red-400 font-mono text-sm tracking-wider mb-2">PHISHING</div>
              <div className="text-xs text-slate-500">HIGH CONFIDENCE</div>
            </div>
          </div>

          {/* Analyst Review */}
          <div className={`bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg p-6 transition-all duration-700 delay-200 ${progress > 0.4 ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'}`}>
            <div className="flex items-center gap-3 mb-6 text-blue-400 border-b border-slate-200 dark:border-slate-800 pb-4">
              <UserCheck className="w-5 h-5" />
              <span className="font-mono text-sm tracking-widest text-slate-800 dark:text-slate-200">ANALYST REVIEW</span>
            </div>
            
            <div className="space-y-3">
              <button 
                className={`w-full p-3 rounded border text-left transition-all ${
                  selectedVerdict === 'phishing' 
                    ? 'bg-red-950 border-red-500 text-red-400' 
                    : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400'
                }`}
              >
                <div className="font-semibold text-sm">CONFIRMED PHISHING</div>
              </button>
              
              <button 
                className={`w-full p-3 rounded border text-left transition-all ${
                  selectedVerdict === 'bec' 
                    ? 'bg-orange-950 border-orange-500 text-orange-400' 
                    : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400'
                }`}
              >
                <div className="font-semibold text-sm">CONFIRMED BEC</div>
              </button>
              
              <button 
                className={`w-full p-3 rounded border text-left transition-all ${
                  selectedVerdict === 'fp' 
                    ? 'bg-green-950 border-green-500 text-green-400' 
                    : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400'
                }`}
              >
                <div className="font-semibold text-sm">FALSE POSITIVE</div>
              </button>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
