'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { Network, Info, X } from 'lucide-react';
import { useState } from 'react';

export function InvestigationGraphScene() {
  const { ref, progress } = useScrollReveal(0.2);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const sceneOpacity = fadeIn;

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // SVG Node positions (0 to 100 percentages)
  const nodes = [
    { id: 'email1', x: 50, y: 80, label: 'EMAIL', color: '#ef4444', showAt: 0.1, detail: 'Initial phishing email from billing@paypa1-support.com' },
    { id: 'domain', x: 30, y: 50, label: 'DOMAIN', color: '#3b82f6', showAt: 0.3, detail: 'Lookalike domain registered 2 days ago: paypa1-support.com' },
    { id: 'ip', x: 70, y: 50, label: 'IP', color: '#f59e0b', showAt: 0.4, detail: 'Relay server IP 203.0.113.42 in untrusted ASN range' },
    { id: 'email2', x: 20, y: 20, label: 'EMAIL 2', color: '#ef4444', showAt: 0.6, detail: 'Second target recipient in Finance Dept' },
    { id: 'email3', x: 80, y: 20, label: 'EMAIL 3', color: '#ef4444', showAt: 0.7, detail: 'Third target recipient in HR Dept' },
    { id: 'campaign', x: 50, y: 10, label: 'CAMPAIGN', color: '#8b5cf6', showAt: 0.9, detail: 'Correlated Campaign ID-8829 (Financial Phishing)' },
  ];

  const edges = [
    { source: 'email1', target: 'domain', showAt: 0.3 },
    { source: 'email1', target: 'ip', showAt: 0.4 },
    { source: 'domain', target: 'email2', showAt: 0.6 },
    { source: 'ip', target: 'email3', showAt: 0.7 },
    { source: 'email2', target: 'campaign', showAt: 0.9 },
    { source: 'email3', target: 'campaign', showAt: 0.9 },
  ];

  const activeNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <section id="scene-09" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center md:px-24" style={{ opacity: sceneOpacity }}>
        
        <div className="text-center mb-8 z-10">
          <h3 className="text-3xl font-bold flex items-center justify-center gap-3">
            <Network className="w-8 h-8 text-blue-500" />
            Investigation Graph
          </h3>
          <p className="text-slate-600 dark:text-slate-400 mt-4 max-w-xl mx-auto">
            ThreatTrace AI correlates isolated artifacts to reveal broader attack campaigns automatically. Click any node to inspect details.
          </p>
        </div>

        {/* Graph Container */}
        <div className="relative w-full max-w-4xl aspect-[4/3] bg-slate-50 dark:bg-slate-950/50 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          
          {/* SVG for Edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {edges.map((edge, idx) => {
              const sourceNode = nodes.find(n => n.id === edge.source)!;
              const targetNode = nodes.find(n => n.id === edge.target)!;
              const isVisible = progress > edge.showAt;

              return (
                <line
                  key={`edge-${idx}`}
                  x1={`${sourceNode.x}%`}
                  y1={`${sourceNode.y}%`}
                  x2={`${targetNode.x}%`}
                  y2={`${targetNode.y}%`}
                  stroke="#334155"
                  strokeWidth="2"
                  className={`transition-all duration-1000 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
                  strokeDasharray="4"
                />
              );
            })}
          </svg>

          {/* HTML Nodes */}
          {nodes.map((node) => {
            const isVisible = progress > node.showAt;
            const isSelected = selectedNodeId === node.id;
            
            return (
              <button
                key={node.id}
                onClick={() => setSelectedNodeId(isSelected ? null : node.id)}
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300 ease-out cursor-pointer ${
                  isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-50'
                }`}
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
              >
                <div 
                  className={`px-4 py-2 rounded-full border shadow-lg text-xs font-bold tracking-wider font-mono backdrop-blur-md transition-all ${
                    isSelected ? 'ring-2 ring-blue-400 scale-110' : 'hover:scale-105'
                  }`}
                  style={{ 
                    backgroundColor: `${node.color}20`,
                    borderColor: node.color,
                    color: node.color
                  }}
                >
                  {node.label}
                </div>
              </button>
            );
          })}

          {/* Node Pop-up Inspector Drawer */}
          {activeNode && (
            <div className="absolute bottom-4 right-4 max-w-sm bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-2xl z-20 font-mono text-xs text-slate-200">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-3">
                <span className="font-bold text-blue-400 flex items-center gap-1.5">
                  <Info className="w-4 h-4" /> {activeNode.label} INSPECTOR
                </span>
                <button
                  onClick={() => setSelectedNodeId(null)}
                  className="text-slate-400 hover:text-slate-100"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-slate-300 leading-relaxed font-sans text-xs mb-2">
                {activeNode.detail}
              </p>
              <div className="text-[10px] text-slate-500 font-mono">
                Click elsewhere or another node to switch inspector view.
              </div>
            </div>
          )}

        </div>
      </div>
    </section>
  );
}
