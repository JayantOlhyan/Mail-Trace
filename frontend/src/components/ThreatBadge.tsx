import React from 'react';
import { ThreatClassification } from '@/types';

interface ThreatBadgeProps {
  classification: ThreatClassification;
}

export function ThreatBadge({ classification }: ThreatBadgeProps) {
  let badgeStyle = 'bg-slate-800 text-slate-300 border-slate-700';

  switch (classification) {
    case 'PHISHING':
      badgeStyle = 'bg-red-950/60 text-red-400 border-red-800/80';
      break;
    case 'BEC':
      badgeStyle = 'bg-purple-950/60 text-purple-400 border-purple-800/80';
      break;
    case 'IMPERSONATION':
      badgeStyle = 'bg-amber-950/60 text-amber-400 border-amber-800/80';
      break;
    case 'FRAUD':
      badgeStyle = 'bg-rose-950/60 text-rose-400 border-rose-800/80';
      break;
    case 'MALWARE':
      badgeStyle = 'bg-orange-950/60 text-orange-400 border-orange-800/80';
      break;
    case 'LEGITIMATE':
      badgeStyle = 'bg-emerald-950/60 text-emerald-400 border-emerald-800/80';
      break;
    default:
      badgeStyle = 'bg-slate-800 text-slate-300 border-slate-700';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded border text-xs font-mono font-bold tracking-wider uppercase ${badgeStyle}`}>
      {classification}
    </span>
  );
}
