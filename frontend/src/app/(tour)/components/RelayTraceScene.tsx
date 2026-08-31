'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { Server, ArrowDown } from 'lucide-react';
import { useState } from 'react';

export function RelayTraceScene() {
  const { ref, progress } = useScrollReveal(0.2);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const sceneOpacity = fadeIn;

  const { relay } = tourData;
  const [activeHop, setActiveHop] = useState<number | null>(null);

  return (
    <section id="scene-07" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center md:justify-between px-4 md:px-24" style={{ opacity: sceneOpacity }}>
        
        {/* Narrative Left */}
        <div className="hidden md:block w-1/3">
          <h3 className="text-3xl font-bold mb-4">Relay Trace</h3>
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
            ThreatTrace AI reconstructs the transmission path from raw headers.
          </p>
          <p className="text-xs font-mono text-slate-500 bg-slate-100/70 dark:bg-slate-900/50 p-3 border border-slate-200 dark:border-slate-800 rounded">
            Observed infrastructure does not establish the physical location or identity of an attacker.
          </p>
        </div>

        {/* Visual Right */}
        <div className="w-full md:w-1/2 flex flex-col items-center">
          
          <div className="flex flex-col items-center space-y-2">
            {relay.hops.map((hop, idx) => {
              const hopThreshold = 0.1 + (idx * 0.15);
              const isVisible = progress > hopThreshold;
              const isInteractable = hop.label === 'IP ADDRESS';

              return (
                <div key={idx} className="flex flex-col items-center w-full max-w-sm">
                  {/* The Hop Box */}
                  <button 
                    onClick={() => isInteractable ? setActiveHop(activeHop === idx ? null : idx) : undefined}
                    className={`w-full bg-slate-100 dark:bg-slate-900 border ${activeHop === idx ? 'border-blue-500' : 'border-slate-200 dark:border-slate-800'} ${isInteractable ? 'cursor-pointer hover:border-slate-400 dark:border-slate-600' : 'cursor-default'} rounded-lg p-4 flex items-center justify-between transition-all duration-500 transform ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-slate-50 dark:bg-slate-950 rounded flex items-center justify-center border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400">
                        <Server className="w-5 h-5" />
                      </div>
                      <div className="text-left">
                        <div className="text-xs font-bold text-slate-500 tracking-wider mb-1">{hop.label}</div>
                        <div className="text-sm font-mono text-slate-800 dark:text-slate-200">{hop.detail}</div>
                      </div>
                    </div>
                  </button>

                  {/* Infrastructure Details Panel (Collapsible) */}
                  {isInteractable && (
                    <div 
                      className={`w-full overflow-hidden transition-all duration-300 ${activeHop === idx ? 'max-h-64 mt-2 mb-4 opacity-100' : 'max-h-0 opacity-0'}`}
                    >
                      <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded p-4 text-xs font-mono text-slate-600 dark:text-slate-400 space-y-2">
                        <div className="grid grid-cols-2">
                          <span>ASN:</span><span className="text-slate-700 dark:text-slate-300">{relay.infrastructure.asn}</span>
                        </div>
                        <div className="grid grid-cols-2">
                          <span>NETWORK:</span><span className="text-slate-700 dark:text-slate-300">{relay.infrastructure.network}</span>
                        </div>
                        <div className="grid grid-cols-2">
                          <span>GEOLOCATION:</span><span className="text-slate-700 dark:text-slate-300">{relay.infrastructure.geolocation}</span>
                        </div>
                        <div className="grid grid-cols-2">
                          <span>CONFIDENCE:</span><span className="text-blue-400">{relay.infrastructure.confidence}</span>
                        </div>
                        <div className="mt-4 pt-2 border-t border-slate-200 dark:border-slate-800 text-slate-500 text-[10px]">
                          PROBABLE SENDING INFRASTRUCTURE
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Connecting Arrow */}
                  {idx < relay.hops.length - 1 && (
                    <div 
                      className={`py-2 text-slate-700 transition-all duration-500 delay-150 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
                    >
                      <ArrowDown className="w-5 h-5" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </section>
  );
}
