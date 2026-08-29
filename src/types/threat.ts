export enum ThreatSeverity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL"
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  sourceIp: string;
  user?: string;
  eventType: string;
  payload: Record<string, unknown>;
  rawLog: string;
}

export interface ThreatAnalysisResult {
  eventId: string;
  severity: ThreatSeverity;
  score: number; // 0 - 100
  threatType: string;
  summary: string;
  recommendedActions: string[];
  reconstructedTimeline?: string[];
}
