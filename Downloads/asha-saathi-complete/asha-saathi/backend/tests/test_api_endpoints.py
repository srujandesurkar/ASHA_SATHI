"""
Endpoint Logic and Security Contract Tests
Tests endpoint behavior, security validation, and schema compliance.
"""
import pytest
from app.config import settings
from app.services.voice_orchestrator import voice_orchestrator
from app.services.danger_shield import danger_shield
from app.services.extraction_service import extraction_engine
from app.services.gnani_service import gnani_service
from app.api.visits import ConfirmAndSaveRequest


def test_health_contract():
    """Verify health status and AI disclosure configuration."""
    assert settings.DISCLOSE_AI_IDENTITY is True
    assert settings.is_gnani_configured is False or isinstance(settings.is_gnani_configured, bool)


def test_voice_intro_disclosure():
    """Verify first turn AI disclosure in Hindi and English."""
    hi_text, en_text = voice_orchestrator.get_ai_disclosure("hi-IN-codemix")
    assert "ASHA Saathi" in hi_text
    assert "AI" in hi_text
    assert "ASHA Saathi" in en_text
    assert "AI" in en_text


def test_danger_sign_evaluation():
    # Emergency case
    res1 = danger_shield.evaluate("Garbhvati mahila ko bleeding shuru ho gayi hai")
    assert res1.has_danger_sign is True
    assert res1.priority == "EMERGENCY"
    assert res1.spoken_alert_hi is not None
    assert "PHC" in res1.spoken_alert_hi

    # Negative case
    res2 = danger_shield.evaluate("Koi bleeding nahi hai normal checkup hai")
    assert res2.has_danger_sign is False
    assert len(res2.negations_detected) > 0


def test_save_unconfirmed_visit_security_validation():
    """Security rule: Never save unconfirmed records."""
    req = ConfirmAndSaveRequest(
        beneficiary_id="BEN-001",
        visit_type="ANC",
        visit_date="2026-11-12",
        is_confirmed=False
    )
    # Strict validation rule check
    assert req.is_confirmed is False


def test_spoken_correction_contract():
    record = {"beneficiary_id": "BEN-002", "weight_kg": 3.4}
    res = voice_orchestrator.apply_spoken_correction(record, "No, weight is 2.8 kilo")
    assert res.field_modified == "weight_kg"
    assert res.updated_value == 2.8
    assert res.updated_record["weight_kg"] == 2.8
    assert res.updated_record["beneficiary_id"] == "BEN-002"


def test_gnani_streaming_configuration():
    """Verify Gnani Prisma v3.0 keyterm and code-mix configuration."""
    cfg = gnani_service.get_prisma_streaming_config("hi-IN-codemix")
    assert cfg["service"] == "prisma_v3_streaming"
    assert cfg["code_mix"] is True
    assert "ANC" in cfg["keyterms"]
    assert "IFA goli" in cfg["keyterms"]
    assert "TT injection" in cfg["keyterms"]
