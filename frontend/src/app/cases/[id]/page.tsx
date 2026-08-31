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
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <Link
          href="/cases"
          className="inline-flex items-center space-x-1 text-xs font-mono text-slate-400 hover:text-slate-100 transition"
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
          className="flex items-center space-x-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-mono text-xs font-semibold shadow-lg transition"
        >
          <FileText className="w-4 h-4" />
          <span>{showReport ? 'Hide Report Preview' : 'Generate Forensic Report'}</span>
        </button>
      </div>

      {/* Case Workflow Status Indicator */}
      <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between flex-wrap gap-4 font-mono text-xs text-slate-400">
        <span className="font-bold text-slate-300">INCIDENT WORKFLOW:</span>
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
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-amber-400 bg-amber-950/80 px-2.5 py-1 rounded border border-amber-800">
                {caseId}
              </span>
              <span className="px-2.5 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-800 text-xs font-mono font-bold uppercase">
                HIGH PRIORITY
              </span>
            </div>

            <h1 className="text-xl font-bold text-slate-100">
              High-Risk Financial Credential Harvesting Campaign
            </h1>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              Active credential harvesting campaign attempting to compromise HR payroll accounts. Infrastructure correlates across 3 distinct email incidents with shared bulletproof hosting ASN.
            </p>
          </div>

          {/* AI Finding vs Analyst Decision Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI Finding */}
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl space-y-4">
              <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                AI Auto-Detection Finding
              </h3>
              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between border-b border-slate-800/60 pb-2">
                  <span className="text-slate-500">Risk Assessment:</span>
                  <span className="text-red-400 font-bold">91 / 100</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-2">
                  <span className="text-slate-500">AI Classification:</span>
                  <span className="text-red-400 font-bold">PHISHING</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Confidence Score:</span>
                  <span className="text-indigo-400 font-bold">HIGH</span>
                </div>
              </div>
            </div>

            {/* Analyst Decision */}
            <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-xl space-y-4">
              <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
                <UserCheck className="w-4 h-4 text-emerald-400" />
                Analyst Incident Verdict
              </h3>
              <div className="space-y-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-mono text-slate-500 uppercase">Set Official Verdict</label>
                  <select
                    value={analystDecision}
                    onChange={(e) => handleDecisionChange(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded p-2 text-xs focus:outline-none focus:border-emerald-500 cursor-pointer font-mono"
                  >
                    <option value="PENDING">PENDING REVIEW</option>
                    <option value="CONFIRMED_PHISHING">CONFIRMED PHISHING</option>
                    <option value="CONFIRMED_BEC">CONFIRMED BUSINESS EMAIL COMPROMISE (BEC)</option>
                    <option value="FALSE_POSITIVE">FALSE POSITIVE (DISMISS)</option>
                  </select>
                </div>
                <div className="p-3 bg-emerald-950/20 border border-emerald-900/40 rounded-lg text-xs leading-relaxed text-slate-300 font-mono">
                  <span className="font-bold text-emerald-400 block mb-1">Decision Lock Status:</span>
                  Verdicts are cryptographically signed and injected directly into the final forensic report package.
                </div>
              </div>
            </div>
          </div>

          <AnalystNotes entityType="CASE" entityId={caseId} />
        </div>
      )}
    </div>
  );
}
