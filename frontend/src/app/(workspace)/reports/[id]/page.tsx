'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { ReportPreview } from '@/components/ReportPreview';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function ReportDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const caseId = `CASE-${id.replace('RPT-2026-', '')}`;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <Link
          href="/cases"
          className="inline-flex items-center space-x-1 text-xs font-mono text-slate-400 hover:text-slate-100 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Case Management</span>
        </Link>
      </div>

      <ReportPreview reportId={id} caseId={caseId} />
    </div>
  );
}
