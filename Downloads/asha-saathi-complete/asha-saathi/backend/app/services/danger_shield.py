"""
ASHA Saathi - Danger Shield Engine (Module 4)
--------------------------------------------
Deterministic, rule-based danger-sign detection module.
Does NOT rely on general LLMs for safety decisions.

Clinical Guidelines & Protocols Referenced:
1. MoHFW / National Health Mission (NHM): Guidelines for Antenatal Care (ANC) & High-Risk Pregnancy.
2. IMNCI (Integrated Management of Neonatal and Childhood Illness) - MoHFW & WHO Chart Booklet.
3. ASHA Handbook: Home Based Newborn Care (HBNC) & Modules 6 & 7 (Skills that Save Lives).
"""
import re
from typing import List, Dict, Any, Tuple
from app.schemas.danger_sign import DangerSignMatch, DangerShieldResult

# Versioned Danger Sign Vocabulary (V1.2 - MoHFW / IMNCI Aligned)
DANGER_SIGN_VOCABULARY = [
    # 1. PREGNANCY: Vaginal Bleeding (Antepartum/Postpartum Hemorrhage)
    {
        "category": "PREGNANCY",
        "sign_code": "PREG_BLEEDING",
        "sign_name": "Vaginal Bleeding in Pregnancy",
        "patterns": [
            r"\b(vaginal\s+bleeding|bleeding|blood\s+loss|bleeding\s+per\s+vaginam)\b",
            r"\b(khoon\s+aa\s*raha|khoon\s+nikal|khoon\s+beh\s*raha|raktsrav|lal\s+pani|khoon\s+gir\s*raha)\b",
            r"\b(spotting|blood\s+spot|rakt\s+bahna)\b"
        ],
        "guideline_source": "MoHFW ANC Guidelines Sec 4.2 / High-Risk Pregnancy Management",
        "immediate_action": "Refer immediately to First Referral Unit (FRU) / PHC. Keep patient resting.",
        "alert_hi": "Chetavani: Garbhavastha me khoon aana ek gambhir sanket hai. Kripya labharthi ko turant Prathmik Swasthya Kendra (PHC) ya FRU refer karein.",
        "alert_en": "Warning: Vaginal bleeding during pregnancy is a critical danger sign. Refer beneficiary immediately to PHC or FRU."
    },

    # 2. PREGNANCY: Convulsions / Fits (Eclampsia / Pre-eclampsia)
    {
        "category": "PREGNANCY",
        "sign_code": "PREG_CONVULSIONS",
        "sign_name": "Convulsions / Fits in Pregnancy",
        "patterns": [
            r"\b(convulsions?|fits?|seizures?|eclampsia)\b",
            r"\b(daure|jhatke|aankh\s+ulatna|mirgi)\b"
        ],
        "guideline_source": "MoHFW High-Risk Pregnancy Protocols - Eclampsia Emergency Management",
        "immediate_action": "Emergency referral to FRU/District Hospital. Keep airway clear, do not give liquids.",
        "alert_hi": "Aapatkaal: Garbhvati ko daure ya jhatke aana eclampsia ka lakshan hai. Turant aspatal le jayein.",
        "alert_en": "Emergency: Convulsions during pregnancy indicate eclampsia. Transport to hospital immediately."
    },

    # 3. PREGNANCY: Severe Headache / Blurred Vision (Severe Pre-eclampsia)
    {
        "category": "PREGNANCY",
        "sign_code": "PREG_SEVERE_HEADACHE",
        "sign_name": "Severe Headache with Blurred Vision",
        "patterns": [
            r"\b(severe\s+headache|blurred\s+vision|flashing\s+lights)\b",
            r"\b(tez\s+sir\s*dard|dhundhla\s+dikh|aankho\s+ke\s+aage\s+andhera)\b"
        ],
        "guideline_source": "MoHFW ANC Module - Identification of Severe Pre-eclampsia",
        "immediate_action": "Refer to PHC/FRU for blood pressure check and urgent evaluation.",
        "alert_hi": "Chetavani: Tez sir dard aur dhundhla dikhna severe pre-eclampsia ho sakta hai. PHC refer karein.",
        "alert_en": "Warning: Severe headache and blurred vision may indicate pre-eclampsia. Refer to PHC immediately."
    },

    # 4. NEWBORN: Fever or Hot to Touch (Neonatal Sepsis / Infection)
    {
        "category": "NEWBORN",
        "sign_code": "NB_HIGH_FEVER",
        "sign_name": "Newborn High Fever / Hot to Touch",
        "patterns": [
            r"\b(newborn\s+fever|infant\s+fever|baby\s+has\s+fever|high\s+fever|very\s+hot)\b",
            r"\b(tez\s+bukhar|garam\s+hai|sharir\s+tap\s*raha|bukhar\s+zyada)\b",
            r"\b(101|102|103|104|38(\.\d+)?|39(\.\d+)?)\s*(degree|celsius|f|fahrenheit|bukhar)?\b"
        ],
        "guideline_source": "IMNCI Chart Booklet: Young Infant 0-2 Months / HBNC Day 1-28 Protocol",
        "immediate_action": "Refer immediately to PHC/SNCU. Do NOT give cold sponge. Keep baby warm.",
        "alert_hi": "Chetavani: Navjaat shishu ko tez bukhar hai. Kripya turant Prathmik Swasthya Kendra (PHC) refer karein.",
        "alert_en": "Warning: Newborn has high fever. Refer immediately to PHC or SNCU for urgent assessment."
    },

    # 5. NEWBORN: Hypothermia / Cold to Touch
    {
        "category": "NEWBORN",
        "sign_code": "NB_HYPOTHERMIA",
        "sign_name": "Newborn Hypothermia (Cold to Touch)",
        "patterns": [
            r"\b(cold\s+to\s+touch|hypothermia|baby\s+is\s+cold|cold\s+hands\s+and\s+feet)\b",
            r"\b(sharir\s+thanda|bachha\s+thanda|pair\s+aur\s+hath\s+thande|thanda\s+pad\s*gaya)\b"
        ],
        "guideline_source": "IMNCI Protocol - Hypothermia in Young Infant",
        "immediate_action": "Provide immediate Kangaroo Mother Care (KMC) skin-to-skin and refer urgently.",
        "alert_hi": "Aapatkaal: Navjaat shishu ka sharir thanda hai. Turant KMC (skin-to-skin) dein aur PHC refer karein.",
        "alert_en": "Emergency: Newborn is cold to touch (hypothermia). Provide immediate KMC and refer to PHC."
    },

    # 6. NEWBORN: Poor Feeding / Unable to Breastfeed
    {
        "category": "NEWBORN",
        "sign_code": "NB_POOR_FEEDING",
        "sign_name": "Unable to Feed / Not Sucking Milk",
        "patterns": [
            r"\b(unable\s+to\s+feed|cannot\s+suckle?|not\s+drinking|poor\s+feeding|stopped\s+feeding)\b",
            r"\b(doodh\s+nahi\s+pee\s*raha|stanpan\s+nahi|feed\s+nahi\s+kar\s*raha|doodh\s+chhod\s*diya)\b"
        ],
        "guideline_source": "IMNCI General Danger Signs - Inability to feed is a sign of severe systemic illness",
        "immediate_action": "Assess attachment; if infant cannot suckle at all, refer urgently to PHC/SNCU.",
        "alert_hi": "Chetavani: Shishu doodh nahi pee pa raha hai. Ye gambhir sanket hai. Turant PHC refer karein.",
        "alert_en": "Warning: Infant unable to feed. This is a critical danger sign. Refer to PHC immediately."
    },

    # 7. NEWBORN: Fast Breathing / Chest Indrawing (Respiratory Distress / Pneumonia)
    {
        "category": "NEWBORN",
        "sign_code": "NB_FAST_BREATHING",
        "sign_name": "Fast Breathing / Severe Chest Indrawing",
        "patterns": [
            r"\b(fast\s+breathing|chest\s+indrawing|grunting|stridor|difficulty\s+breathing)\b",
            r"\b(pasli\s+chal\s*rahi|tez\s+saans|saans\s+ful\s*rahi|saans\s+lene\s+me\s+takleef|haaf\s*raha)\b"
        ],
        "guideline_source": "IMNCI Acute Respiratory Infection Protocol (>60 breaths/min in infant <2mo)",
        "immediate_action": "Count respiratory rate. If chest indrawing is present, refer immediately.",
        "alert_hi": "Chetavani: Shishu ki pasli chal rahi hai ya tez saans chal rahi hai. Turant PHC refer karein.",
        "alert_en": "Warning: Fast breathing or chest indrawing detected. Immediate PHC referral required."
    },

    # 8. NEWBORN: Excessive Drowsiness / Lethargy / Unconsciousness
    {
        "category": "NEWBORN",
        "sign_code": "NB_LETHARGY",
        "sign_name": "Excessive Drowsiness / Lethargy / Unconscious",
        "patterns": [
            r"\b(lethargic|unconscious|excessive\s+drowsiness|floppy|not\s+waking\s*up)\b",
            r"\b(bachha\s+sust\s+hai|jag\s+nahi\s*raha|behosh|koi\s+movement\s+nahi|shithil)\b"
        ],
        "guideline_source": "IMNCI Sick Young Infant Protocol: Abnormally sleepy or difficult to wake",
        "immediate_action": "Emergency transport to SNCU/PHC. Keep infant warm during transit.",
        "alert_hi": "Aapatkaal: Shishu behad sust hai ya jag nahi raha. Turant aspatal le jayein.",
        "alert_en": "Emergency: Infant is abnormally lethargic or unresponsive. Urgent hospital referral needed."
    }
]

