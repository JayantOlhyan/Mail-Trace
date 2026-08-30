import React from 'react';
import { ThreatReasoningFinding } from '@/types';
import { ShieldAlert, AlertTriangle, Info, FileText } from 'lucide-react';

interface EvidenceCardProps {
  finding: ThreatReasoningFinding;
}

export function EvidenceCard({ finding }: EvidenceCardProps) {
  let severityStyle = 'border-slate-800 bg-slate-900/60 text-slate-300';
  let Icon = Info;

  if (finding.severity === 'HIGH') {
    severityStyle = 'border-red-900/50 bg-red-950/20 text-red-300';
    Icon = ShieldAlert;
  } else if (finding.severity === 'MEDIUM') {
    severityStyle = 'border-amber-900/50 bg-amber-950/20 text-amber-300';
    Icon = AlertTriangle;
  }

  return (
    <div className={`p-4 rounded-lg border ${severityStyle} space-y-2 transition-all hover:border-indigo-500/50`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className="w-4 h-4" />
          <span className="font-mono text-xs font-bold text-indigo-400 px-2 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/60">
            {finding.id}
          </span>
          <span className="text-xs font-mono text-slate-400">
            {finding.originating_phase}
          </span>
        </div>
        <span className="text-xs font-bold font-mono uppercase px-2 py-0.5 rounded bg-black/40 border border-current">
          {finding.severity} SEVERITY
        </span>
      </div>

      <p className="text-sm font-medium text-slate-100">{finding.finding}</p>

      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-400">
        <span className="flex items-center space-x-1 text-slate-400">
          <FileText className="w-3.5 h-3.5" />
          <span>Category: {finding.category}</span>
        </span>
        <span className="text-slate-500">Ref: {finding.evidence_reference}</span>
      </div>
    </div>
  );
}
