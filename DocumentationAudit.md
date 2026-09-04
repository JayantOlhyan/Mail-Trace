# Documentation Audit

## Verified
- **Tech Stack**: Next.js 14, React 19, Tailwind CSS, Python 3.9+, FastAPI, SQLAlchemy 2.0 Async, aiosqlite, pytest.
- **Security Mechanisms**: Implemented SSRF protection (`backend/app/security/ssrf.py`) and HTML AST Sanitization (`backend/app/security/sanitizer.py`).
- **Data Integrity**: SHA-256 Hashing of `.eml` files and ZIP package exporting with `manifest.json`.
- **Database Architecture**: Comprehensive SQLite/SQLAlchemy schema across 5 core analysis phases.
- **API**: Comprehensive FastAPI routing matching the phase-based ingestion pipeline. E2E pipeline is covered by robust pytest integration tests.

## Incomplete / Partially Implemented
- **AI Models**: Threat classification relies on a deterministic fallback model (`deterministic-v1`). LLM-based prompt integration appears mocked or planned.
- **External Intelligence Enrichment**: Geolocation, Domain Intelligence, and IP Intelligence schemas exist, but `test_phase4_enrichment.py` and API health checks suggest external providers degrade to mocks without live API keys.

## Missing Documentation
- **Docker / Self-Hosting**: No `Dockerfile` or `docker-compose.yml` exists, yet deployment is implicitly expected.
- **Frontend Architecture**: The `plan.md` outlines a "Cinematic Scrolling UX Revamp", but the frontend directory lacks structural documentation mapping Next.js `(workspace)` and `(tour)` routing flows for a new developer.

## Technical Risks
- **SQLite Concurrency**: Asynchronous SQLite (`aiosqlite`) is utilized, which can bottleneck under high concurrency if multiple analysts submit large 20MB `.eml` payloads simultaneously.
- **Absence of Background Queues**: Ingestion happens synchronously on the FastAPI thread. Long-running tasks (parsing, external enrichment, graph generation) risk timing out the HTTP connection.

## Recommended Next Documentation
- Create a `DOCKER.md` or updated `DEPLOYMENT.md` once containerization is introduced.
- Document the process for plugging in custom ML models (e.g., replacing `deterministic-v1` with a custom HuggingFace or OpenAI service).
- Add frontend UI architectural documentation covering State Management and the `(workspace)` vs `(tour)` Next.js App Router domains.
