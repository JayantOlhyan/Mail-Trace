'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

const CHAPTERS = [
  { id: 'scene-01', label: '01 Incident' },
  { id: 'scene-04', label: '02 Detect' },
  { id: 'scene-05', label: '03 Explain' },
  { id: 'scene-06', label: '04 Forensics' },
  { id: 'scene-07', label: '05 Trace' },
  { id: 'scene-09', label: '06 Correlate' },
  { id: 'scene-11', label: '07 Investigate' },
  { id: 'scene-13', label: '08 Report' },
];

export function TourNavigation() {
  const [activeId, setActiveId] = useState<string>('');

  useEffect(() => {
    const handleScroll = () => {
      // Find the most visible chapter section
      let current = '';
      for (const chapter of CHAPTERS) {
        const el = document.getElementById(chapter.id);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= window.innerHeight / 2 && rect.bottom >= window.innerHeight / 2) {
            current = chapter.id;
          }
        }
      }
      if (current && current !== activeId) {
        setActiveId(current);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [activeId]);

  return (
    <nav className="fixed left-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-4">
      <div className="text-xs font-mono text-slate-500 mb-4 tracking-widest">THREATTRACE</div>
      {CHAPTERS.map((chapter) => (
        <a
          key={chapter.id}
          href={`#${chapter.id}`}
          className={`text-xs font-mono transition-all duration-300 ${
            activeId === chapter.id
              ? 'text-blue-400 font-bold translate-x-2'
              : 'text-slate-600 hover:text-slate-600 dark:text-slate-400'
          }`}
        >
          {chapter.label}
        </a>
      ))}
      <Link 
        href="/workspace"
        className="mt-8 text-xs font-mono text-slate-500 hover:text-slate-700 dark:text-slate-300 transition-colors"
      >
        ← EXIT TOUR
      </Link>
    </nav>
  );
}
