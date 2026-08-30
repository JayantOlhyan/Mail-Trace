'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ReportPreview } from '@/components/ReportPreview';
import { AnalystNotes } from '@/components/AnalystNotes';
import { Briefcase, ArrowLeft, FileText, ShieldAlert } from 'lucide-react';

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;
  const reportId = `RPT-2026-${caseId.replace('CASE-', '')}`;
  const [showReport, setShowReport] = useState(false);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <Link
          href="/cases"
          className="inline-flex items-center space-x-1 text-xs font-mono text-slate-400 hover:text-slate-100 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Cases List</span>
        </Link>

        <button
          onClick={() => setShowReport(!showReport)}
          className="flex items-center space-x-1.5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-mono text-xs font-semibold shadow-lg transition"
        >
          <FileText className="w-4 h-4" />
          <span>{showReport ? 'Hide Report Preview' : 'Generate Forensic Report'}</span>
        </button>
      </div>

      {showReport ? (
        <ReportPreview reportId={reportId} caseId={caseId} />
      ) : (
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-4">
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

          <AnalystNotes entityType="CASE" entityId={caseId} />
        </div>
      )}
    </div>
  );
}
