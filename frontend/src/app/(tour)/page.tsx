import { TourNavigation } from './components/TourNavigation';
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

export default function TourPage() {
  return (
    <main className="relative w-full overflow-hidden bg-slate-50 dark:bg-slate-950">
      {/* Ambient glowing background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-100/50 dark:bg-blue-900/20 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-purple-900/10 blur-[150px]" />
      </div>

      <TourNavigation />
      
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 [&>*:not(:first-child)]:-mt-[100vh]">
        <IncidentScene />
        <ProductRevealScene />
        <IngestionScene />
        <DetectionScene />
        <ExplainabilityScene />
        <HeaderForensicsScene />
        <RelayTraceScene />
        <InfrastructureScene />
        <InvestigationGraphScene />
        <CampaignScene />
        <AnalystScene />
        <EvidenceScene />
        <ReportScene />
        <FinalScene />
      </div>
    </main>
  );
}
