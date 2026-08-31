import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ThreatTrace AI — Product Tour',
  description: 'Explore how ThreatTrace AI detects suspicious email, analyzes technical evidence, traces sending infrastructure, correlates related activity, and generates forensic intelligence.',
};

export default function TourLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-blue-900/50">
      {children}
    </div>
  );
}
