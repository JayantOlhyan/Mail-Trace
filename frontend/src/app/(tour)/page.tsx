'use client';

import { useState } from 'react';
import { TourNavigation, SCENES } from './components/TourNavigation';
import { TourProgressNav } from './components/TourProgressNav';
import { ParticlesBackground } from './components/ParticlesBackground';

import { IncidentScene } from './components/IncidentScene';
import { ProductRevealScene } from './components/ProductRevealScene';
import { IngestionScene } from './components/IngestionScene';
import { DetectionScene } from './components/DetectionScene';
import { ExplainabilityScene } from './components/ExplainabilityScene';
import { HeaderForensicsScene } from './components/HeaderForensicsScene';
import { RelayTraceScene } from './components/RelayTraceScene';
import { InfrastructureScene } from './components/InfrastructureScene';
import { InvestigationGraphScene } from './components/InvestigationGraphScene';
import { CampaignScene } from './components/CampaignScene';
import { AnalystScene } from './components/AnalystScene';
import { EvidenceScene } from './components/EvidenceScene';
import { ReportScene } from './components/ReportScene';
import { FinalScene } from './components/FinalScene';

const SCENE_COMPONENTS = [
  IncidentScene,
  ProductRevealScene,
  IngestionScene,
  DetectionScene,
  ExplainabilityScene,
  HeaderForensicsScene,
  RelayTraceScene,
  InfrastructureScene,
  InvestigationGraphScene,
  CampaignScene,
  AnalystScene,
  EvidenceScene,
  ReportScene,
  FinalScene,
];

export default function TourPage() {
  const [activeIndex, setActiveIndex] = useState(0);

  const ActiveComponent = SCENE_COMPONENTS[activeIndex];

  return (
    <main className="relative w-full h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      
      <ParticlesBackground />
      
      {/* Ambient glowing background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-50">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[60%] rounded-full bg-blue-400/20 dark:bg-blue-900/30 blur-[120px]" />
        <div className="absolute top-[20%] right-[-10%] w-[50%] h-[60%] rounded-full bg-purple-400/20 dark:bg-purple-900/20 blur-[150px]" />
        <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[60%] rounded-full bg-emerald-400/20 dark:bg-emerald-900/20 blur-[150px]" />
      </div>

      <TourNavigation activeIndex={activeIndex} onSelect={setActiveIndex} />
      <TourProgressNav activeIndex={activeIndex} onSelect={setActiveIndex} />
      
      {/* Scene Container - key forces unmount/remount so useScrollReveal restarts */}
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-full flex items-center justify-center">
        <ActiveComponent key={activeIndex} />
      </div>
    </main>
  );
}
