'use client';

import React, { useState } from 'react';
import { Play, RotateCcw, ShieldCheck, CheckCircle2 } from 'lucide-react';

export function DemoBanner() {
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleReset = async () => {
    setResetting(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/demo/reset', { method: 'POST' });
      if (res.ok) {
        setMessage('SIH Demo environment reset to baseline state.');
        setTimeout(() => setMessage(null), 4000);
      }
    } catch (err) {
      console.error('Demo reset error:', err);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="bg-gradient-to-r from-indigo-950 via-slate-900 to-purple-950 border-b border-indigo-500/30 px-6 py-2.5 flex flex-wrap items-center justify-between gap-4 font-mono text-xs select-none">
      <div className="flex items-center space-x-3 text-indigo-200">
        <div className="p-1 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-400/40">
          <Play className="w-3.5 h-3.5" />
        </div>
        <div>
          <strong className="text-slate-100 font-bold tracking-wider">SIH 2026 DEMONSTRATION MODE ACTIVE</strong>
          <span className="ml-2 text-slate-400 text-[11px] hidden md:inline">
            Pre-configured evaluation dataset loaded (Phishing, BEC, Impersonation & Legitimate Emails)
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {message && (
          <span className="text-emerald-400 flex items-center gap-1 text-[11px] animate-fade-in">
            <CheckCircle2 className="w-3.5 h-3.5" />
            {message}
          </span>
        )}

        <button
          onClick={handleReset}
          disabled={resetting}
          className="flex items-center space-x-1.5 px-3 py-1 bg-indigo-600/30 hover:bg-indigo-600 border border-indigo-500/50 text-indigo-200 hover:text-white rounded transition font-semibold"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${resetting ? 'animate-spin' : ''}`} />
          <span>{resetting ? 'Resetting Demo...' : 'Reset Demo Environment'}</span>
        </button>
      </div>
    </div>
  );
}
