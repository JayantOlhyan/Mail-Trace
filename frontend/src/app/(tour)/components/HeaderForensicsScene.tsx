'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { Code2 } from 'lucide-react';

export function HeaderForensicsScene() {
  const { ref, progress } = useScrollReveal(0.3);
  const { headers } = tourData;

  const showParsed = progress > 0.4;
  const showAnalyzed = progress > 0.7;

  return (
    <section id="scene-06" className="relative min-h-[200vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center flex-col px-4 md:px-24">
        
        <div className="text-center mb-12">
          <h3 className="text-xl font-mono text-slate-500 tracking-widest mb-4">HEADER FORENSICS</h3>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Technical evidence hidden in SMTP headers is extracted, normalized, and analyzed for authentication failures.
          </p>
        </div>

        <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 items-stretch">
          
          {/* Raw Headers */}
          <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-xs overflow-hidden shadow-2xl flex flex-col">
            <div className="flex items-center gap-2 mb-4 text-slate-500 border-b border-slate-800 pb-2">
              <Code2 className="w-4 h-4" />
              RAW HEADERS
            </div>
            <div className="text-slate-400 whitespace-pre-wrap leading-relaxed opacity-60">
              {headers.raw}
            </div>
          </div>

          {/* Transformation Stages */}
          <div className="flex flex-col justify-center gap-8">
            
            {/* Parsed & Normalized */}
            <div 
              className={`bg-slate-900 border border-slate-700 rounded-lg p-6 transition-all duration-700 transform ${showParsed ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
            >
              <div className="text-xs font-mono text-slate-500 tracking-wider mb-4 border-b border-slate-800 pb-2">
                NORMALIZED DATA
              </div>
              <div className="space-y-2 font-mono text-sm">
                <div className="grid grid-cols-[100px_1fr] text-slate-300">
                  <span className="text-slate-500">Sender IP:</span>
                  <span>203.0.113.42</span>
                </div>
                <div className="grid grid-cols-[100px_1fr] text-slate-300">
                  <span className="text-slate-500">Return-Path:</span>
                  <span>billing@paypa1-support.com</span>
                </div>
                <div className="grid grid-cols-[100px_1fr] text-slate-300">
                  <span className="text-slate-500">Auth-Results:</span>
                  <span>Extracted</span>
                </div>
              </div>
            </div>

            {/* Analyzed Auth */}
            <div 
              className={`bg-slate-900 border border-slate-700 rounded-lg p-6 transition-all duration-700 delay-150 transform ${showAnalyzed ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
            >
              <div className="text-xs font-mono text-slate-500 tracking-wider mb-4 border-b border-slate-800 pb-2">
                AUTHENTICATION ANALYSIS
              </div>
              <div className="space-y-3">
                {headers.parsed.map((auth, idx) => (
                  <div key={idx} className="flex items-center justify-between bg-red-950/20 border border-red-900/30 p-2 rounded">
                    <div className="flex items-center gap-3">
                      <span className="text-red-500 font-bold font-mono text-xs w-10">{auth.key}</span>
                      <span className="text-slate-400 text-xs">{auth.detail}</span>
                    </div>
                    <span className="text-red-400 font-mono text-xs font-semibold px-2 py-0.5 bg-red-950 rounded">
                      {auth.result}
                    </span>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>
      </div>
    </section>
  );
}
