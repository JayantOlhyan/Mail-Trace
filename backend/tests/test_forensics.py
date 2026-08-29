import os
import pytest
from app.ingestion.eml_ingestor import EmlIngestor
from app.forensics.auth_evaluator import AuthEvaluator
from app.forensics.hop_analyzer import HopAnalyzer
from app.forensics.models import AuthStatus

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

def get_sample(filename: str):
    path = os.path.join(SAMPLES_DIR, filename)
    return EmlIngestor.ingest_file_path(path)

def test_legitimate_forensics_evaluation():
    parsed = get_sample("legitimate.eml")
    verdict = AuthEvaluator.evaluate(parsed)

    assert verdict.spf.status == AuthStatus.PASS
    assert verdict.dmarc.status == AuthStatus.PASS
    assert verdict.spoofing.is_display_name_spoofed == False
    assert verdict.spoofing.is_reply_to_mismatched == False
    assert verdict.spoofing.is_return_path_mismatched == False
    assert verdict.overall_auth_risk_score == 0

def test_spoofed_forensics_evaluation():
    parsed = get_sample("spoofed.eml")
    verdict = AuthEvaluator.evaluate(parsed)

    # Display Name Spoofing check
    assert verdict.spoofing.is_display_name_spoofed == True
    assert verdict.spoofing.impersonated_name == "CEO John Doe"

    # Mismatch checks
    assert verdict.spoofing.is_reply_to_mismatched == True
    assert verdict.spoofing.is_return_path_mismatched == True
    assert len(verdict.spoofing.reasons) >= 3

    # Risk score contribution check
    assert verdict.overall_auth_risk_score >= 70

def test_hop_analyzer_origin_ip():
    parsed = get_sample("spoofed.eml")
    hop_result = HopAnalyzer.analyze(parsed)

    assert hop_result.total_hops == 3
    assert hop_result.untrusted_hops_count == 2
    # Hop 1 (earliest reliable public IP) should be 185.220.101.5
    assert hop_result.observed_origin_ip == "185.220.101.5"
    assert "185.220.101.5" in hop_result.probable_origin_infrastructure
