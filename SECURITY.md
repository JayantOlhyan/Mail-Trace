# ThreatTrace AI — Security Architecture & Guidelines

## 1. Input Security & Hostile Content Policy
Every incoming email file is treated as untrusted and potentially hostile:
- **Zero Attachment Execution**: Attachments are stored as raw bytes and analyzed strictly via metadata and SHA-256 hashes. Files are never opened or executed.
- **HTML Sanitization (`backend/app/security/sanitizer.py`)**: All HTML bodies are passed through an AST parser stripping `<script>`, `<iframe>`, `on*` event handlers, and `javascript:` URIs.
- **SSRF Protection (`backend/app/security/ssrf.py`)**: Outbound requests validate target IP addresses against private CIDR blocks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), and cloud metadata (`169.254.169.254`).

## 2. Data Integrity & Cryptography
- Every raw `.eml` upload is assigned an immutable SHA-256 evidence hash upon ingestion.
- Forensic reports export a cryptographic ZIP evidence package containing `manifest.json` with SHA-256 checksums for legal chain-of-custody.

## 3. Strict Attribution Terminology
To maintain legal and forensic accuracy:
- We **NEVER** claim `IP = Attacker` or `Geolocation = Attacker Location`.
- Platform outputs use precise technical phrasing: `"Probable sending infrastructure"`, `"Estimated network location"`, and `"Associated infrastructure domain"`.
