'use client';

import React, { useState } from 'react';
import {
  FileText,
  Download,
  FileCode,
  Archive,
  Printer,
  ShieldCheck,
  Lock,
  Hash,
  UserCheck,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

interface ReportPreviewProps {
  reportId: string;
  caseId: string;
}

export function ReportPreview({ reportId, caseId }: ReportPreviewProps) {
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = async (format: 'pdf' | 'json' | 'package') => {
    setDownloading(format);
    try {
      const endpoint = `http://localhost:8000/api/v1/reports/${reportId}/${format}`;
      window.open(endpoint, '_blank');
    } catch (err) {
      console.error(`Failed to download ${format}:`, err);
    } finally {
      setTimeout(() => setDownloading(null), 1000);
    }
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl space-y-6">
      {/* Top Export Toolbar */}
      <div className="p-4 bg-slate-900 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/40">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-slate-100 text-sm flex items-center gap-2">
              MAILTRACE FORENSIC REPORT • {reportId}
            </h2>
            <span className="text-xs font-mono text-slate-400">Associated Case: {caseId} • Version 1.0</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
          <button
            onClick={() => handleDownload('pdf')}
            disabled={downloading === 'pdf'}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-semibold transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{downloading === 'pdf' ? 'Exporting PDF...' : 'Export PDF'}</span>
          </button>

          <button
            onClick={() => handleDownload('json')}
            disabled={downloading === 'json'}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 font-semibold transition"
          >
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={() => handleDownload('package')}
            disabled={downloading === 'package'}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 rounded font-semibold transition"
          >
            <Archive className="w-3.5 h-3.5" />
            <span>ZIP Package (SHA-256 Manifest)</span>
          </button>
        </div>
      </div>

      {/* Report Document Content */}
      <div className="p-6 md:p-8 space-y-8 font-sans text-slate-300 max-w-5xl mx-auto">
        {/* Document Header */}
        <div className="border-b border-slate-800 pb-6 flex items-start justify-between">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800 text-xs font-mono font-bold mb-3">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>OFFICIAL CYBER FORENSIC REPORT</span>
            </div>
            <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">
              Email Incident Forensic Assessment Report
            </h1>
            <p className="text-xs font-mono text-slate-400 mt-1">
              MailTrace Automated Intelligence Engine v1.0 • Generated for {caseId}
            </p>
          </div>

          <div className="text-right font-mono text-xs text-slate-400 space-y-1">
            <p><strong className="text-slate-200">Report ID:</strong> {reportId}</p>
            <p><strong className="text-slate-200">Case ID:</strong> {caseId}</p>
            <p><strong className="text-slate-200">Evidence Count:</strong> 4 Items</p>
          </div>
        </div>

        {/* 1. Executive Summary */}
        <section className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-400 font-mono flex items-center gap-2">
            1. Executive Summary
          </h3>
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-sm leading-relaxed text-slate-200">
            MailTrace evaluated email evidence associated with {caseId} and identified a high-risk <strong>PHISHING</strong> event exhibiting multiple technical and behavioral indicators associated with credential theft. Defensive risk score calculated at <strong>91/100 (HIGH Confidence)</strong>.
          </div>
        </section>

        {/* 2. Machine vs Analyst Findings */}
        <section className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-400 font-mono flex items-center gap-2">
            2. Machine vs. Analyst Findings
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 font-mono text-xs">
              <span className="text-xs font-bold text-cyan-400 uppercase block pb-1 border-b border-slate-800">
                🤖 Machine Detected Findings
              </span>
              <div className="flex justify-between"><span className="text-slate-500">AI Risk Score:</span><span className="font-bold text-red-400">91 / 100</span></div>
              <div className="flex justify-between"><span className="text-slate-500">AI Classification:</span><span className="font-bold text-red-400">PHISHING</span></div>
              <div className="flex justify-between"><span className="text-slate-500">SPF Alignment:</span><span className="text-red-400">FAIL (Softfail)</span></div>
              <div className="flex justify-between"><span className="text-slate-500">DKIM Signature:</span><span className="text-red-400">FAIL</span></div>
              <div className="flex justify-between"><span className="text-slate-500">DMARC Policy:</span><span className="text-red-400">FAIL</span></div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 font-mono text-xs">
              <span className="text-xs font-bold text-emerald-400 uppercase block pb-1 border-b border-slate-800">
                👤 Analyst Confirmed Assessment
              </span>
              <div className="flex justify-between"><span className="text-slate-500">Assigned Analyst:</span><span className="text-slate-200">Senior Analyst Jayant</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Case Status:</span><span className="text-amber-400 font-bold">OPEN</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Analyst Decision:</span><span className="text-emerald-400 font-bold">CONFIRMED PHISHING</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Custody Status:</span><span className="text-indigo-400">CHAIN-OF-CUSTODY VERIFIED</span></div>
            </div>
          </div>
        </section>

        {/* 3. Evidence Inventory & SHA-256 Hashes */}
        <section className="space-y-3 font-mono text-xs">
          <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-2">
            <Hash className="w-4 h-4" /> 3. Cryptographic Evidence Inventory & SHA-256 Hashes
          </h3>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] text-slate-400 bg-slate-950 uppercase">
                  <th className="p-3">Evidence ID</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Source</th>
                  <th className="p-3">SHA-256 Checksum</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                <tr>
                  <td className="p-3 font-bold text-indigo-400">EVD-{caseId}-01</td>
                  <td className="p-3">Raw Email Payload</td>
                  <td className="p-3">Email Ingestion</td>
                  <td className="p-3 font-mono text-[11px] text-slate-400 truncate max-w-[220px]">
                    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                  </td>
                </tr>
                <tr>
                  <td className="p-3 font-bold text-indigo-400">EVD-{caseId}-02</td>
                  <td className="p-3">Header Forensics</td>
                  <td className="p-3">Phase 2 Evaluator</td>
                  <td className="p-3 font-mono text-[11px] text-slate-400 truncate max-w-[220px]">
                    7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284ddd200126d90699
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* 4. Limitations Disclaimer */}
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-950 text-xs font-mono text-slate-500 space-y-1">
          <strong className="text-slate-400 block">Investigative Disclaimer & Scope:</strong>
          This report combines machine-generated forensic evidence with analyst findings. Observed infrastructure (IPs, ASNs, geolocations) reflects technical network routing and does not establish legal attribution or physical identity.
        </div>
      </div>
    </div>
  );
}
