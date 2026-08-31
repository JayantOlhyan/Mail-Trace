'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  EmailSummary,
  ThreatAssessment,
  HeaderForensics,
  InvestigationGraph,
} from '@/types';
import { RiskScore } from '@/components/RiskScore';
import { ThreatBadge } from '@/components/ThreatBadge';
import { EvidenceCard } from '@/components/EvidenceCard';
import { HeaderViewer } from '@/components/HeaderViewer';
import { RelayChain } from '@/components/RelayChain';
import { GraphViewer } from '@/components/GraphViewer';
import { Timeline } from '@/components/Timeline';
import { AnalystNotes } from '@/components/AnalystNotes';
import {
  ShieldAlert,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  FileQuestion,
  UserCheck,
  RefreshCw,
  Briefcase,
} from 'lucide-react';
import Link from 'next/link';

export default function EmailInvestigationDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [email, setEmail] = useState<EmailSummary | null>(null);
  const [threat, setThreat] = useState<ThreatAssessment | null>(null);
  const [forensics, setForensics] = useState<HeaderForensics | null>(null);
  const [graph, setGraph] = useState<InvestigationGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [e, t, f, g] = await Promise.all([
          api.getEmailDetail(id),
          api.getEmailThreatAssessment(id),
          api.getEmailForensics(id),
          api.getEmailGraph(id),
        ]);
        setEmail(e);
        setThreat(t);
        setForensics(f);
        setGraph(g);
      } catch (err) {
        console.error('Error loading investigation detail:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  const handleAnalystAction = (action: string) => {
    setActionMessage(`Recorded Analyst Action: "${action}" for ${id}`);
    setTimeout(() => setActionMessage(null), 4000);
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-500 font-mono flex items-center justify-center space-x-2">
        <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
        <span>Loading Evidence Workspace for {id}...</span>
      </div>
    );
  }

  if (!email || !threat || !forensics || !graph) {
    return (
      <div className="p-12 text-center text-slate-400 font-mono space-y-4">
        <p className="text-lg font-bold text-red-400">Email evidence object {id} could not be loaded.</p>
        <Link href="/investigations" className="text-indigo-400 hover:underline text-xs">
          ← Back to Investigations List
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Top Breadcrumb & Action Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <Link
          href="/investigations"
          className="inline-flex items-center space-x-1 text-xs font-mono text-slate-400 hover:text-slate-100 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to All Investigations</span>
        </Link>

        {actionMessage && (
          <div className="bg-emerald-950/80 border border-emerald-700 text-emerald-300 text-xs px-3 py-1.5 rounded font-mono animate-fade-in flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>{actionMessage}</span>
          </div>
        )}
      </div>

      {/* Hero Header Workspace Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 space-y-6 shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950/80 border border-indigo-800 px-2.5 py-1 rounded">
                ID: {email.id}
              </span>
              <ThreatBadge classification={email.classification} />
              <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                Confidence: <strong className="text-slate-200">{threat.confidence}</strong>
              </span>
            </div>
            <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight leading-tight">
              {email.subject}
            </h1>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 font-mono text-xs text-slate-300">
              <div>
                <span className="text-slate-500 block">Sender From:</span>
                <span className="text-slate-200 font-semibold">{email.sender}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Reply-To Address:</span>
                <span className={forensics.reply_to && forensics.reply_to !== forensics.from_address ? 'text-red-400 font-bold' : 'text-slate-300'}>
                  {forensics.reply_to || 'None'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">Received Timestamp:</span>
                <span className="text-slate-300">{new Date(email.received_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="flex-shrink-0 space-y-3 min-w-[240px]">
            <RiskScore score={email.risk_score} size="lg" />

            {/* Analyst Quick Action Buttons */}
            <div className="pt-2 flex flex-col gap-2 font-mono text-xs">
              <button
                onClick={() => handleAnalystAction('Marked as Malicious')}
                className="w-full bg-red-600/20 hover:bg-red-600 border border-red-500/50 text-red-300 hover:text-white py-1.5 px-3 rounded flex items-center justify-center space-x-1.5 font-semibold transition"
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                <span>Mark as Malicious</span>
              </button>
              <button
                onClick={() => handleAnalystAction('Marked as False Positive')}
                className="w-full bg-emerald-600/20 hover:bg-emerald-600 border border-emerald-500/50 text-emerald-300 hover:text-white py-1.5 px-3 rounded flex items-center justify-center space-x-1.5 font-semibold transition"
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Mark False Positive</span>
              </button>
              <Link
                href="/cases/CASE-2026-0042"
                className="w-full bg-indigo-600/20 hover:bg-indigo-600 border border-indigo-500/50 text-indigo-300 hover:text-white py-1.5 px-3 rounded flex items-center justify-center space-x-1.5 font-semibold transition text-center"
              >
                <Briefcase className="w-3.5 h-3.5" />
                <span>Escalate to Case</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* WHY THREATTRACE AI FLAGGED THIS EMAIL */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Why ThreatTrace AI Flagged This Email
          </h2>
          <span className="text-xs font-mono text-slate-400">
            {threat.findings.length} Evidence-Linked Findings
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {threat.findings.map((finding) => (
            <EvidenceCard key={finding.id} finding={finding} />
          ))}
        </div>
      </div>

      {/* Header Forensics */}
      <HeaderViewer forensics={forensics} />

      {/* Mail Relay Chain */}
      <RelayChain hops={forensics.received_hops} />

      {/* Bounded Investigation Graph */}
      <div className="space-y-3">
        <h2 className="text-lg font-bold text-slate-100">Infrastructure & Entity Investigation Graph</h2>
        <GraphViewer graph={graph} />
      </div>

      {/* Timeline & Analyst Notes Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Timeline
          events={[
            {
              id: 'EVT-01',
              timestamp: '2026-08-28 00:00:00',
              title: 'Lookalike Domain Registered',
              description: 'Domain paypa1-support.com registered via anonymous proxy registrar.',
              category: 'DNS / Domain',
              entity_reference: 'paypa1-support.com',
            },
            {
              id: 'EVT-02',
              timestamp: '2026-08-30 14:22:58',
              title: 'First Relay Hop Observed',
              description: 'Email routed through suspicious origin IP 203.0.113.10 (AS12345).',
              category: 'Network Hop',
              entity_reference: '203.0.113.10',
            },
            {
              id: 'EVT-03',
              timestamp: '2026-08-30 14:23:10',
              title: 'ThreatTrace AI Risk Score Triggered',
              description: 'Evaluation engine scored email 91/100 (PHISHING).',
              category: 'Detection Engine',
              entity_reference: email.id,
            },
          ]}
        />

        <AnalystNotes entityType="EMAIL" entityId={email.id} />
      </div>
    </div>
  );
}
