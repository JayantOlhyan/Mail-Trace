# MailTrace — System Architecture & Forensic Intelligence Blueprint
## SIH 2026 Problem Statement 106

MailTrace is an AI-powered email threat detection, header forensics, infrastructure geolocation, and campaign correlation platform.

---

## 1. System Pipeline Architecture

```
                       ┌────────────────────────────┐
                       │   UNTRUSTED RAW EMAIL     │
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                       ┌────────────────────────────┐
                       │  Phase 1: Ingestion & MIME │
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                       ┌────────────────────────────┐
                       │ Phase 2: Header Forensics  │
                       │ & SPF/DKIM/DMARC Evaluator │
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                       ┌────────────────────────────┐
                       │  Phase 3: AI Multi-Signal  │
                       │   Threat & Risk Engine     │
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                       ┌────────────────────────────┐
                       │  Phase 4: Infrastructure   │
                       │  & Geolocation Intelligence│
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                       ┌────────────────────────────┐
                       │  Phase 5: Investigation    │
                       │ Graph & Campaign Correlation│
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                       ┌────────────────────────────┐
                       │  Phase 6 & 7: SOC Workspace│
                       │ & Cryptographic PDF/ZIP    │
                       └────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Backend (Python 3.9+ / FastAPI)
- **FastAPI / Uvicorn**: Asynchronous HTTP/REST API server.
- **SQLAlchemy 2.0 Async / SQLite**: Persistent metadata store for emails, evidence hashes, forensic findings, and case notes.
- **Pydantic v2**: Strict domain schema validation and serialization.

### 2.2 Security & Protection Layer
- **SSRF Guard (`backend/app/security/ssrf.py`)**: Outbound network protection blocking internal CIDRs, loopback (`127.0.0.1`), and cloud metadata (`169.254.169.254`).
- **HTML AST Sanitizer (`backend/app/security/sanitizer.py`)**: HTML parser stripping scripts, iframes, and executable attributes.

### 2.3 Frontend (Next.js 14 / TypeScript / Tailwind CSS)
- **SOC Workspace**: Interactive dashboard, investigation workspace, case manager, interactive SVG graph visualization, and forensic report exporter.

---

## 3. Data Integrity & Chain of Custody
- Every uploaded `.eml` file is hashed immediately upon receipt using SHA-256.
- Raw file evidence is immutable.
- Exported Forensic Packages contain `manifest.json` with cryptographic SHA-256 checksums for legal chain-of-custody verification.
