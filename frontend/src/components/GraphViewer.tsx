'use client';

import React, { useState } from 'react';
import { InvestigationGraph, GraphNode, GraphEdge } from '@/types';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  SlidersHorizontal,
  Mail,
  Server,
  Globe,
  Link as LinkIcon,
  Shield,
  Layers,
  Info,
  X,
} from 'lucide-react';

interface GraphViewerProps {
  graph: InvestigationGraph;
}

export function GraphViewer({ graph }: GraphViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [depth, setDepth] = useState(2);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<GraphEdge | null>(null);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'EMAIL':
        return <Mail className="w-4 h-4 text-indigo-400" />;
      case 'SENDER':
        return <Mail className="w-4 h-4 text-amber-400" />;
      case 'DOMAIN':
        return <Globe className="w-4 h-4 text-cyan-400" />;
      case 'IP':
        return <Server className="w-4 h-4 text-red-400" />;
      case 'ASN':
        return <Layers className="w-4 h-4 text-purple-400" />;
      case 'URL':
        return <LinkIcon className="w-4 h-4 text-emerald-400" />;
      default:
        return <Shield className="w-4 h-4 text-slate-400" />;
    }
  };

  const resetView = () => {
    setZoom(1);
    setSelectedNode(null);
    setSelectedEdge(null);
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden relative flex flex-col h-[520px]">
      {/* Control Bar */}
      <div className="p-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between z-10 select-none">
        <div className="flex items-center space-x-3">
          <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
            <Shield className="w-4 h-4 text-indigo-400" />
            Bounded Investigation Graph (Depth: {depth})
          </h3>
        </div>

        <div className="flex items-center space-x-2">
          {/* Depth Selector */}
          <div className="flex items-center space-x-1 bg-slate-950 px-2 py-1 rounded border border-slate-800 text-xs text-slate-300">
            <SlidersHorizontal className="w-3.5 h-3.5 text-slate-400" />
            <span>Depth:</span>
            {[1, 2, 3].map((d) => (
              <button
                key={d}
                onClick={() => setDepth(d)}
                className={`px-1.5 py-0.5 rounded font-mono ${
                  depth === d ? 'bg-indigo-600 text-white font-bold' : 'hover:bg-slate-800 text-slate-400'
                }`}
              >
                {d}
              </button>
            ))}
          </div>

          {/* Zoom buttons */}
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.2, 2))}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.2, 0.6))}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={resetView}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Canvas Area */}
      <div className="flex-1 bg-slate-950/90 relative overflow-hidden flex items-center justify-center p-8">
        {/* SVG Graph Layout Simulation with Radial Connecting Lines (Approach H Panel 3) */}
        <div
          className="transition-transform duration-200 relative w-full h-full flex items-center justify-center"
          style={{ transform: `scale(${zoom})` }}
        >
          {/* SVG Connecting Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-80">
            {graph.nodes.map((node, index) => {
              const total = Math.max(1, graph.nodes.length);
              const angle = (index / total) * 2 * Math.PI;
              const cx = 50 + 36 * Math.cos(angle);
              const cy = 50 + 34 * Math.sin(angle);
              const isSelected = selectedNode?.id === node.id;
              return (
                <g key={`edge-g-${node.id}`}>
                  <line
                    x1="50%"
                    y1="50%"
                    x2={`${cx}%`}
                    y2={`${cy}%`}
                    stroke={isSelected ? '#ef4444' : node.node_type === 'EMAIL' ? '#ef4444' : '#38bdf8'}
                    strokeWidth={isSelected ? '2.5' : '1.5'}
                    strokeDasharray="4 3"
                  />
                </g>
              );
            })}
          </svg>

          <div className="relative w-full h-full max-w-2xl max-h-[380px]">
            {graph.nodes.map((node, index) => {
              const isSelected = selectedNode?.id === node.id;
              const total = Math.max(1, graph.nodes.length);
              const angle = (index / total) * 2 * Math.PI;
              const isCenter = node.node_type === 'EMAIL';
              const leftPercent = isCenter ? 50 : 50 + 36 * Math.cos(angle);
              const topPercent = isCenter ? 50 : 50 + 34 * Math.sin(angle);

              return (
                <div
                  key={node.id}
                  onClick={() => {
                    setSelectedNode(node);
                    setSelectedEdge(null);
                  }}
                  style={{
                    left: `${leftPercent}%`,
                    top: `${topPercent}%`,
                  }}
                  className={`absolute -translate-x-1/2 -translate-y-1/2 p-3 rounded-xl border cursor-pointer transition-all flex items-center space-x-2.5 shadow-xl select-none backdrop-blur-md z-10 ${
                    isCenter
                      ? 'border-red-500 bg-red-950/80 ring-2 ring-red-500/50 scale-110'
                      : isSelected
                      ? 'border-indigo-500 bg-indigo-950/80 ring-2 ring-indigo-500/50 scale-105'
                      : 'border-slate-800 bg-slate-900/90 hover:border-slate-600 hover:bg-slate-900'
                  }`}
                >
                  <div className={`p-1.5 rounded-lg border ${isCenter ? 'bg-red-950 border-red-800' : 'bg-slate-950 border-slate-800'}`}>
                    {getNodeIcon(node.node_type)}
                  </div>
                  <div>
                    <div className="flex items-center space-x-1">
                      <span className={`text-[9px] font-mono px-1 py-0.2 rounded font-semibold ${isCenter ? 'bg-red-900/80 text-red-200' : 'bg-slate-800 text-slate-400'}`}>
                        {node.node_type}
                      </span>
                    </div>
                    <p className="text-[11px] font-bold text-slate-200 mt-0.5 max-w-[120px] truncate">
                      {node.display_value}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Node Inspector Drawer */}
        {selectedNode && (
          <div className="absolute top-4 right-4 bottom-4 w-80 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-2xl flex flex-col justify-between z-20 font-mono text-xs text-slate-200">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="font-bold text-indigo-400 flex items-center gap-1.5">
                  <Info className="w-4 h-4" /> NODE INSPECTOR
                </span>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-slate-400 hover:text-slate-100"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-4 space-y-3">
                <div>
                  <span className="text-slate-500 block">ID:</span>
                  <span className="text-slate-200 font-bold">{selectedNode.id}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Type:</span>
                  <span className="text-indigo-300 font-semibold">{selectedNode.node_type}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Canonical Value:</span>
                  <span className="text-slate-200 break-all">{selectedNode.canonical_value}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">First Seen:</span>
                  <span className="text-slate-400">{selectedNode.first_seen}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Last Seen:</span>
                  <span className="text-slate-400">{selectedNode.last_seen}</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-500">
              Select connected edges to view evidence provenance.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
