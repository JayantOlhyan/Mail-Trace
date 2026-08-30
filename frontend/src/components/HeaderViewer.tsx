'use client';

import React, { useState } from 'react';
import { HeaderForensics } from '@/types';
import { ChevronDown, ChevronRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

interface HeaderViewerProps {
  forensics: HeaderForensics;
}

export function HeaderViewer({ forensics }: HeaderViewerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const getAuthBadge = (status: string) => {
    if (status === 'PASS') {
      return (
        <span className="inline-flex items-center space-x-1 text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800 px-2 py-0.5 rounded">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>PASS</span>
        </span>
      );
    }
    if (status === 'FAIL') {
      return (
        <span className="inline-flex items-center space-x-1 text-xs font-mono text-red-400 bg-red-950/40 border border-red-800 px-2 py-0.5 rounded">
          <XCircle className="w-3.5 h-3.5" />
          <span>FAIL</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 text-xs font-mono text-slate-400 bg-slate-900 border border-slate-700 px-2 py-0.5 rounded">
        <AlertCircle className="w-3.5 h-3.5" />
        <span>{status}</span>
      </span>
    );
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
      {/* Header Bar */}
      <div className="p-4 bg-slate-900 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="font-semibold text-slate-200">Authentication & Header Forensics</h3>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">SPF:</span>
            {getAuthBadge(forensics.spf_status)}
            <span className="text-xs text-slate-400 ml-2">DKIM:</span>
            {getAuthBadge(forensics.dkim_status)}
            <span className="text-xs text-slate-400 ml-2">DMARC:</span>
            {getAuthBadge(forensics.dmarc_status)}
          </div>
        </div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="text-slate-400 hover:text-slate-100 flex items-center space-x-1 text-xs font-mono bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded transition"
        >
          <span>{isOpen ? 'Collapse Raw Headers' : 'Inspect Header Details'}</span>
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Expandable Content */}
      {isOpen && (
        <div className="p-4 border-t border-slate-800 space-y-4 bg-slate-950 font-mono text-xs text-slate-300">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-slate-500 block">From:</span>
              <span className="text-slate-200">{forensics.from_address}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Reply-To:</span>
              <span className={forensics.reply_to && forensics.reply_to !== forensics.from_address ? 'text-red-400 font-bold' : 'text-slate-200'}>
                {forensics.reply_to || 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 block">Return-Path:</span>
              <span className="text-slate-200">{forensics.return_path || 'N/A'}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Message-ID:</span>
              <span className="text-slate-200">{forensics.message_id || 'N/A'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
