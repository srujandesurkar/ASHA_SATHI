"""
Unit Tests for Danger Shield Engine (Module 4)
Tests pregnancy danger signs, newborn danger signs, and explicit negations.
"""
import pytest
from app.services.danger_shield import danger_shield


def test_pregnancy_bleeding_detection():
    text = "Beneficiary Sunita Devi ko aaj subah se vaginal bleeding ho rahi hai aur pet me dard hai."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is True
    assert res.priority == "EMERGENCY"
    assert any(s.sign_code == "PREG_BLEEDING" for s in res.detected_signs)
    assert res.spoken_alert_hi is not None
    assert "PHC" in res.spoken_alert_hi


def test_pregnancy_bleeding_hindi_slang():
    text = "Garbhvati mahila ko khoon aa raha hai, kapde kharab ho gaye."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is True
    assert any(s.sign_code == "PREG_BLEEDING" for s in res.detected_signs)


def test_newborn_fever_detection():
    text = "Shishu ka sharir bahut garam hai aur tez bukhar hai 102 degree."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is True
    assert any(s.sign_code == "NB_HIGH_FEVER" for s in res.detected_signs)


def test_newborn_poor_feeding_and_breathing():
    text = "Bachha doodh nahi pee raha hai aur pasli chal rahi hai tez saans ke sath."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is True
    assert len(res.detected_signs) >= 2
    sign_codes = [s.sign_code for s in res.detected_signs]
    assert "NB_POOR_FEEDING" in sign_codes
    assert "NB_FAST_BREATHING" in sign_codes


def test_negative_danger_sign_statements():
    """Explicit negation test: worker clarifies that symptoms are ABSENT."""
    text = "Beneficiary bilkul theek hai, koi bleeding nahi hai aur bukhar bhi nahi hai."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is False
    assert res.priority == "NORMAL"
    assert len(res.detected_signs) == 0
    assert len(res.negations_detected) > 0


def test_negative_feeding_statement():
    """Worker states baby is feeding well."""
    text = "Bachha doodh theek se pee raha hai koi problem nahi hai."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is False
    assert len(res.detected_signs) == 0


def test_convulsions_detection():
    text = "Garbhvati mahila ko achanak jhatke aur daure pad rahe hain."
    res = danger_shield.evaluate(text)
    assert res.has_danger_sign is True
    assert any(s.sign_code == "PREG_CONVULSIONS" for s in res.detected_signs)
