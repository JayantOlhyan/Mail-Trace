'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { EmailSummary, Case } from '@/types';
import { RiskScore } from '@/components/RiskScore';
import { ThreatBadge } from '@/components/ThreatBadge';
import {
  ShieldAlert,
  AlertTriangle,
  Briefcase,
  Layers,
  Search,
  ArrowRight,
  RefreshCw,
  Network,
  Activity,
} from 'lucide-react';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    threats_detected: 183,
    high_risk: 24,
    open_cases: 12,
    campaign_candidates: 7,
    infrastructure_clusters: 15,
  });
  const [emails, setEmails] = useState<EmailSummary[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [m, e, c] = await Promise.all([
          api.getMetrics(),
          api.getEmails(),
          api.getCases(),
        ]);
        setMetrics(m);
        setEmails(e);
        setCases(c);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  const filteredEmails = emails.filter((item) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.subject.toLowerCase().includes(q) ||
      item.sender.toLowerCase().includes(q) ||
      item.id.toLowerCase().includes(q)
    );
  });

  // Split emails into high-risk (> 80) and normal
  const highRiskActivity = filteredEmails.filter((e) => e.risk_score >= 80);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-3xl font-black tracking-wider text-slate-100 font-mono">
            THREATTRACE AI
          </h1>
          <p className="text-xs text-slate-400 font-mono tracking-widest mt-1 uppercase">
            EMAIL THREAT & FORENSIC INTELLIGENCE
          </p>
        </div>

        {/* Global Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search IP, Domain, Subject..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono transition"
          />
        </div>
      </div>

      {/* Key Metrics Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link href="/investigations" className="group">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 hover:border-indigo-500/60 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-slate-400 uppercase">Threats Detected</span>
              <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 group-hover:scale-110 transition-transform">
                <ShieldAlert className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-extrabold font-mono text-slate-100 mt-3">{metrics.threats_detected}</p>
            <span className="text-[11px] text-indigo-400 font-mono flex items-center mt-2 group-hover:underline">
              View all analyzed emails <ArrowRight className="w-3 h-3 ml-1" />
            </span>
          </div>
        </Link>

        <Link href="/investigations?filter=high-risk" className="group">
          <div className="p-5 rounded-xl border border-red-900/40 bg-red-950/20 hover:border-red-600/60 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-red-400 uppercase">High Risk Alerts</span>
              <div className="p-2 rounded-lg bg-red-500/10 text-red-400 group-hover:scale-110 transition-transform">
                <AlertTriangle className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-extrabold font-mono text-red-300 mt-3">{metrics.high_risk}</p>
            <span className="text-[11px] text-red-400 font-mono flex items-center mt-2 group-hover:underline">
              Requires analyst review <ArrowRight className="w-3 h-3 ml-1" />
            </span>
          </div>
        </Link>

        <Link href="/cases" className="group">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 hover:border-indigo-500/60 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-slate-400 uppercase">Open Cases</span>
              <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 group-hover:scale-110 transition-transform">
                <Briefcase className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-extrabold font-mono text-slate-100 mt-3">{metrics.open_cases}</p>
            <span className="text-[11px] text-amber-400 font-mono flex items-center mt-2 group-hover:underline">
              Manage active incidents <ArrowRight className="w-3 h-3 ml-1" />
            </span>
          </div>
        </Link>

        <Link href="/campaigns" className="group">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/60 hover:border-indigo-500/60 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-slate-400 uppercase">Campaign Candidates</span>
              <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 group-hover:scale-110 transition-transform">
                <Layers className="w-5 h-5" />
              </div>
            </div>
            <p className="text-3xl font-extrabold font-mono text-slate-100 mt-3">{metrics.campaign_candidates}</p>
            <span className="text-[11px] text-purple-400 font-mono flex items-center mt-2 group-hover:underline">
              Correlated infrastructure <ArrowRight className="w-3 h-3 ml-1" />
            </span>
          </div>
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Loading analyst metrics...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Investigations */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
            <div className="p-4 bg-slate-900 flex items-center justify-between border-b border-slate-800">
              <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
                <Activity className="w-4 h-4 text-indigo-400" /> Recent Investigations
              </h3>
              <Link href="/investigations" className="text-xs text-indigo-400 hover:underline font-mono">
                View All
              </Link>
            </div>
            <div className="divide-y divide-slate-800/60 overflow-y-auto max-h-[350px] flex-1">
              {filteredEmails.length === 0 ? (
                <div className="p-8 text-center text-slate-500 font-mono">No recent investigations.</div>
              ) : (
                filteredEmails.map((email) => (
                  <div key={email.id} className="p-3.5 hover:bg-slate-800/40 transition-colors flex items-center justify-between gap-4 font-mono text-xs">
                    <div className="min-w-0">
                      <p className="font-sans font-semibold text-slate-200 truncate">{email.subject}</p>
                      <p className="text-[10px] text-slate-500 truncate mt-0.5">{email.sender}</p>
                    </div>
                    <div className="flex items-center gap-2.5 flex-shrink-0">
                      <ThreatBadge classification={email.classification} />
                      <Link href={`/investigations/${email.id}`} className="text-indigo-400 hover:text-indigo-300 font-bold">
                        Inspect
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* High-Risk Activity */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
            <div className="p-4 bg-slate-900 flex items-center justify-between border-b border-slate-800">
              <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400" /> High-Risk Activity
              </h3>
              <span className="text-xs font-mono text-slate-400">Score &ge; 80</span>
            </div>
            <div className="divide-y divide-slate-800/60 overflow-y-auto max-h-[350px] flex-1">
              {highRiskActivity.length === 0 ? (
                <div className="p-8 text-center text-slate-500 font-mono">No high-risk activity detected.</div>
              ) : (
                highRiskActivity.map((email) => (
                  <div key={email.id} className="p-3.5 hover:bg-slate-800/40 transition-colors flex items-center justify-between gap-4 font-mono text-xs">
                    <div className="min-w-0">
                      <p className="font-sans font-semibold text-slate-200 truncate">{email.subject}</p>
                      <p className="text-[10px] text-slate-500 truncate mt-0.5">{email.sender}</p>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      <RiskScore score={email.risk_score} size="sm" />
                      <Link href={`/investigations/${email.id}`} className="text-red-400 hover:text-red-300 font-bold">
                        Analyze
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Infrastructure Clusters */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
            <div className="p-4 bg-slate-900 flex items-center justify-between border-b border-slate-800">
              <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
                <Network className="w-4 h-4 text-purple-400" /> Infrastructure Clusters
              </h3>
              <Link href="/infrastructure" className="text-xs text-purple-400 hover:underline font-mono">
                Analyze Clusters
              </Link>
            </div>
            <div className="p-4 space-y-4 flex-1">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg text-center">
                  <span className="text-[10px] font-mono text-slate-400 uppercase block">Active Clusters</span>
                  <span className="text-2xl font-bold font-mono text-purple-400 block mt-1">{metrics.infrastructure_clusters}</span>
                </div>
                <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg text-center">
                  <span className="text-[10px] font-mono text-slate-400 uppercase block">Monitored ASNs</span>
                  <span className="text-2xl font-bold font-mono text-slate-200 block mt-1">42</span>
                </div>
              </div>
              <div className="p-3 bg-indigo-950/20 border border-indigo-900/40 rounded-lg text-xs leading-relaxed text-slate-300">
                <span className="font-bold text-indigo-400 block mb-1">Correlation Summary:</span>
                Identified overlap on AS13335 (Cloudflare) and AS16509 (Amazon) across recent BEC and Impersonation candidate clusters.
              </div>
            </div>
          </div>

          {/* Recent Cases */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
            <div className="p-4 bg-slate-900 flex items-center justify-between border-b border-slate-800">
              <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
                <Briefcase className="w-4 h-4 text-amber-400" /> Recent Cases
              </h3>
              <Link href="/cases" className="text-xs text-amber-400 hover:underline font-mono">
                View Directory
              </Link>
            </div>
            <div className="divide-y divide-slate-800/60 overflow-y-auto max-h-[350px] flex-1">
              {cases.length === 0 ? (
                <div className="p-8 text-center text-slate-500 font-mono">No open incidents.</div>
              ) : (
                cases.slice(0, 5).map((c) => (
                  <div key={c.id} className="p-3.5 hover:bg-slate-800/40 transition-colors flex items-center justify-between gap-4 font-mono text-xs">
                    <div className="min-w-0">
                      <span className="text-[10px] font-bold text-amber-400 bg-amber-950/80 px-1.5 py-0.5 rounded border border-amber-800/60 mr-2">
                        {c.case_id}
                      </span>
                      <span className="font-sans font-bold text-slate-200 truncate">{c.title}</span>
                    </div>
                    <Link href={`/cases/${c.id}`} className="text-amber-400 hover:text-amber-300 font-bold flex-shrink-0">
                      Workspace
                    </Link>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
