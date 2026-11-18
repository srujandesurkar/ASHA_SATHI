"""
Unit Tests for Smart Visit Record Extraction Engine (Module 2)
Tests field extraction, evidence mapping, and missing field handling.
"""
import pytest
from app.services.extraction_service import extraction_engine


def test_normal_anc_visit_extraction():
    text = "Beneficiary BEN-001 ka ANC checkup kiya. Wajan 52 kilo hai, BP 120/80 aur 30 IFA goli di. Agla visit 25 November ko hai."
    ext = extraction_engine.extract(text)

    assert ext.beneficiary_id == "BEN-001"
    assert ext.visit_type == "ANC"
    assert ext.weight_kg == 52.0
    assert ext.blood_pressure == "120/80"
    assert ext.ifa_tablets_given == 30
    assert ext.next_visit_date is not None
    assert "beneficiary_id" in ext.evidence
    assert "weight_kg" in ext.evidence
    assert ext.has_danger_sign is False


def test_newborn_visit_extraction():
    text = "Navjaat shishu BEN-002 ka HBNC checkup kiya. Bachhe ka wajan 2.8 kilo hai. Doodh theek se pee raha hai. Agla visit 2 hafte baad hoga."
    ext = extraction_engine.extract(text)

    assert ext.beneficiary_id == "BEN-002"
    assert ext.visit_type == "NEWBORN"
    assert ext.weight_kg == 2.8
    assert ext.next_visit_date is not None
    assert ext.has_danger_sign is False


def test_immunisation_visit_extraction():
    text = "Labharthi BEN-004 ko BCG aur OPV de diya hai. Pentavalent lagna baaki hai agle mahine. Wajan 3.5 kilo."
    ext = extraction_engine.extract(text)

    assert ext.beneficiary_id == "BEN-004"
    assert ext.visit_type == "IMMUNISATION"
    assert "BCG" in ext.vaccinations_completed
    assert "OPV" in ext.vaccinations_completed
    assert "Pentavalent" in ext.vaccinations_due
    assert ext.weight_kg == 3.5


def test_missing_beneficiary_id_rule():
    """Rule: Never invent missing beneficiary IDs."""
    text = "Aaj ek ANC visit kiya, wajan 55 kg hai aur next visit 2 hafte baad hai."
    ext = extraction_engine.extract(text)

    assert ext.beneficiary_id is None
    assert "beneficiary_id" in ext.missing_fields
    assert ext.clarification_prompt_hi is not None


def test_missing_next_visit_date_rule():
    """Rule: Preserve missing next visit date as None and request clarification."""
    text = "Beneficiary BEN-003 ka visit kiya, wajan 48 kg hai."
    ext = extraction_engine.extract(text)

    assert ext.beneficiary_id == "BEN-003"
    assert ext.next_visit_date is None
    assert "next_visit_date" in ext.missing_fields


def test_noisy_background_speech():
    """Handles conversational filler words and background noise."""
    text = "Arey suno haan... BEN-001 ka ANC visit likho na, gaadi ki awaaz aa rahi hai... wajan 53 kilo aur agla visit 20 November ko bol do."
    ext = extraction_engine.extract(text)

    assert ext.beneficiary_id == "BEN-001"
    assert ext.visit_type == "ANC"
    assert ext.weight_kg == 53.0
