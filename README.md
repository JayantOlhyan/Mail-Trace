# ThreatTrace AI

> AI-Powered Email Threat Detection & Forensic Intelligence Platform

![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)
![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)
![License MIT](https://img.shields.io/badge/License-MIT-blue.svg)

## Overview

ThreatTrace AI is an enterprise-grade forensic intelligence and email threat detection platform. It is designed to move beyond simple spam classification by deeply analyzing email headers, authenticating origins, geolocating infrastructure, and leveraging deterministic AI rules to assess risk. The platform provides a complete SOC (Security Operations Center) workspace for incident responders to triage emails, trace their origins, and export cryptographically verifiable forensic packages.

**Project Status:** Active development. Fully implements email ingestion, parsing, deterministic threat rules, and SOC workspace visualization. Currently utilizes SQLite and local file storage.

## Why This Project Exists

Security Operation Centers (SOCs) waste hundreds of hours manually deconstructing `.eml` files, traversing `Received` headers, and checking IPs against intelligence feeds. ThreatTrace AI automates the entire manual forensic workflow. It ingests raw evidence files, builds an investigation graph, and outputs structured intelligence, solving the specific requirements of Smart India Hackathon (SIH) 2026 Problem Statement 106.

## Features

- **📧 RFC 5322 MIME & Header Parser**: Full MIME decomposition, multi-part attachment extraction, and ordered `Received` hop chain analysis.
- **🛡️ SPF / DKIM / DMARC Verification**: Cryptographic email authentication and spoofing detection.
- **🧠 Deterministic Threat Engine**: Assesses risk using a multi-signal rule evaluator with fallback baseline capabilities (identifies social engineering, credential harvesting, etc.).
- **🔗 Bounded Investigation Graph**: Entity resolution connecting emails, IP subnets, and lookalike domains.
- **🖥️ SOC Workspace**: Modern Next.js 14 Web UI with interactive graph visualizations, timeline analysis, and analyst decision logs.
- **📜 Forensic Reporting & Cryptographic Export**: Generates PDF forensic reports and downloadable `.zip` evidence packages containing `manifest.json` with SHA-256 evidence hashes for legal chain of custody.
- **🛡️ Hardened Security**: Built-in SSRF protection guarding against internal CIDR/loopback probing, and HTML AST sanitization for safe rendering of suspicious emails.

*(Note: Advanced AI models and external intelligence provider integrations are partially implemented or mocked in current tests).*

## Architecture

ThreatTrace AI uses a decoupled client-server architecture:

```text
User (Analyst)
 ↓
Next.js Frontend (SOC Workspace / Tour)
 ↓
FastAPI REST API
 ↓
Core Engines:
 ├─ MIME Parser
 ├─ Header Forensics
 ├─ Deterministic AI Risk Engine
 └─ Bounded Graph Engine
 ↓
SQLite Database (aiosqlite)
 & Local Evidence Store (SHA-256 Hashed Files)
```

### Forensic Data Flow

```text
Raw Email (.eml) → MIME Parser → Authentication Check (SPF/DKIM/DMARC)
→ AI Threat & Risk Engine → IOC Extraction → Correlation Engine
→ Case Workspace → Forensic Report (PDF/ZIP with manifest.json)
```

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS, PostCSS
- **UI Libraries:** `lucide-react`, `clsx`, `tailwind-merge`

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.9+
- **Database Engine:** SQLite (async via `aiosqlite`)
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic v2
- **Testing:** Pytest, HTTPX

### Infrastructure & Security
- **Data Integrity:** SHA-256 Hashing of uploaded `.eml` files
- **HTML Sanitization:** BeautifulSoup4 and lxml
- **Network Security:** SSRF validation middleware

## Repository Structure

```text
ThreatTrace-AI/
├── backend/               # Python/FastAPI Backend
│   ├── app/
│   │   ├── api/           # FastAPI v1 Routes
│   │   ├── core/          # Config, DB Setup, Logging
│   │   ├── models/        # SQLAlchemy Models
│   │   ├── schemas/       # Pydantic Schemas
│   │   ├── security/      # SSRF & Sanitization logic
│   │   └── threat/        # Risk Engine & Deterministic Rules
│   └── tests/             # Comprehensive Pytest Suite
├── frontend/              # Next.js 14 Frontend
│   └── src/app/
│       ├── (tour)/        # Scrolling UX product tour
│       └── (workspace)/   # SOC Investigation Workspace
├── src/                   # Core CLI & Types
├── evidence_store/        # Local storage for uploaded .eml files
└── threattrace.db         # Default SQLite Database
```

## Prerequisites

- **Node.js** v20+
- **Python** 3.9+
- **npm** or **yarn**

## Local Development

### 1. Clone Repository
```bash
git clone https://github.com/JayantOlhyan/ThreatTrace-AI.git
cd ThreatTrace-AI
```

### 2. Configure Environment
Copy the example environment variables:
```bash
cp .env.example .env
```

### 3. Start the Backend API (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The database (`threattrace.db`) will be automatically created on startup via the lifespan context manager. Evidence files are saved to `./evidence_store`.

### 4. Start the Frontend UI (Next.js)
In a new terminal:
```bash
cd frontend
npm install
npm run dev -- -p 3002
```

## Database

ThreatTrace AI uses SQLite (`threattrace.db`) with `aiosqlite` for asynchronous database operations. The ORM used is SQLAlchemy 2.0.

Key tables and relationships:
- **`evidence`**: Stores uploaded file metadata and SHA-256 hashes.
- **`emails`**: Core entity containing parsed body, headers, and metadata.
- **`received_headers` & `email_addresses` & `urls`**: Extracted IOCs.
- **`threat_analyses` & `threat_signals`**: Determined risk, primary classification, and signals.
- **`graph_nodes` & `graph_edges`**: Investigation entity correlation structure.

## API

The backend exposes a comprehensive REST API. Important endpoints include:

- `GET /api/v1/system/health`: Detailed multi-subsystem health check.
- `POST /api/v1/emails/upload`: Upload & Parse Raw `.eml` file.
- `GET /api/v1/emails/{email_id}`: Fetch normalized canonical email object.
- `POST /api/v1/emails/{email_id}/forensics`: Execute Phase 2 forensic analysis (SPF/DKIM/Relay).
- `POST /api/v1/emails/{email_id}/threat-analysis`: Execute Phase 3 threat risk assessment.
- `GET /api/v1/emails/{email_id}/graph`: Retrieve correlation graph for the evidence.
- `GET /api/v1/reports/{report_id}/package`: Download cryptographic `.zip` export with `manifest.json`.

*(For the complete specification, refer to `API.md`)*

## Security

Security is deeply integrated into the application pipeline:

- **SSRF Mitigation (`app/security/ssrf.py`)**: Strict validation of extracted URLs blocking loopback (`127.0.0.1`), private networks (RFC 1918), and cloud metadata endpoints (`169.254.169.254`).
- **HTML Sanitization (`app/security/sanitizer.py`)**: Analyzes HTML email bodies via BeautifulSoup4 to strip `<script>`, `<iframe>`, and malicious `javascript:` attributes before rendering in the SOC workspace.
- **Cryptographic Hashing**: File uploads are immediately hashed (SHA-256) ensuring evidence integrity and legal chain of custody.

## Testing

The project has a robust Pytest suite ranging from unit tests to End-to-End integration tests.

To run the backend test suite:
```bash
cd backend
PYTHONPATH=. venv/bin/pytest tests/ -v
```

The test suite includes:
- EML parsing tests
- SSRF and Security module tests
- E2E full investigation and cryptographic export pipeline tests (`test_phase8_e2e_integration.py`).

## Known Limitations

- **Database Scale:** Currently uses SQLite which is sufficient for local SOC triage and SIH demonstrations, but not suitable for high-concurrency, enterprise multi-tenant deployments without migrating to PostgreSQL.
- **AI Models:** The system currently relies on a deterministic rule-based threat engine (`deterministic-v1`). LLM or Advanced NLP models for threat assessment are mocked or require integration.
- **External Intelligence:** Integrations with services like VirusTotal, IPinfo, AbuseIPDB, and Shodan are supported via `.env` but rely on graceful degradation to mock data if API keys are absent.
- **Docker/Containerization:** No Dockerfile or `docker-compose.yml` is currently provided in the repository.

## Roadmap

### Completed
- RFC 5322 MIME & Header Parser
- SQLite asynchronous metadata storage
- SSRF and HTML Sanitizer Security Gates
- Cryptographic ZIP Export of evidence
- Deterministic Threat Evaluation Engine

### Planned
- PostgreSQL migration for high-scale enterprise deployments
- Integration of a live LLM/NLP Inference Engine for semantic threat analysis
- Containerized Docker deployment pipeline
- Redis-backed background queues for heavy external API intelligence enrichment

## License

This project is licensed under the [MIT License](LICENSE).

## Author

Jayant Olhyan
