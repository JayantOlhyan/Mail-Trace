'use client';

import { useEffect, useState } from 'react';

const SCENES = [
  { id: 'scene-01', label: 'Incident Signal', short: 'Incident' },
  { id: 'scene-02', label: 'Threat Intelligence', short: 'Overview' },
  { id: 'scene-03', label: 'MIME Ingestion', short: 'Ingestion' },
  { id: 'scene-04', label: 'Multi-Layer Detection', short: 'Detection' },
  { id: 'scene-05', label: 'Explainability & Scoring', short: 'Scoring' },
  { id: 'scene-06', label: 'Header Forensics', short: 'Headers' },
  { id: 'scene-07', label: 'SMTP Relay Trace', short: 'Relay' },
  { id: 'scene-08', label: 'Infrastructure Intelligence', short: 'Infra' },
  { id: 'scene-09', label: 'Investigation Graph', short: 'Graph' },
  { id: 'scene-10', label: 'Campaign Correlation', short: 'Campaign' },
  { id: 'scene-11', label: 'Analyst Workspace', short: 'SOC' },
  { id: 'scene-12', label: 'Evidence Preservation', short: 'Evidence' },
  { id: 'scene-13', label: 'Forensic Report', short: 'Report' },
  { id: 'scene-14', label: 'SOC Action Plan', short: 'Action' },
];

export function TourProgressNav() {
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + window.innerHeight / 3;
      
      let current = 0;
      for (let i = 0; i < SCENES.length; i++) {
        const el = document.getElementById(SCENES[i].id);
        if (el) {
          const top = el.offsetTop;
          if (scrollPosition >= top) {
            current = i;
          }
        }
      }
      setActiveIndex(current);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToScene = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const activeScene = SCENES[activeIndex];

  return (
    <>
      {/* Top Floating Badge with Current Step info */}
      <div className="fixed top-20 right-6 z-40 hidden sm:flex items-center gap-3 bg-slate-900/80 dark:bg-slate-950/80 backdrop-blur-xl border border-slate-700/60 text-white px-4 py-2 rounded-full shadow-2xl text-xs font-mono">
        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        <span className="text-slate-400">STEP {String(activeIndex + 1).padStart(2, '0')} / {SCENES.length}:</span>
        <span className="font-semibold text-blue-300">{activeScene.label}</span>
      </div>

      {/* Floating Right Dot Rail Navigation */}
      <div className="fixed right-4 top-1/2 -translate-y-1/2 z-40 hidden md:flex flex-col items-center gap-2 bg-slate-900/40 dark:bg-slate-950/40 backdrop-blur-md p-2 rounded-full border border-slate-700/40 shadow-xl">
        {SCENES.map((scene, idx) => {
          const isActive = idx === activeIndex;
          return (
            <button
              key={scene.id}
              onClick={() => scrollToScene(scene.id)}
              className="group relative flex items-center justify-center p-1 focus:outline-none"
              aria-label={`Jump to ${scene.label}`}
            >
              {/* Dot */}
              <span
                className={`transition-all duration-300 rounded-full ${
                  isActive
                    ? 'w-3 h-3 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)] scale-110'
                    : 'w-2 h-2 bg-slate-400/50 hover:bg-slate-300 hover:scale-125'
                }`}
              />

              {/* Hover Tooltip */}
              <span className="absolute right-8 px-2.5 py-1 bg-slate-900 text-slate-100 text-[11px] font-mono rounded shadow-lg opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap border border-slate-800">
                {scene.short}
              </span>
            </button>
          );
        })}
      </div>
    </>
  );
}
