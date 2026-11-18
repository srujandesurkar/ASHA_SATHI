"""
Unit Tests for Voice Read-Back, Spoken Corrections, and Confirmation (Module 3)
"""
import pytest
from app.services.voice_orchestrator import voice_orchestrator
from app.services.extraction_service import extraction_engine


def test_readback_generation():
    text = "BEN-001 ANC visit wajan 52 kilo. Next visit 25 November."
    extraction = extraction_engine.extract(text)
    hi_read, en_read = voice_orchestrator.generate_readback(extraction)

    assert "BEN-001" in hi_read
    assert "52" in hi_read
    assert "ANC" in hi_read
    assert "BEN-001" in en_read


def test_weight_voice_correction():
    """Test: 'No, weight is 2.8 kilo' updates ONLY weight_kg."""
    initial_record = {
        "beneficiary_id": "BEN-002",
        "visit_type": "NEWBORN",
        "weight_kg": 3.4,
        "next_visit_date": "2026-11-20"
    }
    correction_phrase = "No, weight is 2.8 kilo"

    resp = voice_orchestrator.apply_spoken_correction(initial_record, correction_phrase)

    assert resp.field_modified == "weight_kg"
    assert resp.previous_value == 3.4
    assert resp.updated_value == 2.8
    assert resp.updated_record["weight_kg"] == 2.8
    # Ensure other fields were NOT modified!
    assert resp.updated_record["beneficiary_id"] == "BEN-002"
    assert resp.updated_record["next_visit_date"] == "2026-11-20"
    assert "2.8" in resp.readback_speech_hi


def test_next_visit_voice_correction():
    """Test: 'Nahi agla visit 25 tareekh ko hai'."""
    initial_record = {
        "beneficiary_id": "BEN-001",
        "visit_type": "ANC",
        "weight_kg": 52.0,
        "next_visit_date": "2026-11-15"
    }
    correction_phrase = "Nahi agla visit 25 tareekh ko hai"

    resp = voice_orchestrator.apply_spoken_correction(initial_record, correction_phrase)

    assert resp.field_modified == "next_visit_date"
    assert "25" in str(resp.updated_value)
    assert resp.updated_record["weight_kg"] == 52.0


def test_spoken_confirmation_eval():
    # Affirmatives
    assert voice_orchestrator.evaluate_confirmation("Haan save karo") is True
    assert voice_orchestrator.evaluate_confirmation("Yes confirm please") is True
    assert voice_orchestrator.evaluate_confirmation("Theek hai save kar do") is True

    # Rejections
    assert voice_orchestrator.evaluate_confirmation("Nahi abhi mat karo") is False
    assert voice_orchestrator.evaluate_confirmation("Cancel this record") is False
    assert voice_orchestrator.evaluate_confirmation("Ruk jao change karna hai") is False
