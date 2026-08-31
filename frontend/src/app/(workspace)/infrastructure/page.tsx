'use client';

import React from 'react';
import { Network, Server, Globe, Shield, AlertTriangle } from 'lucide-react';

export default function InfrastructurePage() {
  const sampleClusters = [
    {
      id: 'INFRA-004',
      name: 'Bulletproof Host AS12345 Cluster',
      asn: 'AS12345',
      org: 'Bulletproof Hosting Ltd',
      location: 'Frankfurt, Germany',
      ips_count: 5,
      domains_count: 3,
      confidence: 92,
    },
    {
      id: 'INFRA-009',
      name: 'Cloudflare Shared Proxy Pool',
      asn: 'AS13335',
      org: 'Cloudflare, Inc.',
      location: 'Global CDN',
      ips_count: 14,
      domains_count: 12,
      confidence: 15, // Low correlation score due to common infrastructure suppression
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-4">
        <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Network className="w-5 h-5 text-cyan-400" /> Technical Infrastructure Intelligence
        </h1>
        <p className="text-xs text-slate-600 dark:text-slate-400 font-mono mt-0.5">
          Observed Origin IPs, ASNs, Domains & Infrastructure Clusters
        </p>
      </div>

      {/* Disclaimers */}
      <div className="p-4 rounded-xl border border-cyan-900/40 bg-cyan-950/20 text-cyan-200 text-xs font-mono flex items-start space-x-3">
        <AlertTriangle className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
        <div>
          <strong className="block font-bold">Infrastructure Attribution Principle:</strong>
          Infrastructure ownership, ASN classification, or geolocation data represents technical routing intelligence and does NOT establish physical location or personal identity of an attacker.
        </div>
      </div>

      {/* Clusters List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sampleClusters.map((cluster) => (
          <div key={cluster.id} className="bg-slate-100/80 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-800">
                {cluster.id}
              </span>
              <span className="text-xs font-mono text-slate-600 dark:text-slate-400">Correlation: {cluster.confidence}%</span>
            </div>

            <h3 className="font-bold text-slate-900 dark:text-slate-100 text-base">{cluster.name}</h3>

            <div className="grid grid-cols-2 gap-3 pt-2 font-mono text-xs text-slate-700 dark:text-slate-300 border-t border-slate-200 dark:border-slate-800">
              <div>
                <span className="text-slate-500 block text-[10px]">ASN:</span>
                <span>{cluster.asn}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Organization:</span>
                <span>{cluster.org}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Location:</span>
                <span>{cluster.location}</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px]">Entities:</span>
                <span>{cluster.ips_count} IPs • {cluster.domains_count} Domains</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
