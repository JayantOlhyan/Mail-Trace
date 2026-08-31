'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { Mail } from 'lucide-react';

export function IncidentScene() {
  const { ref, progress } = useScrollReveal();

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const sceneOpacity = fadeIn;

  const { incident } = tourData;

  // For the first scene, we want it fully visible on load (no fade in).
  const opacity = Math.min(1, fadeIn);
  const separation = Math.max(0, progress * 2);

  return (
    <section id="scene-01" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center" style={{ opacity: sceneOpacity }}>
        <div 
          className="w-full max-w-2xl bg-slate-100/60 dark:bg-slate-900/40 backdrop-blur-2xl text-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700/50 rounded-2xl shadow-[0_0_40px_rgba(0,0,0,0.5)] overflow-hidden transition-all duration-700 ease-[cubic-bezier(0.16,1,0.3,1)]"
          style={{ opacity, transform: `scale(${1 - progress * 0.05})` }}
        >
          {/* Email Header */}
          <div className="bg-slate-200 dark:bg-slate-800/30 p-5 border-b border-slate-300 dark:border-slate-700/50 backdrop-blur-md">
            <div className="flex items-center gap-3 mb-2">
              <Mail className="w-5 h-5 text-slate-500" />
              <div className="font-semibold text-sm">New Message</div>
            </div>
            <div className="text-sm">
              <span className="text-slate-600 dark:text-slate-400 w-16 inline-block">From:</span>
              <span className="font-medium text-slate-900 dark:text-slate-100">{incident.from}</span>
            </div>
            <div className="text-sm">
              <span className="text-slate-600 dark:text-slate-400 w-16 inline-block">Subject:</span>
              <span className="font-bold text-slate-900 dark:text-slate-100">{incident.subject}</span>
            </div>
          </div>
          
          {/* Email Body */}
          <div className="p-8 text-sm relative leading-relaxed text-slate-700 dark:text-slate-300">
            <div className="mb-8">{incident.body.split('\n')[0]}</div>
            <div className="flex justify-center mb-8">
              <button className="bg-blue-600/90 hover:bg-blue-500 text-slate-900 dark:text-white px-8 py-3 rounded-md font-semibold tracking-wide shadow-[0_0_20px_rgba(37,99,235,0.3)] transition-all hover:scale-105 active:scale-95">
                VERIFY ACCOUNT
              </button>
            </div>
            <div>{incident.body.split('\n')[4]}</div>
            
            {/* Suspicious URL Overlay (reveals on scroll) */}
            <div 
              className="absolute inset-x-0 bottom-4 text-center transition-opacity duration-300"
              style={{ opacity: separation }}
            >
              <div className="inline-block bg-red-100 text-red-800 text-xs font-mono px-3 py-1 rounded border border-red-200">
                {incident.url}
              </div>
            </div>
          </div>
        </div>

        {/* Narrative Text */}
        <div 
          className="absolute bottom-24 text-center transition-opacity duration-500"
          style={{ opacity: separation > 0.8 ? 1 : 0 }}
        >
          <h2 className="text-2xl font-bold mb-2 tracking-tight">ONE EMAIL.</h2>
          <p className="text-slate-600 dark:text-slate-400 text-lg">MULTIPLE HIDDEN SIGNALS.</p>
        </div>
      </div>
    </section>
  );
}
