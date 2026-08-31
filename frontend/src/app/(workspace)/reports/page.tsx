'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Case } from '@/types';
import { FileText, ArrowRight, RefreshCw, Briefcase, Calendar } from 'lucide-react';

export default function ReportsPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" /> Forensic Reports & Evidence Export
          </h1>
          <p className="text-xs text-slate-600 dark:text-slate-400 font-mono mt-0.5">
            Cryptographically Verified Case Reports & Legal Artifact Packages
          </p>
        </div>
      </div>

      {/* Reports Directory */}
      <div className="bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xl">
        {loading ? (
          <div className="p-8 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
            <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
            <span>Loading forensic index...</span>
          </div>
        ) : cases.length === 0 ? (
          <div className="p-8 text-center text-slate-500 font-mono">No cases available for reporting.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-950/60 uppercase">
                  <th className="p-3.5">Report ID</th>
                  <th className="p-3.5">Associated Case</th>
                  <th className="p-3.5">Priority</th>
                  <th className="p-3.5">Case Title</th>
                  <th className="p-3.5">Date Created</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs text-slate-700 dark:text-slate-300">
                {cases.map((c) => {
                  const reportId = `RPT-2026-${c.case_id.replace('CASE-', '')}`;
                  return (
                    <tr key={c.id} className="hover:bg-slate-200 dark:bg-slate-800/40 transition-colors">
                      <td className="p-3.5 font-bold text-indigo-400">{reportId}</td>
                      <td className="p-3.5 font-bold text-slate-700 dark:text-slate-300">{c.case_id}</td>
                      <td className="p-3.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[10px] font-bold ${
                          c.priority === 'CRITICAL' 
                            ? 'bg-red-950/60 text-red-400 border-red-800' 
                            : c.priority === 'HIGH' 
                              ? 'bg-amber-950/60 text-amber-400 border-amber-800' 
                              : 'bg-blue-950/60 text-blue-400 border-blue-800'
                        }`}>
                          {c.priority}
                        </span>
                      </td>
                      <td className="p-3.5 max-w-xs font-sans font-medium text-slate-800 dark:text-slate-200 truncate">
                        {c.title}
                      </td>
                      <td className="p-3.5 text-slate-600 dark:text-slate-400 text-[11px] font-mono">
                        {new Date(c.created_at).toLocaleDateString()}
                      </td>
                      <td className="p-3.5 text-right">
                        <Link
                          href={`/reports/${reportId}`}
                          className="inline-flex items-center space-x-1 px-3 py-1 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-slate-900 dark:text-white rounded border border-indigo-500/40 transition text-xs font-semibold"
                        >
                          <span>Generate Report</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
