# MailTrace — System Limitations & Scope Boundaries

MailTrace is designed for technical email header forensics, multi-signal threat detection, and infrastructure correlation.

---

## 1. Technical & Intelligence Limitations

1. **IP Geolocation Accuracy**: IP addresses map to network operator registration locations or ISP POPs. Geolocation estimates network infrastructure location, **not** physical sender identity or human attacker location.
2. **VPN / TOR / Proxy Anonymization**: MailTrace identifies when sending infrastructure belongs to public VPN ranges or TOR exit nodes, but cannot look past VPN encryption tunnels without upstream ISP logs.
3. **Cloud & Shared Infrastructure**: High-reputation cloud hosting (AWS, Cloudflare, Google Cloud) can be abused by threat actors. MailTrace applies common infrastructure suppression to prevent false attribution.
4. **Header Spoofing**: Email headers prior to trusted receiving relays can be forged. MailTrace evaluates trust boundaries based on trusted receiving MTAs.
5. **AI Threat Signals**: Risk scores are heuristic threat signals intended for security analyst triage, not legally binding proof of criminal intent.

---

## 2. Mandatory Scope Rules
- **No Attachment Execution**: Attachments are sanitized and cataloged by hash; code is never executed.
- **No Automatic Attacker Claims**: MailTrace never makes claims such as `"IP = Attacker"` or `"Location = Attacker Home"`.
