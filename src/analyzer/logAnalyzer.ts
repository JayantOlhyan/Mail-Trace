import { SecurityEvent, ThreatAnalysisResult, ThreatSeverity } from "../types/threat.js";

export class LogAnalyzer {
  public parseLogLine(rawLog: string): SecurityEvent {
    const timestamp = new Date().toISOString();
    const id = `evt_${Math.random().toString(36).substring(2, 9)}`;
    
    // Basic heuristic parser for IP and event extraction
    const ipMatch = rawLog.match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/);
    const sourceIp = ipMatch ? ipMatch[0] : "127.0.0.1";

    let eventType = "UNKNOWN_LOG_ENTRY";
    if (/failed|denied|unauthorized|invalid/i.test(rawLog)) {
      eventType = "AUTH_FAILURE";
    } else if (/sudo|privilege|root|admin/i.test(rawLog)) {
      eventType = "PRIVILEGE_EVAL";
    } else if (/exec|spawn|shell|cmd/i.test(rawLog)) {
      eventType = "COMMAND_EXECUTION";
    }

    return {
      id,
      timestamp,
      sourceIp,
      eventType,
      payload: { rawText: rawLog },
      rawLog
    };
  }

  public analyzeEvent(event: SecurityEvent): ThreatAnalysisResult {
    let score = 10;
    let severity = ThreatSeverity.LOW;
    let threatType = "BENIGN_ACTIVITY";
    const recommendedActions: string[] = ["Monitor standard activity"];

    if (event.eventType === "AUTH_FAILURE") {
      score = 65;
      severity = ThreatSeverity.MEDIUM;
      threatType = "SUSPICIOUS_AUTHENTICATION_ATTEMPT";
      recommendedActions.push("Enforce rate limiting on auth endpoints", "Check for credential stuffing");
    } else if (event.eventType === "PRIVILEGE_EVAL") {
      score = 85;
      severity = ThreatSeverity.HIGH;
      threatType = "POTENTIAL_PRIVILEGE_ESCALATION";
      recommendedActions.push("Audit user permissions", "Revoke active session token");
    } else if (event.eventType === "COMMAND_EXECUTION" && /rm -rf|eval|base64|curl|wget/i.test(event.rawLog)) {
      score = 95;
      severity = ThreatSeverity.CRITICAL;
      threatType = "REMOTE_CODE_EXECUTION_OR_MALICIOUS_SCRIPT";
      recommendedActions.push("Isolate target host immediately", "Trigger automated incident response playbook");
    }

    return {
      eventId: event.id,
      severity,
      score,
      threatType,
      summary: `Analyzed log event '${event.id}': Detected ${threatType} with Threat Score ${score}/100.`,
      recommendedActions
    };
  }
}
