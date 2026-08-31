'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';

export function ProductRevealScene() {
  const { ref, progress } = useScrollReveal();
  
  const textOpacity = Math.min(1, progress * 2);
  const translateY = Math.max(0, 50 - progress * 100);
  
  return (
    <section id="scene-02" className="relative min-h-[150vh]" ref={ref}>
      <div 
        className="sticky top-0 flex h-screen flex-col items-center justify-center text-center px-4 transition-all duration-700"
        style={{ 
          opacity: textOpacity,
          transform: `translateY(${translateY}px)`
        }}
      >
        <h2 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-r from-white via-slate-200 to-slate-500 bg-clip-text text-transparent drop-shadow-sm leading-tight">
          AI-POWERED THREAT DETECTION <br className="hidden md:block"/>
          & FORENSIC INTELLIGENCE
        </h2>
        <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto mb-16 font-light">
          Turn suspicious email into actionable forensic intelligence.
        </p>
        
        <div className="inline-flex items-center justify-center px-8 py-3 text-sm font-medium text-white transition-all duration-300 border border-slate-700/50 bg-slate-800/30 backdrop-blur-md rounded-full hover:bg-slate-700/50 hover:border-slate-500 hover:shadow-[0_0_20px_rgba(255,255,255,0.05)]">
          EXPLORE THE INVESTIGATION ↓
        </div>
      </div>
    </section>
  );
}
