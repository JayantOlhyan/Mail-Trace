'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { InvestigationGraph } from '@/types';
import { GraphViewer } from '@/components/GraphViewer';
import { GitFork, RefreshCw } from 'lucide-react';

export default function GraphExplorerPage() {
  const [graph, setGraph] = useState<InvestigationGraph | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getEmailGraph('EML-2026-8801');
        setGraph(data);
      } catch (err) {
        console.error('Failed to load global investigation graph:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
          <GitFork className="w-5 h-5 text-indigo-400" /> Standalone Investigation Graph Explorer
        </h1>
        <p className="text-xs text-slate-400 font-mono mt-0.5">
          Interactive Bounded Graph Traversal Across Ingested Indicators & Relationships
        </p>
      </div>

      {loading || !graph ? (
        <div className="p-12 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Building investigation graph canvas...</span>
        </div>
      ) : (
        <GraphViewer graph={graph} />
      )}
    </div>
  );
}
