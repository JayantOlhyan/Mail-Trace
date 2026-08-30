import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { Navigation } from '@/components/Navigation';
import { DemoBanner } from '@/components/DemoBanner';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });
const mono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' });

export const metadata: Metadata = {
  title: 'MailTrace — AI Email Forensic Intelligence Platform',
  description: 'Cybersecurity Incident Response & Investigation Workspace for SIH 2026 Problem Statement 106',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${mono.variable} font-sans bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col`}>
        <DemoBanner />
        <div className="flex-1 flex overflow-hidden">
          <Navigation />
          <main className="flex-1 overflow-y-auto min-h-screen bg-slate-950 p-6 md:p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
