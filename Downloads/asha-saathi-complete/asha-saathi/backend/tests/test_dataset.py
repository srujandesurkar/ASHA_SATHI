"""
ASHA Saathi - Documented 10-Case Evaluation Dataset Runner
----------------------------------------------------------
Measures Field Extraction Accuracy and Danger-Sign Recall on the 10 hackathon test cases:
1. Normal ANC visit
2. Newborn visit
3. Immunisation visit
4. Pregnancy bleeding detection
5. Newborn fever detection
6. Negative danger-sign statements
7. Noisy background speech
8. Incorrect weight followed by voice correction
9. Missing beneficiary ID
10. Missing next visit date
"""
import pytest
from app.services.extraction_service import extraction_engine
from app.services.danger_shield import danger_shield
from app.services.voice_orchestrator import voice_orchestrator

# Documented Test Dataset with Ground Truth
TEST_DATASET = [
    {
        "id": 1,
        "name": "Normal ANC visit",
        "input": "Beneficiary BEN-001 ka ANC checkup kiya. Wajan 52 kilo hai. Agla visit 25 November ko hai.",
        "expected_id": "BEN-001",
        "expected_type": "ANC",
        "expected_weight": 52.0,
        "expected_danger": False
    },
    {
        "id": 2,
        "name": "Newborn visit",
        "input": "Navjaat shishu BEN-002 ka HBNC checkup kiya. Wajan 2.8 kilo hai. Bachha theek hai.",
        "expected_id": "BEN-002",
        "expected_type": "NEWBORN",
        "expected_weight": 2.8,
        "expected_danger": False
    },
    {
        "id": 3,
        "name": "Immunisation visit",
        "input": "Labharthi BEN-004 ko BCG aur OPV lag gaya. Pentavalent baaki hai. Wajan 3.5 kilo.",
        "expected_id": "BEN-004",
        "expected_type": "IMMUNISATION",
        "expected_weight": 3.5,
        "expected_danger": False
    },
    {
        "id": 4,
        "name": "Pregnancy bleeding detection",
        "input": "BEN-001 ko teentaas se vaginal bleeding ho rahi hai aur pet me tez dard hai.",
        "expected_id": "BEN-001",
        "expected_danger": True,
        "danger_code": "PREG_BLEEDING"
    },
    {
        "id": 5,
        "name": "Newborn fever detection",
        "input": "BEN-002 navjaat bachhe ka sharir bahut garam hai aur tez bukhar hai 102 degree.",
        "expected_id": "BEN-002",
        "expected_danger": True,
        "danger_code": "NB_HIGH_FEVER"
    },
    {
        "id": 6,
        "name": "Negative danger-sign statements",
        "input": "Labharthi bilkul normal hai, koi bleeding nahi hai aur bukhar bhi nahi hai.",
        "expected_danger": False,
        "expected_negation": True
    },
    {
        "id": 7,
        "name": "Noisy background speech",
        "input": "Arey bhaiya suno na... BEN-001 ka ANC likho, background me gaadi chal rahi hai... wajan 53 kilo.",
        "expected_id": "BEN-001",
        "expected_type": "ANC",
        "expected_weight": 53.0,
        "expected_danger": False
    },
    {
        "id": 8,
        "name": "Incorrect weight followed by voice correction",
        "input_initial": "BEN-002 ka newborn visit, wajan 3.5 kilo.",
        "correction": "No, weight is 2.8 kilo",
        "expected_id": "BEN-002",
        "expected_corrected_weight": 2.8,
        "expected_danger": False
    },
    {
        "id": 9,
        "name": "Missing beneficiary ID",
        "input": "Aaj ek ANC visit kiya, wajan 55 kg hai aur next visit 2 hafte baad.",
        "expected_id": None,
        "expected_missing": "beneficiary_id",
        "expected_danger": False
    },
    {
        "id": 10,
        "name": "Missing next visit date",
        "input": "BEN-003 ka ANC checkup kiya, wajan 49 kilo.",
        "expected_id": "BEN-003",
        "expected_next_visit": None,
        "expected_missing": "next_visit_date",
        "expected_danger": False
    }
]


def test_run_documented_10_cases():
    total_danger_cases = 0
    correct_danger_detections = 0
    total_field_checks = 0
    correct_field_checks = 0

    for case in TEST_DATASET:
        case_id = case["id"]

        if case_id == 8:
            # Special correction test
            ext = extraction_engine.extract(case["input_initial"])
            record_dict = ext.model_dump()
            corr_resp = voice_orchestrator.apply_spoken_correction(record_dict, case["correction"])
            assert corr_resp.updated_record["weight_kg"] == case["expected_corrected_weight"]
            correct_field_checks += 1
            total_field_checks += 1
            continue

        text = case["input"]
        ext = extraction_engine.extract(text)
        danger_eval = danger_shield.evaluate(text)

        # Danger Sign Recall evaluation
        if case.get("expected_danger") is True:
            total_danger_cases += 1
            if danger_eval.has_danger_sign is True:
                correct_danger_detections += 1
        elif case.get("expected_danger") is False:
            # Check false positive resistance
            assert danger_eval.has_danger_sign is False, f"False positive in Case {case_id}: {case['name']}"

        # Negation check
        if case.get("expected_negation") is True:
            assert len(danger_eval.negations_detected) > 0

        # Field accuracy checks
        if "expected_id" in case:
            total_field_checks += 1
            if ext.beneficiary_id == case["expected_id"]:
                correct_field_checks += 1

        if "expected_type" in case:
            total_field_checks += 1
            if ext.visit_type == case["expected_type"]:
                correct_field_checks += 1

        if "expected_weight" in case:
            total_field_checks += 1
            if ext.weight_kg == case["expected_weight"]:
                correct_field_checks += 1

        if "expected_missing" in case:
            total_field_checks += 1
            if case["expected_missing"] in ext.missing_fields:
                correct_field_checks += 1

    danger_recall = (correct_danger_detections / total_danger_cases) * 100.0 if total_danger_cases else 100.0
    field_accuracy = (correct_field_checks / total_field_checks) * 100.0 if total_field_checks else 100.0

    print(f"\n=======================================================")
    print(f"ASHA Saathi - Documented Evaluation Results:")
    print(f"Danger-Sign Recall: {danger_recall:.1f}% ({correct_danger_detections}/{total_danger_cases})")
    print(f"Field Extraction Accuracy: {field_accuracy:.1f}% ({correct_field_checks}/{total_field_checks})")
    print(f"=======================================================\n")

    assert danger_recall == 100.0, "Zero-miss danger sign requirement breached!"
    assert field_accuracy >= 95.0, "Field extraction accuracy under threshold!"