# Explicit Negation Expressions in Hindi, Hinglish, and English
NEGATION_PATTERNS = [
    # Hindi / Hinglish negations following or preceding symptom
    r"(nahi\s+hai|nahi\s+ho\s+raha|nahi\s+nikal|nahi\s+pada|nahi\s+aaya|nahi\s+tha)",
    r"(koi\s+\w+\s+nahi|kuch\s+bhi\s+nahi|bilkul\s+nahi)",
    r"(no\s+\w+|not\s+present|denies\s+\w+|without\s+\w+|negative\s+for)",
    r"(normal\s+hai|bilkul\s+theek\s+hai|acche\s+se\s+pee\s+raha)"
]


class DangerShieldEngine:
    """
    Deterministic rule-based danger-sign detection engine.
    Ensures zero hallucination and strictly enforces Indian public health referral protocols.
    """

    def __init__(self, vocabulary=None):
        self.vocabulary = vocabulary or DANGER_SIGN_VOCABULARY

    def _is_negated(self, text: str, match_start: int, match_end: int) -> Tuple[bool, str]:
        """
        Check for explicit negation within a window of words around the matched danger term.
        Window size: 40 characters before and after.
        """
        window_start = max(0, match_start - 45)
        window_end = min(len(text), match_end + 45)
        surrounding_text = text[window_start:window_end].lower()

        # Specific Hindi/English negation checks
        negation_clauses = [
            r"koi\s+[\w\s]{0,20}(nahi|not|absent)",
            r"(nahi\s+hai|nahi\s+ho\s*raha|nahi\s+aaya|nahi\s+dekha)",
            r"(no|not|neither|without|denies)\s+[\w\s]{0,20}",
            r"doodh\s+(theek|achha|sahi)\s+pee\s*raha",
            r"(normal|fine|good|well)\s+condition"
        ]

        for pattern in negation_clauses:
            neg_match = re.search(pattern, surrounding_text, re.IGNORECASE)
            if neg_match:
                return True, neg_match.group(0).strip()

        return False, ""

    def evaluate(self, speech_text: str) -> DangerShieldResult:
        """
        Evaluates transcribed speech for positive danger signs while checking for explicit negations.
        """
        if not speech_text or not speech_text.strip():
            return DangerShieldResult(has_danger_sign=False, priority="NORMAL")

        cleaned_text = speech_text.strip()
        matched_signs: List[DangerSignMatch] = []
        detected_negations: List[str] = []
        highest_severity = "NORMAL"

        for item in self.vocabulary:
            for pattern_str in item["patterns"]:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                for match in pattern.finditer(cleaned_text):
                    match_start = match.start()
                    match_end = match.end()
                    matched_term = match.group(0)

                    # Check for explicit negation
                    is_neg, neg_phrase = self._is_negated(cleaned_text, match_start, match_end)
                    if is_neg:
                        detected_negations.append(f"{matched_term} negated by '{neg_phrase}'")
                        continue

                    # Positive danger sign identified!
                    sign_match = DangerSignMatch(
                        category=item["category"],
                        sign_code=item["sign_code"],
                        sign_name=item["sign_name"],
                        matched_term=matched_term,
                        severity="EMERGENCY",
                        guideline_source=item["guideline_source"],
                        immediate_action=item["immediate_action"]
                    )

                    # Prevent duplicate entries for same sign_code
                    if not any(s.sign_code == sign_match.sign_code for s in matched_signs):
                        matched_signs.append(sign_match)
                        highest_severity = "EMERGENCY"

        has_danger = len(matched_signs) > 0
        spoken_hi = None
        spoken_en = None

        if has_danger:
            # Construct clear, direct spoken alerts in Hindi and English
            sign_names_hi = " aur ".join([s.sign_name for s in matched_signs])
            spoken_hi = f"Chetavani: Labharthi me gambhir lakshan paye gaye hain ({sign_names_hi}). Kripya turant Prathmik Swasthya Kendra (PHC) refer karein."
            spoken_en = f"Alert: High-risk danger signs detected ({', '.join([s.sign_name for s in matched_signs])}). Immediate referral to Primary Health Centre (PHC) required."

        return DangerShieldResult(
            has_danger_sign=has_danger,
            priority=highest_severity if has_danger else "NORMAL",
            detected_signs=matched_signs,
            negations_detected=detected_negations,
            spoken_alert_hi=spoken_hi,
            spoken_alert_en=spoken_en,
            referral_required=has_danger,
            recommended_facility="Primary Health Centre (PHC) / SNCU" if has_danger else None
        )


# Global singleton instance
danger_shield = DangerShieldEngine()
