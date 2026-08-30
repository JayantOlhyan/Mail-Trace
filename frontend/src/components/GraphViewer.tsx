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
        {/* SVG Graph Layout Simulation */}
        <div
          className="transition-transform duration-200 flex flex-wrap items-center justify-center gap-8 max-w-4xl"
          style={{ transform: `scale(${zoom})` }}
        >
          {graph.nodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            return (
              <div
                key={node.id}
                onClick={() => {
                  setSelectedNode(node);
                  setSelectedEdge(null);
                }}
                className={`p-4 rounded-xl border cursor-pointer transition-all flex items-center space-x-3 shadow-lg select-none ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-950/60 ring-2 ring-indigo-500/50 scale-105'
                    : 'border-slate-800 bg-slate-900/80 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                  {getNodeIcon(node.node_type)}
                </div>
                <div>
                  <div className="flex items-center space-x-1.5">
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-semibold">
                      {node.node_type}
                    </span>
                  </div>
                  <p className="text-xs font-bold text-slate-200 mt-1 max-w-[160px] truncate">
                    {node.display_value}
                  </p>
                </div>
              </div>
            );
          })}
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
