'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { EmailSummary } from '@/types';
import { RiskScore } from '@/components/RiskScore';
import { ThreatBadge } from '@/components/ThreatBadge';
import { Search, Filter, ArrowRight, RefreshCw, Mail } from 'lucide-react';

export default function InvestigationsPage() {
  const [emails, setEmails] = useState<EmailSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClassification, setSelectedClassification] = useState<string>('ALL');

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getEmails();
        setEmails(data);
      } catch (err) {
        console.error('Failed to load email investigations:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filtered = emails.filter((item) => {
    const matchesSearch =
      !searchQuery ||
      item.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.id.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesClass =
      selectedClassification === 'ALL' || item.classification === selectedClassification;

    return matchesSearch && matchesClass;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <Mail className="w-5 h-5 text-indigo-400" /> Email Investigations Workspace
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 font-mono mt-0.5">
            Full Ingested Evidence Directory & Risk Analysis Index
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-600 dark:text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search sender, subject..."
              className="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-800 dark:text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div className="flex items-center space-x-1 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2 py-1 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-600 dark:text-slate-400" />
            <select
              value={selectedClassification}
              onChange={(e) => setSelectedClassification(e.target.value)}
              className="bg-transparent text-slate-800 dark:text-slate-200 focus:outline-none font-mono cursor-pointer"
            >
              <option value="ALL">All Classifications</option>
              <option value="PHISHING">Phishing</option>
              <option value="BEC">BEC</option>
              <option value="IMPERSONATION">Impersonation</option>
              <option value="LEGITIMATE">Legitimate</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Loading emails...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-slate-500 font-mono">No email records match criteria.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-950/60 uppercase">
                  <th className="p-3.5">Email ID</th>
                  <th className="p-3.5">Risk Score</th>
                  <th className="p-3.5">Classification</th>
                  <th className="p-3.5">Sender</th>
                  <th className="p-3.5">Subject</th>
                  <th className="p-3.5">Received Date</th>
                  <th className="p-3.5 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs text-slate-700 dark:text-slate-300">
                {filtered.map((email) => (
                  <tr key={email.id} className="hover:bg-slate-200 dark:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 font-bold text-indigo-400">{email.id}</td>
                    <td className="p-3.5">
                      <RiskScore score={email.risk_score} size="sm" />
                    </td>
                    <td className="p-3.5">
                      <ThreatBadge classification={email.classification} />
                    </td>
                    <td className="p-3.5 max-w-[200px] truncate text-slate-700 dark:text-slate-300">{email.sender}</td>
                    <td className="p-3.5 max-w-xs truncate font-sans text-slate-800 dark:text-slate-200 font-medium">
                      {email.subject}
                    </td>
                    <td className="p-3.5 text-slate-600 dark:text-slate-400 text-[11px]">
                      {new Date(email.received_at).toLocaleString()}
                    </td>
                    <td className="p-3.5 text-right">
                      <Link
                        href={`/investigations/${email.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-slate-900 dark:text-white rounded border border-indigo-500/40 transition text-xs font-semibold"
                      >
                        <span>Inspect Workspace</span>
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
