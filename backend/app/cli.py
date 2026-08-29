#!/usr/bin/env python3
import sys
import os
import argparse
import time
from app.ingestion.validator import EmailValidator
from app.ingestion.evidence import EvidenceMetadata
from app.parsing.email_parser import EmailParserEngine

def main():
    parser = argparse.ArgumentParser(description="MailTrace Phase 1 Development & Analysis CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze and parse a local .eml email file")
    analyze_parser.add_argument("filepath", type=str, help="Path to raw .eml file")

    args = parser.parse_args()

    if args.command == "analyze":
        filepath = args.filepath
        if not os.path.exists(filepath):
            print(f"Error: File '{filepath}' not found.")
            sys.exit(1)

        start_time = time.time()
        with open(filepath, "rb") as f:
            raw_bytes = f.read()

        filename = os.path.basename(filepath)
        EmailValidator.validate_bytes(raw_bytes, filename)

        evidence_id, sha256_hash, size_bytes = EvidenceMetadata.process_payload(raw_bytes, filename)
        canonical_obj, _ = EmailParserEngine.parse_eml(raw_bytes, evidence_id, filename)

        duration = time.time() - start_time

        from_addr = canonical_obj.identity.from_[0].address if canonical_obj.identity.from_ else "Unknown"
        from_name = canonical_obj.identity.from_[0].display_name if canonical_obj.identity.from_ else ""
        from_str = f"{from_name} <{from_addr}>" if from_name else from_addr

        to_addrs = ", ".join([a.address for a in canonical_obj.identity.to]) or "Unknown"

        print("\nMailTrace Email Ingestion & Parsing Engine")
        print("------------------------------------------")
        print(f"File:        {filename}")
        print(f"SHA-256:     {sha256_hash}")
        print(f"Evidence ID: {evidence_id}")
        print(f"\nMessage-ID:  {canonical_obj.identity.message_id or 'None'}")
        print(f"From:        {from_str}")
        print(f"To:          {to_addrs}")
        print(f"Subject:     {canonical_obj.content.subject}")
        print(f"\nHeader count:   {len(canonical_obj.headers.raw)}")
        print(f"Received hops:  {len(canonical_obj.headers.received)}")
        print(f"URLs:           {len(canonical_obj.indicators.urls)}")
        print(f"Domains:        {len(canonical_obj.indicators.domains)}")
        print(f"IP addresses:   {len(canonical_obj.indicators.ips)}")
        print(f"Attachments:    {len(canonical_obj.attachments)}")
        print(f"\nStatus:         PARSED ({duration:.3f}s)\n")

if __name__ == "__main__":
    main()
