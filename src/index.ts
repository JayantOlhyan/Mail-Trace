import { LogAnalyzer } from "./analyzer/logAnalyzer.js";
export * from "./types/threat.js";
export * from "./analyzer/logAnalyzer.js";

export class ThreatTraceAI {
  private analyzer: LogAnalyzer;

  constructor() {
    this.analyzer = new LogAnalyzer();
  }

  public processLog(rawLog: string) {
    const event = this.analyzer.parseLogLine(rawLog);
    return this.analyzer.analyzeEvent(event);
  }
}

export default ThreatTraceAI;
