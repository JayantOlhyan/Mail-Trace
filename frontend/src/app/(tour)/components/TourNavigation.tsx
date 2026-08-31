'use client';

import Link from 'next/link';

export const SCENES = [
  { id: 'scene-01', label: 'Incident Signal', short: 'Incident', inSidebar: true, sidebarLabel: '01 Incident' },
  { id: 'scene-02', label: 'Threat Intelligence', short: 'Overview', inSidebar: false },
  { id: 'scene-03', label: 'MIME Ingestion', short: 'Ingestion', inSidebar: false },
  { id: 'scene-04', label: 'Multi-Layer Detection', short: 'Detection', inSidebar: true, sidebarLabel: '02 Detect' },
  { id: 'scene-05', label: 'Explainability & Scoring', short: 'Scoring', inSidebar: true, sidebarLabel: '03 Explain' },
  { id: 'scene-06', label: 'Header Forensics', short: 'Headers', inSidebar: true, sidebarLabel: '04 Forensics' },
  { id: 'scene-07', label: 'SMTP Relay Trace', short: 'Relay', inSidebar: true, sidebarLabel: '05 Trace' },
  { id: 'scene-08', label: 'Infrastructure Intelligence', short: 'Infra', inSidebar: false },
  { id: 'scene-09', label: 'Investigation Graph', short: 'Graph', inSidebar: true, sidebarLabel: '06 Correlate' },
  { id: 'scene-10', label: 'Campaign Correlation', short: 'Campaign', inSidebar: false },
  { id: 'scene-11', label: 'Analyst Workspace', short: 'SOC', inSidebar: true, sidebarLabel: '07 Investigate' },
  { id: 'scene-12', label: 'Evidence Preservation', short: 'Evidence', inSidebar: false },
  { id: 'scene-13', label: 'Forensic Report', short: 'Report', inSidebar: true, sidebarLabel: '08 Report' },
  { id: 'scene-14', label: 'SOC Action Plan', short: 'Action', inSidebar: false },
];

interface Props {
  activeIndex: number;
  onSelect: (index: number) => void;
}

export function TourNavigation({ activeIndex, onSelect }: Props) {
  const activeSceneId = SCENES[activeIndex]?.id;
  const sidebarItems = SCENES.filter(s => s.inSidebar);

  return (
    <nav className="fixed left-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-4">
      <div className="text-xs font-mono text-slate-500 mb-4 tracking-widest">THREATTRACE</div>
      {sidebarItems.map((chapter) => {
        // Find if the currently active scene falls under this chapter.
        // We consider a chapter active if the activeIndex is >= this chapter's index 
        // AND < the next chapter's index.
        const chapterIndex = SCENES.findIndex(s => s.id === chapter.id);
        const nextChapterItem = sidebarItems[sidebarItems.findIndex(s => s.id === chapter.id) + 1];
        const nextChapterIndex = nextChapterItem ? SCENES.findIndex(s => s.id === nextChapterItem.id) : SCENES.length;
        
        const isActive = activeIndex >= chapterIndex && activeIndex < nextChapterIndex;

        return (
          <button
            key={chapter.id}
            onClick={() => onSelect(chapterIndex)}
            className={`text-left text-xs font-mono transition-all duration-300 ${
              isActive
                ? 'text-blue-400 font-bold translate-x-2'
                : 'text-slate-600 hover:text-slate-600 dark:text-slate-400 hover:translate-x-1'
            }`}
          >
            {chapter.sidebarLabel}
          </button>
        );
      })}
      <Link 
        href="/workspace"
        className="mt-8 text-xs font-mono text-slate-500 hover:text-slate-700 dark:text-slate-300 transition-colors"
      >
        ← EXIT TOUR
      </Link>
    </nav>
  );
}
