# MailTrace — Smart India Hackathon (SIH 2026) 3-5 Minute Demo Guide

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
