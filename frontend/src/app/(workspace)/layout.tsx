import { Navigation } from '@/components/Navigation';
import { DemoBanner } from '@/components/DemoBanner';

export default function WorkspaceLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <DemoBanner />
      <div className="flex-1 flex overflow-hidden">
        <Navigation />
        <main className="flex-1 overflow-y-auto min-h-screen bg-slate-50 dark:bg-slate-950 p-6 md:p-8">
          {children}
        </main>
      </div>
    </>
  );
}
