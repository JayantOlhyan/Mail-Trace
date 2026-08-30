'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { EmailSummary } from '@/types';
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
} from 'lucide-react';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    threats_detected: 183,
    high_risk: 24,
    open_cases: 12,
    campaign_candidates: 7,
  });
  const [emails, setEmails] = useState<EmailSummary[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [m, e] = await Promise.all([api.getMetrics(), api.getEmails()]);
        setMetrics(m);
        setEmails(e);
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

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-100 flex items-center gap-2">
            Security Operations Dashboard
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-1">
            Real-time Threat Monitoring & Incident Investigation Workspace
          </p>
        </div>

        {/* Global Search */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search IP, Domain, Email ID..."
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono transition"
          />
        </div>
      </div>

      {/* Top-Level Metrics */}
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

      {/* Recent Email Investigations Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 bg-slate-900 flex items-center justify-between border-b border-slate-800">
          <h3 className="font-semibold text-slate-200 text-sm tracking-wide">Recent Suspicious Email Investigations</h3>
          <Link href="/investigations" className="text-xs text-indigo-400 hover:underline font-mono">
            View All →
          </Link>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Loading active investigations...</span>
          </div>
        ) : filteredEmails.length === 0 ? (
          <div className="p-8 text-center text-slate-500 font-mono">No matching email investigations found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-mono text-slate-400 bg-slate-950/60 uppercase">
                  <th className="p-3.5">ID</th>
                  <th className="p-3.5">Risk Score</th>
                  <th className="p-3.5">Classification</th>
                  <th className="p-3.5">Subject & Sender</th>
                  <th className="p-3.5">Received Date</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs text-slate-300">
                {filteredEmails.map((email) => (
                  <tr key={email.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 text-indigo-400 font-bold">{email.id}</td>
                    <td className="p-3.5">
                      <RiskScore score={email.risk_score} size="sm" />
                    </td>
                    <td className="p-3.5">
                      <ThreatBadge classification={email.classification} />
                    </td>
                    <td className="p-3.5 max-w-xs">
                      <p className="font-sans font-medium text-slate-200 truncate">{email.subject}</p>
                      <p className="text-[11px] text-slate-400 truncate">{email.sender}</p>
                    </td>
                    <td className="p-3.5 text-slate-400 text-[11px]">
                      {new Date(email.received_at).toLocaleString()}
                    </td>
                    <td className="p-3.5 text-right">
                      <Link
                        href={`/investigations/${email.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white rounded border border-indigo-500/40 transition text-xs font-semibold"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
