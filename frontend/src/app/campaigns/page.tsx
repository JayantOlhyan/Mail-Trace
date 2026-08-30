'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { CampaignCandidate, CampaignStatus } from '@/types';
import { Layers, ArrowRight, RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignCandidate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getCampaigns();
        setCampaigns(data);
      } catch (err) {
        console.error('Failed to load campaigns:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleStatusChange = async (campaignId: string, status: CampaignStatus) => {
    try {
      await api.updateCampaignStatus(campaignId, status);
      setCampaigns((prev) =>
        prev.map((c) => (c.id === campaignId ? { ...c, status } : c))
      );
    } catch (err) {
      console.error('Failed to update campaign status:', err);
    }
  };

  const getStatusBadge = (status: CampaignStatus) => {
    let style = 'bg-slate-800 text-slate-300 border-slate-700';
    if (status === 'CANDIDATE') style = 'bg-purple-950/60 text-purple-400 border-purple-800';
    if (status === 'CONFIRMED_BY_ANALYST') style = 'bg-emerald-950/60 text-emerald-400 border-emerald-800';
    if (status === 'DISMISSED') style = 'bg-slate-900 text-slate-500 border-slate-800';

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded border text-xs font-mono font-bold uppercase ${style}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Layers className="w-5 h-5 text-purple-400" /> Infrastructure Campaign Candidates
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Correlated Cross-Email Campaign Candidates & Shared Technical Indicators
          </p>
        </div>
      </div>

      {/* Disclaimers */}
      <div className="p-4 rounded-xl border border-purple-900/40 bg-purple-950/20 text-purple-200 text-xs font-mono flex items-start space-x-3">
        <AlertTriangle className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="block font-bold">Investigative Disclaimer:</strong>
          Campaign candidates are machine-generated correlations based on shared infrastructure and temporal windows. Shared cloud infrastructure alone does not prove common authorship.
        </div>
      </div>

      {/* Campaigns Grid */}
      {loading ? (
        <div className="p-8 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
          <RefreshCw className="w-4 h-4 animate-spin text-purple-400" />
          <span>Correlating campaign candidates...</span>
        </div>
      ) : campaigns.length === 0 ? (
        <div className="p-8 text-center text-slate-500 font-mono">No campaign candidates detected.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {campaigns.map((c) => (
            <div
              key={c.id}
              className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl hover:border-purple-500/50 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-purple-400 bg-purple-950/80 px-2.5 py-1 rounded border border-purple-800">
                    {c.campaign_id}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono text-slate-400">Confidence: {c.confidence}%</span>
                    {getStatusBadge(c.status)}
                  </div>
                </div>

                <h3 className="font-bold text-slate-100 text-base">{c.summary}</h3>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">{c.explanation}</p>

                {/* Shared Indicators */}
                <div className="pt-2 border-t border-slate-800/80 space-y-1.5 font-mono text-xs">
                  <span className="text-slate-500 text-[11px] block">SHARED INDICATORS:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {c.shared_indicators.map((ind) => (
                      <span key={ind} className="px-2 py-0.5 rounded bg-slate-950 text-indigo-300 border border-slate-800 text-[11px]">
                        {ind}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer status change */}
              <div className="pt-4 border-t border-slate-800 flex items-center justify-between font-mono text-xs">
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500 text-[11px]">Analyst Decision:</span>
                  <select
                    value={c.status}
                    onChange={(e) => handleStatusChange(c.id, e.target.value as CampaignStatus)}
                    className="bg-slate-950 border border-slate-800 text-slate-200 rounded px-2 py-1 focus:outline-none focus:border-purple-500 cursor-pointer"
                  >
                    <option value="CANDIDATE">CANDIDATE</option>
                    <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                    <option value="CONFIRMED_BY_ANALYST">CONFIRMED_BY_ANALYST</option>
                    <option value="DISMISSED">DISMISSED</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
