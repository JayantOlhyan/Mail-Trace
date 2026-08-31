# ThreatTrace AI — Smart India Hackathon (SIH 2026) 3-5 Minute Demo Guide

## Golden Demo Workflow (Problem Statement 106)

1. **Dashboard Overview (`http://localhost:3002`)**:
   - Open main dashboard displaying high-level threat score cards, active investigations, and system status badge (`ONLINE`).
2. **Inspect Phishing Case (`EML-2026-8801`)**:
   - Click **Inspect Workspace** on `EML-2026-8801`.
   - Review multi-signal risk score (94/100 - CRITICAL PHISHING).
   - Review Header Forensics & SPF/DKIM/DMARC failure indicators.
3. **Graph & Campaign Correlation**:
   - Expand the Bounded Investigation Graph showing cross-email infrastructure connections (`INFRA-001928`).
   - Highlight the identified Campaign Candidate (`CMP-2026-9041`).
4. **Analyst Case Management**:
   - Switch to Case Workspace (`CASE-2026-0042`).
   - Add analyst note and set decision (`CONFIRMED_MALICIOUS`).
5. **Cryptographic Report & Evidence Export**:
   - Click **Generate Forensic Report**.
   - Preview machine vs analyst findings.
   - Click **Export Evidence Package (.ZIP)** containing `manifest.json` with SHA-256 evidence checksums.
6. **Reset Environment**:
   - Click `[ Reset Demo Environment ]` in the top SIH banner to return system state back to baseline.

---

## 🎤 Presentation Script & Timeline (3-5 Minutes)

### 0:00 — Dashboard Introduction
> "Welcome. This is ThreatTrace AI, an AI-powered email threat detection and forensic intelligence platform built for SIH 2026 Problem Statement 106. ThreatTrace AI continuously evaluates incoming email headers, routing hops, and content for phishing, impersonation, and fraud indicators."

### 0:30 — Suspicious Email Analysis
> "We select our primary high-risk investigation `EML-2026-8801`. This email has a defensive risk score of 91/100 because multiple independent signals—including lookalike domain registration and urgent financial payload language—indicate phishing."

### 1:00 — Header Forensics & Relay hop Tracing
> "By analyzing raw headers, ThreatTrace AI validates sender authentication and reconstructs the hop-by-hop relay path. We verify that SPF, DKIM, and DMARC have all failed, and we trace the path back to the earliest observed sending IP."

### 1:45 — Infrastructure Enrichment
> "We inspect the probable sending infrastructure, geolocating the IP, classifying its hosting provider, and inspecting reverse DNS records. Note that this indicates network routing location and is not a physical claim of the attacker's home."

### 2:15 — Correlation Graph Explorer
> "Opening the Graph Explorer, our correlation engine links this email to shared subnets, lookalike domain servers, and historical indicators, revealing a cluster of overlapping infrastructure."

### 3:00 — Campaign Candidates
> "These related observations are automatically grouped as a campaign candidate. This group maps out the scope of the threat actor's infrastructure across multiple target emails."

### 3:30 — Incident Case Workspace
> "We escalate this to an active Case Workspace, log our notes, and select our analyst verdict—independently from the automated machine classification."

### 4:00 — Report Generation & Evidence Package
> "Finally, we generate a cryptographically signed Forensic Report. We can export this as a PDF, raw JSON, or download the full ZIP Evidence Package containing an immutable manifest of SHA-256 custody hashes for legal compliance."
