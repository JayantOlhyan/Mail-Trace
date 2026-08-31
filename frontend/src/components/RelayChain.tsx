import React from 'react';
import { ArrowDown, Server, ShieldAlert } from 'lucide-react';

interface RelayHop {
  hop_index: number;
  from_server?: string;
  by_server?: string;
  ip?: string;
  timestamp?: string;
  is_suspicious?: boolean;
}

interface RelayChainProps {
  hops: RelayHop[];
}

export function RelayChain({ hops }: RelayChainProps) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-200 text-sm tracking-wide flex items-center gap-2">
          <Server className="w-4 h-4 text-indigo-400" />
          Mail Relay & Hop Chain Tracing
        </h3>
        <span className="text-xs font-mono text-slate-400">Ordered Received Headers (First $\rightarrow$ Last)</span>
      </div>

      <div className="space-y-3">
        {hops.map((hop, index) => (
          <React.Fragment key={hop.hop_index}>
            {index > 0 && (
              <div className="flex justify-center my-1 text-slate-600">
                <ArrowDown className="w-4 h-4" />
              </div>
            )}
            <div
              className={`p-3.5 rounded-lg border font-mono text-xs transition-colors ${
                hop.is_suspicious
                  ? 'border-red-800/80 bg-red-950/30 text-red-200'
                  : 'border-slate-800 bg-slate-950/80 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between font-bold mb-1">
                <span className="flex items-center space-x-2">
                  <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    Hop #{hop.hop_index}
                  </span>
                  {hop.is_suspicious && (
                    <span className="flex items-center space-x-1 text-red-400 bg-red-950/80 px-2 py-0.5 rounded border border-red-800">
                      <ShieldAlert className="w-3 h-3" />
                      <span>OBSERVED ORIGIN INFRASTRUCTURE</span>
                    </span>
                  )}
                </span>
                <span className="text-slate-400 font-normal">{hop.timestamp || 'N/A'}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mt-2 pt-2 border-t border-slate-800/50">
                <div>
                  <span className="text-slate-500 block text-[10px]">FROM SERVER</span>
                  <span className="truncate block font-semibold">{hop.from_server || 'Unknown'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">BY SERVER</span>
                  <span className="truncate block">{hop.by_server || 'Unknown'}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">OBSERVED RELAY IP</span>
                  <span className={hop.is_suspicious ? 'text-red-400 font-bold underline' : 'text-slate-200'}>
                    {hop.ip || 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </React.Fragment>
        ))}
      </div>
      
      <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-[10px] font-mono text-slate-500 mt-2 leading-relaxed">
        <span className="font-bold text-slate-400">Disclaimer:</span> Geolocation represents observed sending infrastructure and does not establish the physical location or identity of an attacker.
      </div>
    </div>
  );
}
