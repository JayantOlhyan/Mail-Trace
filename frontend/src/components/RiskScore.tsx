import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface RiskScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export function RiskScore({ score, size = 'md' }: RiskScoreProps) {
  let label = 'LOW RISK';
  let colorClass = 'text-emerald-400 bg-emerald-950/40 border-emerald-800';
  let Icon = CheckCircle;

  if (score >= 80) {
    label = 'CRITICAL / HIGH RISK';
    colorClass = 'text-red-400 bg-red-950/40 border-red-800';
    Icon = ShieldAlert;
  } else if (score >= 50) {
    label = 'MEDIUM RISK';
    colorClass = 'text-amber-400 bg-amber-950/40 border-amber-800';
    Icon = AlertTriangle;
  } else if (score >= 20) {
    label = 'LOW RISK';
    colorClass = 'text-blue-400 bg-blue-950/40 border-blue-800';
    Icon = Info;
  }

  if (size === 'sm') {
    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded border text-xs font-mono font-semibold ${colorClass}`}>
        <Icon className="w-3 h-3" />
        <span>{score}/100</span>
      </span>
    );
  }

  if (size === 'lg') {
    return (
      <div className={`p-4 rounded-xl border flex items-center space-x-4 ${colorClass}`}>
        <div className="p-3 rounded-lg bg-black/40 border border-current">
          <Icon className="w-8 h-8" />
        </div>
        <div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold font-mono">{score}</span>
            <span className="text-xs text-slate-400 font-mono">/ 100</span>
          </div>
          <p className="text-xs font-bold tracking-wider uppercase font-mono mt-0.5">{label}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`px-3 py-2 rounded-lg border flex items-center space-x-2.5 ${colorClass}`}>
      <Icon className="w-5 h-5 flex-shrink-0" />
      <div>
        <span className="text-sm font-bold font-mono">{score}/100</span>
        <span className="ml-2 text-xs font-semibold uppercase">{label}</span>
      </div>
    </div>
  );
}
