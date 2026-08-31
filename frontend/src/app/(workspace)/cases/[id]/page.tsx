'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ReportPreview } from '@/components/ReportPreview';
import { AnalystNotes } from '@/components/AnalystNotes';
import { Briefcase, ArrowLeft, FileText, ShieldAlert, Cpu, UserCheck, CheckCircle2 } from 'lucide-react';

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;
  const reportId = `RPT-2026-${caseId.replace('CASE-', '')}`;
  const [showReport, setShowReport] = useState(false);
  const [analystDecision, setAnalystDecision] = useState('PENDING');
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const handleDecisionChange = (val: string) => {
    setAnalystDecision(val);
    setActionMessage(`Analyst Decision Recorded: ${val}`);
    setTimeout(() => setActionMessage(null), 3000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
        <Link
          href="/cases"
          className="inline-flex items-center space-x-1 text-xs font-mono text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-slate-100 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Cases List</span>
        </Link>

        {actionMessage && (
          <div className="bg-emerald-950/80 border border-emerald-700 text-emerald-300 text-xs px-3 py-1.5 rounded font-mono animate-fade-in flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{actionMessage}</span>
          </div>
        )}

        <button
          onClick={() => setShowReport(!showReport)}
          className="flex items-center space-x-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-slate-900 dark:text-white rounded font-mono text-xs font-semibold shadow-lg transition"
        >
          <FileText className="w-4 h-4" />
          <span>{showReport ? 'Hide Report Preview' : 'Generate Forensic Report'}</span>
        </button>
      </div>

      {/* Case Workflow Status Indicator */}
      <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-4 rounded-xl flex items-center justify-between flex-wrap gap-4 font-mono text-xs text-slate-600 dark:text-slate-400">
        <span className="font-bold text-slate-700 dark:text-slate-300">INCIDENT WORKFLOW:</span>
        <div className="flex items-center space-x-2">
          <span className="text-emerald-400 font-bold">1. Ingested</span>
          <span>&rarr;</span>
          <span className="text-emerald-400 font-bold">2. Case Created</span>
          <span>&rarr;</span>
          <span className="text-emerald-400 font-bold">3. Evidence Added</span>
          <span>&rarr;</span>
          <span className={analystDecision !== 'PENDING' ? 'text-emerald-400 font-bold' : 'text-amber-500 animate-pulse font-bold'}>
            4. Analyst Decision
          </span>
          <span>&rarr;</span>
          <span className={showReport ? 'text-emerald-400 font-bold' : 'text-slate-600'}>
            5. Report Export
          </span>
        </div>
      </div>

      {showReport ? (
        <ReportPreview reportId={reportId} caseId={caseId} />
      ) : (
        <div className="space-y-6">
          {/* Main Case Info Header */}
          <div className="bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/80 px-2.5 py-1 rounded border border-amber-800">
                  {caseId}
                </span>
                <span className="px-2.5 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800 text-xs font-mono font-bold uppercase">
                  OPEN
                </span>
                <span className="px-2.5 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-800 text-xs font-mono font-bold uppercase">
                  HIGH RISK
                </span>
              </div>
            </div>

            <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">
              High-Risk Financial Credential Harvesting Campaign
            </h1>
            <p className="text-xs text-slate-700 dark:text-slate-300 font-sans leading-relaxed">
              Active credential harvesting campaign attempting to compromise HR payroll accounts. Infrastructure correlates across 3 distinct email incidents with shared bulletproof hosting ASN.
            </p>

            {/* Sub-tabs bar (Approach H Panel 5) */}
            <div className="flex items-center gap-2 border-t border-slate-200 dark:border-slate-800 pt-4 font-mono text-xs">
              <button className="px-3 py-1.5 rounded bg-indigo-600 text-white font-bold">Summary</button>
              <button className="px-3 py-1.5 rounded text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800">Evidence (17)</button>
              <button className="px-3 py-1.5 rounded text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800">Timeline</button>
              <button className="px-3 py-1.5 rounded text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800">Notes</button>
              <button className="px-3 py-1.5 rounded text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800">Report</button>
            </div>
          </div>

          {/* AI Assessment vs Analyst Verdict Section (Approach H Panel 5) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI Assessment */}
            <div className="bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 p-5 rounded-xl space-y-4 shadow-xl">
              <h3 className="font-semibold text-slate-800 dark:text-slate-200 text-sm font-mono tracking-wide flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
                <Cpu className="w-4 h-4 text-indigo-400" />
                AI Assessment
              </h3>
              <div className="text-center py-4 space-y-2 font-mono">
                <div className="text-3xl font-black text-red-500 tracking-wider">PHISHING</div>
                <div className="text-4xl font-extrabold text-red-400">91 / 100</div>
                <div className="text-xs text-indigo-400 font-bold tracking-widest uppercase">High Confidence</div>
              </div>
            </div>

            {/* Analyst Verdict */}
            <div className="bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 p-5 rounded-xl space-y-4 shadow-xl">
              <h3 className="font-semibold text-slate-800 dark:text-slate-200 text-sm font-mono tracking-wide flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
                <UserCheck className="w-4 h-4 text-emerald-400" />
                Analyst Verdict
              </h3>
              <div className="space-y-4 font-mono text-xs">
                <div className="flex flex-col gap-2">
                  <span className="px-4 py-2 rounded bg-emerald-600 text-white font-bold text-center tracking-wider shadow-md">
                    CONFIRMED PHISHING
                  </span>
                </div>
                <div className="space-y-1 text-slate-600 dark:text-slate-400 text-[11px] pt-1">
                  <div className="flex justify-between">
                    <span>Analyst:</span>
                    <span className="text-slate-800 dark:text-slate-200 font-bold">Tier 2 Analyst</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Verified Date:</span>
                    <span className="text-slate-800 dark:text-slate-200 font-bold">May 12, 2026 11:02 AM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Evidence Integrity SHA-256 Badge (Approach H Panel 5) */}
          <div className="p-4 bg-emerald-950/30 border border-emerald-800/60 rounded-xl flex items-center justify-between font-mono text-xs text-emerald-300 shadow-lg">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="font-bold">Evidence Integrity:</span>
              <span className="text-slate-300">Cryptographically Hashed & Sealed</span>
            </div>
            <div className="flex items-center space-x-1.5 px-3 py-1 rounded bg-emerald-950 text-emerald-400 border border-emerald-700 font-bold">
              <span>✓ SHA-256 Verified</span>
            </div>
          </div>

          <AnalystNotes entityType="CASE" entityId={caseId} />
        </div>
      )}
    </div>
  );
}
