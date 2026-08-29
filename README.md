<p align="center">
  <img src="docs/assets/logo.jpg" alt="MailTrace Logo" width="400" />
</p>

<h1 align="center">MailTrace ✉️🔍🛡️</h1>

<p align="center">
  <b>AI-Powered Email Threat Detection & Forensic Intelligence Platform</b><br />
  <i>Smart India Hackathon (SIH) 2026 — Problem Statement 106</i>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT"></a>
  <a href="https://github.com/JayantOlhyan/Mail-Trace"><img src="https://img.shields.io/badge/Build-Passing-brightgreen.svg" alt="Build Status"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python 3.9+"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg" alt="FastAPI"></a>
  <a href="https://nextjs.org"><img src="https://img.shields.io/badge/Next.js-14-black.svg" alt="Next.js 14"></a>
</p>

---

## 🎯 Overview

**MailTrace** is an enterprise-grade forensic intelligence and email threat detection platform built specifically for cybersecurity analysts and incident responders. Designed for **SIH 2026 Problem Statement 106**, MailTrace goes beyond simple spam/phishing classification by answering key investigation questions:

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
- **🔒 SSRF & Zero-Execution Attachment Safety**: Passive URL metadata analysis and SHA-256 evidence hashing without malicious attachment execution.
- **📋 Forensic PDF Reports**: Chain-of-custody compliant evidence exports for security operations center (SOC) analysts.

---

## 📂 Core Forensic Pipeline

```mermaid
graph TD
    A[Raw .eml Upload] --> B[MIME & Header Ingestor]
    B --> C[RFC 5322 Parser & HTML Sanitizer]
    C --> D[SPF / DKIM / DMARC Evaluator]
    D --> E[Relay Hop & Origin Tracing]
    E --> F[Deterministic Rules + NLP AI Detector]
    F --> G[Centralized Risk Engine (0-100)]
    G --> H[PostgreSQL Graph Correlator]
    H --> I[Case Management & Forensic PDF Report]
```

---

## 🚀 Quick Start (Backend Engine)

### Prerequisites

- Python 3.9+
- pip & venv

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/JayantOlhyan/Mail-Trace.git
cd Mail-Trace

# Create virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run PyTest suite
PYTHONPATH=backend pytest backend/tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git checkout -b feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
