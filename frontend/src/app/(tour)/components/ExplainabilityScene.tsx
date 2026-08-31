'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';

export function ExplainabilityScene() {
  const { ref, progress } = useScrollReveal(0.4);
  const { incident } = tourData;

  const showOverlay = progress > 0.2;

  return (
    <section id="scene-05" className="relative min-h-[150vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center md:px-24">
        
        <div className="text-center mb-12">
          <h3 className="text-xl font-mono text-slate-500 tracking-widest mb-4">EXPLAINABILITY</h3>
          <h2 className="text-3xl md:text-4xl font-bold">WHY WAS THIS FLAGGED?</h2>
        </div>

        <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-center">
          
          {/* Mock Email Context */}
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 font-mono text-sm shadow-xl relative overflow-hidden">
            <div className="text-slate-500 mb-2">From:</div>
            <div className={`relative inline-block transition-colors duration-500 ${showOverlay ? 'text-red-400 bg-red-950/50' : 'text-slate-300'}`}>
              billing@paypa1-support.com
            </div>
            
            <div className="text-slate-500 mt-6 mb-2">Message Body:</div>
            <div className="text-slate-400 whitespace-pre-wrap">{incident.body.substring(0, 100)}...</div>
            
            <div className={`relative inline-block mt-4 transition-colors duration-500 ${showOverlay ? 'text-orange-400 bg-orange-950/50 px-2 py-1 rounded' : 'text-slate-300'}`}>
              {incident.url}
            </div>

            {/* Connecting lines overlay (simulated with CSS for performance) */}
            <div className={`absolute inset-0 pointer-events-none transition-opacity duration-700 ${showOverlay ? 'opacity-100' : 'opacity-0'}`}>
               <div className="absolute top-[4.5rem] right-0 w-16 border-t-2 border-red-500/50 border-dashed" />
               <div className="absolute bottom-[2.5rem] right-0 w-16 border-t-2 border-orange-500/50 border-dashed" />
            </div>
          </div>

          {/* Connected Explanations */}
          <div className="space-y-6 relative">
            <div 
              className={`p-4 border-l-2 border-red-500 bg-red-950/20 transition-all duration-700 delay-100 transform ${showOverlay ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'}`}
            >
              <div className="text-xs font-bold text-red-500 tracking-wider mb-1">LOOKALIKE DOMAIN</div>
              <div className="text-sm text-slate-300">
                The sender domain <span className="font-mono text-red-400">paypa1-support.com</span> is visually similar to a known brand, but registered 2 days ago.
              </div>
            </div>

            <div 
              className={`p-4 border-l-2 border-orange-500 bg-orange-950/20 transition-all duration-700 delay-300 transform ${showOverlay ? 'translate-x-0 opacity-100' : 'translate-x-8 opacity-0'}`}
            >
              <div className="text-xs font-bold text-orange-500 tracking-wider mb-1">SUSPICIOUS URL</div>
              <div className="text-sm text-slate-300">
                Link destination routes through a newly observed infrastructure cluster associated with credential harvesting.
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
