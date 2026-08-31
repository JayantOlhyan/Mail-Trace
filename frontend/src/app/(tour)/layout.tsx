import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ThreatTrace AI — Product Tour',
  description: 'Explore how ThreatTrace AI detects suspicious email, analyzes technical evidence, traces sending infrastructure, correlates related activity, and generates forensic intelligence.',
};

import { ThemeToggle } from '@/components/ThemeToggle';

export default function TourLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 font-sans selection:bg-blue-900/50">
      <div className="fixed top-6 right-6 z-50">
        <ThemeToggle />
      </div>
      {children}
    </div>
  );
}
