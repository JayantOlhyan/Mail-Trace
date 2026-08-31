'use client';

import { SCENES } from './TourNavigation';

interface Props {
  activeIndex: number;
  onSelect: (index: number) => void;
}

export function TourProgressNav({ activeIndex, onSelect }: Props) {
  const activeScene = SCENES[activeIndex];

  if (!activeScene) return null;

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
              onClick={() => onSelect(idx)}
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
