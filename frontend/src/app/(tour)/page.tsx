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
    <main className="relative w-full overflow-hidden bg-slate-50 dark:bg-slate-950 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]">
      {/* Ambient glowing background - absolute so it scrolls with the page */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-50">
        <div className="absolute top-0 left-[-10%] w-[40%] h-[100vh] rounded-full bg-blue-400/20 dark:bg-blue-900/30 blur-[120px]" />
        <div className="absolute top-[50vh] right-[-10%] w-[50%] h-[100vh] rounded-full bg-purple-400/20 dark:bg-purple-900/20 blur-[150px]" />
        <div className="absolute top-[150vh] left-[10%] w-[40%] h-[100vh] rounded-full bg-indigo-400/20 dark:bg-indigo-900/30 blur-[120px]" />
        <div className="absolute top-[250vh] right-[10%] w-[40%] h-[100vh] rounded-full bg-emerald-400/20 dark:bg-emerald-900/20 blur-[120px]" />
        <div className="absolute top-[350vh] left-[20%] w-[50%] h-[100vh] rounded-full bg-blue-400/20 dark:bg-blue-900/30 blur-[150px]" />
      </div>

      <TourNavigation />
      
      <div className="relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 [&>*:not(:first-child)]:-mt-[150vh]">
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
