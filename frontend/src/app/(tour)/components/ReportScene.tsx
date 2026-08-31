'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';
import { FileText, Download } from 'lucide-react';

export function ReportScene() {
  const { ref, progress } = useScrollReveal(0.3);
  const { case: caseData, detection } = tourData;
  
  // Simulate report generation based on scroll progress
  const isGenerating = progress <= 0.4;

  const showReport = progress > 0.2;

  return (
    <section id="scene-13" className="relative min-h-[150vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center px-4 md:px-24">
        
        <div className={`w-full max-w-4xl bg-slate-100 text-slate-900 rounded-lg shadow-2xl overflow-hidden transition-all duration-700 transform ${showReport ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-16'}`}>
          
          {/* Header */}
          <div className="bg-slate-100 dark:bg-slate-900 text-slate-800 dark:text-slate-200 p-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-blue-400" />
              <div>
                <div className="font-mono text-xs tracking-widest text-slate-600 dark:text-slate-400">FORENSIC REPORT</div>
                <div className="font-bold">{caseData.id}</div>
              </div>
            </div>
            
            {isGenerating ? (
              <div className="flex items-center gap-2 text-blue-400 font-mono text-xs">
                <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                GENERATING...
              </div>
            ) : (
              <div className="flex items-center gap-2 text-green-400 font-mono text-xs">
                REPORT READY
              </div>
            )}
          </div>

          {/* Body */}
          <div className="p-8 relative min-h-[400px]">
            {isGenerating ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-100/80 backdrop-blur-sm z-10">
                <div className="space-y-4 w-64">
                  <div className="h-2 bg-slate-300 rounded overflow-hidden">
                    <div className="h-full bg-blue-500 w-1/3 animate-pulse" />
                  </div>
                  <div className="h-2 bg-slate-300 rounded overflow-hidden">
                    <div className="h-full bg-blue-500 w-2/3 animate-pulse delay-75" />
                  </div>
                  <div className="h-2 bg-slate-300 rounded overflow-hidden">
                    <div className="h-full bg-blue-500 w-1/2 animate-pulse delay-150" />
                  </div>
                </div>
              </div>
            ) : null}

            <div className={`transition-opacity duration-500 ${isGenerating ? 'opacity-20' : 'opacity-100'}`}>
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h4 className="font-bold text-slate-800 border-b border-slate-300 pb-2 mb-4">EXECUTIVE SUMMARY</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-3 rounded border border-slate-200 shadow-sm">
                      <div className="text-xs text-slate-500 font-mono">CLASSIFICATION</div>
                      <div className="font-bold text-red-600">{detection.classification}</div>
                    </div>
                    <div className="bg-white p-3 rounded border border-slate-200 shadow-sm">
                      <div className="text-xs text-slate-500 font-mono">RISK SCORE</div>
                      <div className="font-bold text-red-600">{detection.riskScore} / 100</div>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-bold text-slate-800 border-b border-slate-300 pb-2 mb-4">INVESTIGATION METRICS</h4>
                  <ul className="space-y-2 text-sm">
                    <li className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-600">Evidence Items</span>
                      <span className="font-bold font-mono">10 ITEMS</span>
                    </li>
                    <li className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-600">Infrastructure Clusters</span>
                      <span className="font-bold font-mono">2 CLUSTERS</span>
                    </li>
                    <li className="flex justify-between pb-1">
                      <span className="text-slate-600">Campaign Candidate</span>
                      <span className="font-bold font-mono">1 DETECTED</span>
                    </li>
                  </ul>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-4 pt-6 border-t border-slate-300">
                <button className="flex items-center gap-2 bg-slate-100 dark:bg-slate-900 text-slate-900 dark:text-white px-4 py-2 rounded text-sm font-medium hover:bg-slate-200 dark:bg-slate-800 transition-colors">
                  <Download className="w-4 h-4" /> EXPORT PDF
                </button>
                <button className="flex items-center gap-2 bg-white text-slate-700 border border-slate-300 px-4 py-2 rounded text-sm font-medium hover:bg-slate-50 transition-colors">
                  <Download className="w-4 h-4" /> EXPORT JSON
                </button>
                <button className="flex items-center gap-2 bg-white text-slate-700 border border-slate-300 px-4 py-2 rounded text-sm font-medium hover:bg-slate-50 transition-colors">
                  <Download className="w-4 h-4" /> EXPORT EVIDENCE PACKAGE
                </button>
              </div>
            </div>
          </div>
          
        </div>

      </div>
    </section>
  );
}
