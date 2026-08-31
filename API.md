# MailTrace — REST API Reference Specification
## SIH 2026 Problem Statement 106

All endpoints are hosted under the base prefix `/api/v1`.

---

## 1. System Health & Probes

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/system/health` | Multi-subsystem health check (API, Database, AI Engine, Intelligence) |
| `GET` | `/system/live` | Kubernetes/container liveness probe |
| `GET` | `/system/ready` | Kubernetes/container readiness probe |
| `GET` | `/system/metrics` | Measured classification metrics (Precision, Recall, F1, Accuracy) |

---

## 2. Ingestion & Email APIs

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/emails/upload` | Upload raw `.eml` evidence file (max 10MB) |
| `GET` | `/emails/{id}` | Get canonical normalized email object |
| `GET` | `/emails/{id}/headers` | Get raw and structured email headers |
| `GET` | `/emails/{id}/indicators` | Get extracted IOC indicators (IPs, domains, URLs) |

---

## 3. Forensics & Threat Assessment

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/emails/{id}/forensics` | Trigger Phase 2 header forensics & auth evaluation |
| `POST` | `/emails/{id}/threat-analysis` | Trigger Phase 3 multi-signal AI threat detection |

---

## 4. Graph & Campaign Correlation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/emails/{id}/graph` | Generate bounded 2-hop investigation graph |
| `GET` | `/campaigns` | List correlated campaign candidates |

---

## 5. Reports & Evidence Packages

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/cases/{case_id}/reports` | Generate structured forensic report |
| `GET` | `/reports/{report_id}/package` | Download zip evidence package with SHA-256 manifest |
| `POST` | `/demo/reset` | Reset demo environment state |
