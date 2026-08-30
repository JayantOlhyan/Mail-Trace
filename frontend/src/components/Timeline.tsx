'use client';

import React, { useState } from 'react';
import { TimelineEvent } from '@/types';
import { Clock, Filter, Calendar } from 'lucide-react';

interface TimelineProps {
  events: TimelineEvent[];
}

export function Timeline({ events }: TimelineProps) {
  const [filter, setFilter] = useState<'24h' | '7d' | '30d' | 'all'>('all');

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
          <Clock className="w-4 h-4 text-indigo-400" />
          Investigation Chronological Timeline
        </h3>

        {/* Filter intervals */}
        <div className="flex items-center space-x-1 bg-slate-950 px-2 py-1 rounded border border-slate-800 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          {(['24h', '7d', '30d', 'all'] as const).map((interval) => (
            <button
              key={interval}
              onClick={() => setFilter(interval)}
              className={`px-2 py-0.5 rounded uppercase font-mono ${
                filter === interval
                  ? 'bg-indigo-600 text-white font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {interval}
            </button>
          ))}
        </div>
      </div>

      <div className="relative pl-6 border-l-2 border-slate-800 space-y-6">
        {events.length === 0 ? (
          <p className="text-xs text-slate-500 font-mono py-4">No chronological events recorded for this interval.</p>
        ) : (
          events.map((event) => (
            <div key={event.id} className="relative group">
              {/* Dot */}
              <div className="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full bg-indigo-500 border-2 border-slate-950 group-hover:scale-125 transition-transform" />

              <div className="bg-slate-950 border border-slate-800/80 rounded-lg p-3.5 space-y-1 font-mono text-xs">
                <div className="flex items-center justify-between text-slate-400">
                  <span className="flex items-center space-x-1 text-slate-400 font-bold">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{event.timestamp}</span>
                  </span>
                  <span className="px-2 py-0.5 rounded bg-indigo-950/60 text-indigo-300 border border-indigo-800/60 uppercase font-bold text-[10px]">
                    {event.category}
                  </span>
                </div>
                <h4 className="font-bold text-slate-200 text-sm mt-1">{event.title}</h4>
                <p className="text-slate-400 font-sans text-xs">{event.description}</p>
                {event.entity_reference && (
                  <p className="text-[11px] text-slate-500 pt-1">
                    Ref: <span className="text-slate-400">{event.entity_reference}</span>
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
