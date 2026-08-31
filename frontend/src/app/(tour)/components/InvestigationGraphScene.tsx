'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { Network } from 'lucide-react';

export function InvestigationGraphScene() {
  const { ref, progress } = useScrollReveal(0.2);

  // SVG Node positions (0 to 100 percentages)
  const nodes = [
    { id: 'email1', x: 50, y: 80, label: 'EMAIL', color: '#ef4444', showAt: 0.1 },
    { id: 'domain', x: 30, y: 50, label: 'DOMAIN', color: '#3b82f6', showAt: 0.3 },
    { id: 'ip', x: 70, y: 50, label: 'IP', color: '#f59e0b', showAt: 0.4 },
    { id: 'email2', x: 20, y: 20, label: 'EMAIL 2', color: '#ef4444', showAt: 0.6 },
    { id: 'email3', x: 80, y: 20, label: 'EMAIL 3', color: '#ef4444', showAt: 0.7 },
    { id: 'campaign', x: 50, y: 10, label: 'CAMPAIGN', color: '#8b5cf6', showAt: 0.9 },
  ];

  const edges = [
    { source: 'email1', target: 'domain', showAt: 0.3 },
    { source: 'email1', target: 'ip', showAt: 0.4 },
    { source: 'domain', target: 'email2', showAt: 0.6 },
    { source: 'ip', target: 'email3', showAt: 0.7 },
    { source: 'email2', target: 'campaign', showAt: 0.9 },
    { source: 'email3', target: 'campaign', showAt: 0.9 },
  ];

  return (
    <section id="scene-09" className="relative min-h-[250vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center md:px-24">
        
        <div className="text-center mb-8 z-10">
          <h3 className="text-3xl font-bold flex items-center justify-center gap-3">
            <Network className="w-8 h-8 text-blue-500" />
            Investigation Graph
          </h3>
          <p className="text-slate-400 mt-4 max-w-xl mx-auto">
            ThreatTrace AI correlates isolated artifacts to reveal broader attack campaigns automatically.
          </p>
        </div>

        {/* Graph Container */}
        <div className="relative w-full max-w-4xl aspect-[4/3] bg-slate-950/50 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
          
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
            
            return (
              <div
                key={node.id}
                className={`absolute transform -translate-x-1/2 -translate-y-1/2 transition-all duration-700 ease-out ${
                  isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-50'
                }`}
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
              >
                <div 
                  className="px-4 py-2 rounded-full border shadow-lg text-xs font-bold tracking-wider font-mono backdrop-blur-md"
                  style={{ 
                    backgroundColor: `${node.color}20`, // 20% opacity hex
                    borderColor: node.color,
                    color: node.color
                  }}
                >
                  {node.label}
                </div>
              </div>
            );
          })}

        </div>
      </div>
    </section>
  );
}
