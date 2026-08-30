'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Case, CaseStatus } from '@/types';
import { Briefcase, Plus, Filter, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react';

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getCases();
        setCases(data);
      } catch (err) {
        console.error('Failed to load cases:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleStatusChange = async (caseId: string, newStatus: CaseStatus) => {
    try {
      await api.updateCaseStatus(caseId, newStatus);
      setCases((prev) =>
        prev.map((c) => (c.id === caseId ? { ...c, status: newStatus } : c))
      );
    } catch (err) {
      console.error('Failed to update case status:', err);
    }
  };

  const filtered = cases.filter((c) =>
    selectedStatus === 'ALL' ? true : c.status === selectedStatus
  );

  const getPriorityBadge = (priority: string) => {
    let style = 'bg-slate-800 text-slate-300 border-slate-700';
    if (priority === 'CRITICAL') style = 'bg-red-950/60 text-red-400 border-red-800';
    if (priority === 'HIGH') style = 'bg-amber-950/60 text-amber-400 border-amber-800';
    if (priority === 'MEDIUM') style = 'bg-blue-950/60 text-blue-400 border-blue-800';

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-mono font-bold uppercase ${style}`}>
        {priority}
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-amber-400" /> Case Management Directory
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Active Incident Escalation & Analyst Case Workflows
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1 bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-xs font-mono">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="ESCALATED">Escalated</option>
              <option value="RESOLVED">Resolved</option>
              <option value="DISMISSED">Dismissed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cases Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
            <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
            <span>Loading active cases...</span>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-slate-500 font-mono">No cases found matching criteria.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-mono text-slate-400 bg-slate-950/60 uppercase">
                  <th className="p-3.5">Case ID</th>
                  <th className="p-3.5">Priority</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Title & Summary</th>
                  <th className="p-3.5">Assigned Analyst</th>
                  <th className="p-3.5">Related Entities</th>
                  <th className="p-3.5 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs text-slate-300">
                {filtered.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 font-bold text-amber-400">{c.case_id}</td>
                    <td className="p-3.5">{getPriorityBadge(c.priority)}</td>
                    <td className="p-3.5">
                      <select
                        value={c.status}
                        onChange={(e) => handleStatusChange(c.id, e.target.value as CaseStatus)}
                        className="bg-slate-950 border border-slate-800 text-slate-200 rounded px-2 py-1 text-xs focus:outline-none focus:border-amber-500 cursor-pointer font-mono"
                      >
                        <option value="OPEN">OPEN</option>
                        <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                        <option value="ESCALATED">ESCALATED</option>
                        <option value="RESOLVED">RESOLVED</option>
                        <option value="DISMISSED">DISMISSED</option>
                      </select>
                    </td>
                    <td className="p-3.5 max-w-xs">
                      <p className="font-sans font-bold text-slate-200 truncate">{c.title}</p>
                      <p className="text-[11px] text-slate-400 truncate">{c.summary}</p>
                    </td>
                    <td className="p-3.5 text-slate-300">{c.assigned_to}</td>
                    <td className="p-3.5 text-slate-400 text-[11px]">
                      {c.related_emails_count} Emails • {c.campaigns_count} Campaign
                    </td>
                    <td className="p-3.5 text-right">
                      <Link
                        href={`/cases/${c.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1 bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white rounded border border-amber-500/40 transition text-xs font-semibold"
                      >
                        <span>Case Workspace</span>
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
