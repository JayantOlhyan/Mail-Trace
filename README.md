<p align="center">
  <img src="docs/assets/logo.jpg" alt="ThreatTrace AI Logo" width="400" />
</p>

<h1 align="center">ThreatTrace AI ✉️🔍🛡️</h1>

<p align="center">
  <b>AI-Powered Email Threat Detection & Forensic Intelligence Platform</b><br />
  <i>Smart India Hackathon (SIH) 2026 — Problem Statement 106</i>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT"></a>
  <a href="https://github.com/JayantOlhyan/ThreatTrace-AI"><img src="https://img.shields.io/badge/Build-Passing-brightgreen.svg" alt="Build Status"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python 3.9+"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg" alt="FastAPI"></a>
  <a href="https://nextjs.org"><img src="https://img.shields.io/badge/Next.js-14-black.svg" alt="Next.js 14"></a>
  <a href="ARCHITECTURE.md"><img src="https://img.shields.io/badge/Phase_9-SIH_Production_Ready-success.svg" alt="Phase 9 Ready"></a>
</p>

---

## 🎯 Overview

**ThreatTrace AI** is an enterprise-grade forensic intelligence and email threat detection platform built specifically for cybersecurity analysts and incident responders. Designed for **SIH 2026 Problem Statement 106**, ThreatTrace AI goes beyond simple spam/phishing classification by answering key investigation questions:

- **Why is this email suspicious?**
- **How did it reach the recipient?**
- **What infrastructure was involved?**
- **What is the probable origin infrastructure?**
- **Is this infrastructure connected to previous incidents or campaigns?**

---

## 🌟 Key Features

- **📧 RFC 5322 MIME & Header Parser**: Full MIME decomposition, multi-part attachment extraction, and ordered Received hop chain analysis.
- **🛡️ SPF / DKIM / DMARC Verification**: Cryptographic email authentication and spoofing detection.
- **📍 Origin & Relay Tracing**: Distinguishes *Observed Origin IP* from *Probable Origin Infrastructure* with confidence scoring.
- **🧠 AI & NLP Threat Detection**: Identifies social engineering, urgency tactics, credential harvesting, and Business Email Compromise (BEC).
- **⚡ Centralized Risk Engine**: Defensive 0–100 threat severity scoring with explainable evidence binding.
- **🔗 Bounded Investigation Graph**: Entity resolution connecting emails, IP subnets, lookalike domains, and campaign candidates (`CMP-xxxxxx`).
- **🖥️ SOC Workspace**: Modern Next.js 14 Web UI with interactive graph visualizations, timeline analysis, and analyst decision logs.
- **📜 Forensic Reporting & Cryptographic Export**: Generates PDF forensic reports and downloadable `.zip` evidence packages containing `manifest.json` with SHA-256 evidence hashes.
- **🛡️ Hardened Security & SSRF Protection**: Outbound IP validation (`backend/app/security/ssrf.py`) and HTML AST sanitization (`backend/app/security/sanitizer.py`).

---

## 📚 Documentation

- 📐 **[ARCHITECTURE.md](ARCHITECTURE.md)** — System Pipeline & Module Design
- 🔌 **[API.md](API.md)** — Complete REST API Specification
- 🛡️ **[SECURITY.md](SECURITY.md)** — SSRF Protection & HTML Sanitization Guidelines
- 🚀 **[DEPLOYMENT.md](DEPLOYMENT.md)** — Local Setup & Server Running Instructions
- 🏆 **[DEMO.md](DEMO.md)** — SIH 2026 3-5 Minute Presentation Workflow
- ⚙️ **[ENVIRONMENT.md](ENVIRONMENT.md)** — Environment Variables Reference
- ⚠️ **[LIMITATIONS.md](LIMITATIONS.md)** — Scope Boundaries & Technical Limitations

---

## ⚡ Quickstart

### Running Backend API (FastAPI)
```bash
cd backend
PYTHONPATH=. venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Running Frontend UI (Next.js)
```bash
cd frontend
npm run dev -- -p 3002
```

### Running Test Suite
```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/ -v
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
