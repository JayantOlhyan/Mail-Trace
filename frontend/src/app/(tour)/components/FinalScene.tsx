'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import Link from 'next/link';
import { ArrowRight, Box } from 'lucide-react';

export function FinalScene() {
  const { ref, progress } = useScrollReveal(0.3);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const fadeOut = Math.max(0, 1 - (progress - 0.66) * 3);
  const sceneOpacity = fadeIn;


  const showContent = progress > 0.1;
  const showPipeline = progress > 0.4;
  const showButtons = progress > 0.7;

  return (
    <section id="scene-14" className="relative min-h-[250vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center px-4" style={{ opacity: sceneOpacity }}>
        
        <div className={`text-center transition-all duration-1000 transform ${showContent ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'}`}>
          <div className="text-sm font-mono text-blue-500 tracking-[0.3em] mb-6">THREATTRACE AI</div>
          
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            FROM SUSPICIOUS EMAIL
          </h2>
          <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent mb-16">
            TO FORENSIC INTELLIGENCE.
          </h2>

          {/* Pipeline Visualization */}
          <div className={`flex flex-wrap items-center justify-center gap-2 md:gap-4 mb-16 transition-all duration-1000 ${showPipeline ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
            {['DETECT', 'EXPLAIN', 'TRACE', 'CORRELATE', 'INVESTIGATE', 'PRESERVE', 'REPORT'].map((step, idx) => (
              <div key={step} className="flex items-center gap-2 md:gap-4">
                <div className="text-xs md:text-sm font-mono font-semibold text-slate-700 dark:text-slate-300 border border-slate-300 dark:border-slate-700 bg-slate-100/70 dark:bg-slate-900/50 px-3 py-1.5 rounded">
                  {step}
                </div>
                {idx < 6 && <ArrowRight className="w-4 h-4 text-slate-600" />}
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div className={`flex flex-col sm:flex-row items-center justify-center gap-6 transition-all duration-1000 delay-300 ${showButtons ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <Link 
              href="/workspace"
              className="bg-blue-600 hover:bg-blue-700 text-slate-900 dark:text-white font-medium px-8 py-3 rounded-full transition-colors w-full sm:w-auto"
            >
              OPEN WORKSPACE
            </Link>
            
            <a 
              href="https://github.com/jayantolhyan"
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-2 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:text-white border border-slate-300 dark:border-slate-700 hover:border-slate-500 bg-slate-100/70 dark:bg-slate-900/50 px-8 py-3 rounded-full transition-all w-full sm:w-auto"
            >
              <Box className="w-4 h-4 group-hover:scale-110 transition-transform" />
              VIEW ARCHITECTURE
            </a>
          </div>

        </div>

      </div>
    </section>
  );
}
