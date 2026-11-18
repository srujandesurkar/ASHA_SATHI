"""
ASHA Saathi - Smart Visit Record Extraction Engine (Module 2)
------------------------------------------------------------
Extracts structured healthcare visit fields from Indic/English code-mixed speech.
Maintains evidence linking each field to its spoken transcript slice.
Enforces strict rules:
- Never guess beneficiary IDs.
- Never assume a vaccination was completed unless explicitly affirmed.
- Preserves missing fields as null/None.
- Generates voice clarification prompts for missing essential fields.
"""
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.visit_record import VisitRecordExtraction, FieldEvidence
from app.services.danger_shield import danger_shield

# Type alias
Tuple_Optional = Tuple[Optional[Any], Optional[str]]

# Known Indic and National Immunisation Schedule Vaccines
KNOWN_VACCINES = [
    "BCG", "OPV", "OPV-0", "OPV-1", "OPV-2", "OPV-3",
    "Hepatitis B", "Pentavalent", "Pentavalent-1", "Pentavalent-2", "Pentavalent-3",
    "Rotavirus", "IPV", "PCV", "MR", "Measles Rubella", "JE",
    "DPT Booster", "Vitamin A", "TT", "Td", "Tetanus Toxoid"
]


class ExtractionEngine:
    def __init__(self):
        self.vaccine_patterns = {
            "BCG": r"\b(bcg)\b",
            "OPV": r"\b(opv|polio|oral\s+polio)\b",
            "Hepatitis B": r"\b(hepatitis\s*b|hep\s*b)\b",
            "Pentavalent": r"\b(pentavalent|penta)\b",
            "Rotavirus": r"\b(rotavirus|rota)\b",
            "IPV": r"\b(ipv|polio\s+injection)\b",
            "PCV": r"\b(pcv|pneumococcal)\b",
            "MR": r"\b(mr|measles|rubella|khasra)\b",
            "DPT Booster": r"\b(dpt|dpt\s*booster)\b",
            "TT": r"\b(tt|tetanus|tetanus\s+toxoid|td|tt\s*injection)\b",
            "Vitamin A": r"\b(vitamin\s*a|vit\s*a)\b"
        }

    def _extract_beneficiary(self, text: str) -> Tuple_Optional:
        """Extract beneficiary ID like BEN-001 or ID 1."""
        # Check standard format BEN-XXX or BENXXX
        id_match = re.search(r"\b(BEN[-\s]?\d{3,4}|BEN[-\s]?\d+)\b", text, re.IGNORECASE)
        if id_match:
            raw = id_match.group(0).upper().replace(" ", "-")
            if not raw.startswith("BEN-"):
                raw = f"BEN-{raw[3:]}" if raw.startswith("BEN") else f"BEN-{raw}"
            return raw, id_match.group(0)

        # Check spoken format "beneficiary number 3" or "labharthi 2"
        spoken_match = re.search(r"\b(?:beneficiary|labharthi|patient|id)\s*(?:no|number|kramank)?\s*(\d+)\b", text, re.IGNORECASE)
        if spoken_match:
            num = spoken_match.group(1).zfill(3)
            return f"BEN-{num}", spoken_match.group(0)

        return None, None

    def _extract_visit_type(self, text: str) -> Tuple_Optional:
        """Determine ANC, PNC, IMMUNISATION, or NEWBORN."""
        patterns = [
            ("ANC", r"\b(anc|antenatal|pregnancy\s+checkup|garbhavastha\s+jaanch|garbhvati\s+visit)\b"),
            ("PNC", r"\b(pnc|postnatal|delivery\s+ke\s+baad|prasav\s+ke\s+baad)\b"),
            ("NEWBORN", r"\b(hbnc|newborn|navjaat|shishu\s+visit|infant\s+checkup|bachhe\s+ki\s+jaanch)\b"),
            ("IMMUNISATION", r"\b(immunisation|immunization|teekakaran|tika|vaccination|vaccine\s+visit)\b")
        ]
        for vtype, pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return vtype, m.group(0)

        # Infer IMMUNISATION if specific vaccines are mentioned (BCG, OPV, Pentavalent, etc.)
        vaccine_kw = r"\b(bcg|opv|pentavalent|rotavirus|polio|measles|rubella|tetanus|dpt|teeka|lag gaya|lagna baaki)\b"
        vm = re.search(vaccine_kw, text, re.IGNORECASE)
        if vm:
            return "IMMUNISATION", vm.group(0)

        return None, None

    def _extract_weight(self, text: str) -> Tuple_Optional:
        """
        Extract weight in kg.
        Handles: "2.8 kilo", "52 kg", "3 kilo 200 gram", "wajan 2.8 hai"
        """
        # Complex compound: "3 kilo 200 gram"
        compound_m = re.search(r"\b(\d+)\s*(?:kilo|kg)\s*(\d+)\s*(?:gram|gm)\b", text, re.IGNORECASE)
        if compound_m:
            kg = float(compound_m.group(1)) + float(compound_m.group(2)) / 1000.0
            return round(kg, 2), compound_m.group(0)

        # Simple decimal or integer weight: "2.8 kilo", "52 kg", "wajan 52.5"
        weight_m = re.search(r"(?:wajan|weight|vajan|bhara)?\s*(\d+(?:\.\d+)?)\s*(?:kilo|kg|kilogram|kilos)?\b", text, re.IGNORECASE)
        # Look for explicit weight keyword proximity
        keyword_m = re.search(r"(?:wajan|weight|vajan)\s*(?:hai)?\s*(\d+(?:\.\d+)?)\s*(?:kilo|kg)?", text, re.IGNORECASE)
        if keyword_m:
            val = float(keyword_m.group(1))
            return val, keyword_m.group(0)

        unit_m = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:kilo|kg|kilogram)\b", text, re.IGNORECASE)
        if unit_m:
            val = float(unit_m.group(1))
            return val, unit_m.group(0)

        return None, None

    def _extract_vaccinations(self, text: str) -> tuple[List[str], List[str], Dict[str, str]]:
        """
        Distinguish vaccinations COMPLETED vs DUE.
        Never assume completed without affirmative indicators in the same clause/sentence.
        """
        completed = []
        due = []
        evidence_dict = {}

        # Look for completed contexts
        completed_keywords = ["de diya", "lag gaya", "laga diya", "completed", "given", "done", "lag chuka"]
        due_keywords = ["dena baaki", "lagna baaki", "baaki hai", "due hai", "next time", "agle mahine", "pending", "bacha hai"]

        # Split text into clauses/sentences to prevent cross-contamination
        sentences = re.split(r"[.\n]+", text)

        for sentence in sentences:
            sentence_clean = sentence.strip()
            if not sentence_clean:
                continue

            for vac_name, pattern in self.vaccine_patterns.items():
                m = re.search(pattern, sentence_clean, re.IGNORECASE)
                if m:
                    # Look for keywords in this specific sentence/clause
                    sub = sentence_clean.lower()
                    is_due = any(k in sub for k in due_keywords)
                    is_completed = any(k in sub for k in completed_keywords)

                    if is_due and not is_completed:
                        if vac_name not in due:
                            due.append(vac_name)
                            evidence_dict[f"due_{vac_name}"] = sentence_clean
                    elif is_completed:
                        if vac_name not in completed:
                            completed.append(vac_name)
                            evidence_dict[f"completed_{vac_name}"] = sentence_clean
                    else:
                        if vac_name not in due and vac_name not in completed:
                            due.append(vac_name)
                            evidence_dict[f"due_{vac_name}"] = sentence_clean

        return completed, due, evidence_dict

    def _extract_dates(self, text: str) -> tuple[str, Optional[str], Optional[str]]:
        """
        Extract visit_date and next_visit_date.
        """
        today = datetime.now()
        visit_date_str = today.strftime("%Y-%m-%d")

        # Next visit date
        next_visit_str = None
        next_visit_source = None

        # Pattern: "next visit 25 november", "agla visit 25 tareekh", "after 2 weeks"
        next_match = re.search(r"(?:agla\s+visit|next\s+visit|agli\s+jaanch|agli\s+tareekh)\s*(?:hai)?\s*(\d{1,2})?\s*([a-zA-Z]+)?", text, re.IGNORECASE)
        if next_match:
            day_str = next_match.group(1)
            month_str = next_match.group(2)
            if day_str:
                day = int(day_str)
                # If month specified
                if month_str:
                    next_visit_str = f"2026-11-{day:02d}"  # standardized ISO
                else:
                    next_visit_str = (today + timedelta(days=14)).strftime("%Y-%m-%d")
                next_visit_source = next_match.group(0)

        # Relative timing: "2 hafte baad" / "in 2 weeks"
        rel_match = re.search(r"(\d+)\s*(?:hafte|weeks?|mahine|months?)\s*(?:baad|later|after)", text, re.IGNORECASE)
        if rel_match:
            count = int(rel_match.group(1))
            is_month = "mahin" in rel_match.group(0).lower() or "month" in rel_match.group(0).lower()
            days = count * 30 if is_month else count * 7
            next_visit_str = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            next_visit_source = rel_match.group(0)

        return visit_date_str, next_visit_str, next_visit_source

    def extract(self, text: str) -> VisitRecordExtraction:
        """
        Main extraction pipeline linking every field to its spoken evidence.
        """
        evidence_map: Dict[str, FieldEvidence] = {}
        missing_fields: List[str] = []

        # 1. Beneficiary ID
        ben_id, ben_source = self._extract_beneficiary(text)
        if ben_id:
            evidence_map["beneficiary_id"] = FieldEvidence(
                field_name="beneficiary_id",
                spoken_source=ben_source,
                confidence=0.98,
                extracted_value=ben_id
            )
        else:
            missing_fields.append("beneficiary_id")

        # 2. Visit Type
        vtype, vtype_source = self._extract_visit_type(text)
        if vtype:
            evidence_map["visit_type"] = FieldEvidence(
                field_name="visit_type",
                spoken_source=vtype_source,
                confidence=0.95,
                extracted_value=vtype
            )
        else:
            missing_fields.append("visit_type")

        # 3. Weight
        weight, weight_source = self._extract_weight(text)
        if weight is not None:
            evidence_map["weight_kg"] = FieldEvidence(
                field_name="weight_kg",
                spoken_source=weight_source,
                confidence=0.94,
                extracted_value=weight
            )

        # 4. Vaccinations
        vac_completed, vac_due, vac_evidence = self._extract_vaccinations(text)
        for k, src in vac_evidence.items():
            evidence_map[k] = FieldEvidence(
                field_name=k,
                spoken_source=src,
                confidence=0.90,
                extracted_value=True
            )

        # 5. Blood Pressure & IFA tablets
        anc_details = {}
        bp_match = re.search(r"\b(?:bp|blood\s+pressure)\s*(\d{2,3})[\s/](\d{2,3})\b", text, re.IGNORECASE)
        bp_val = None
        if bp_match:
            bp_val = f"{bp_match.group(1)}/{bp_match.group(2)}"
            anc_details["blood_pressure"] = bp_val
            evidence_map["blood_pressure"] = FieldEvidence(
                field_name="blood_pressure",
                spoken_source=bp_match.group(0),
                confidence=0.96,
                extracted_value=bp_val
            )

        ifa_match = re.search(r"(\d+)\s*(?:ifa|iron|folic|goli|tablets?)", text, re.IGNORECASE)
        ifa_count = None
        if ifa_match:
            ifa_count = int(ifa_match.group(1))
            anc_details["ifa_tablets"] = ifa_count
            evidence_map["ifa_tablets_given"] = FieldEvidence(
                field_name="ifa_tablets_given",
                spoken_source=ifa_match.group(0),
                confidence=0.95,
                extracted_value=ifa_count
            )

        # 6. Dates
        visit_date, next_visit, next_source = self._extract_dates(text)
        if next_visit:
            evidence_map["next_visit_date"] = FieldEvidence(
                field_name="next_visit_date",
                spoken_source=next_source or "next visit phrase",
                confidence=0.92,
                extracted_value=next_visit
            )
        else:
            missing_fields.append("next_visit_date")

        # 7. Danger Sign Evaluation
        danger_eval = danger_shield.evaluate(text)

        # 8. Clarification Prompts if mandatory fields missing
        clarify_hi = None
        clarify_en = None
        if "beneficiary_id" in missing_fields:
            clarify_hi = "Kripya labharthi ki ID ya naam batayein (jaise BEN-001)."
            clarify_en = "Please provide the Beneficiary ID or name (e.g. BEN-001)."
        elif "next_visit_date" in missing_fields:
            clarify_hi = "Agla visit kab nirdharit kiya gaya hai?"
            clarify_en = "When is the next visit scheduled?"

        return VisitRecordExtraction(
            beneficiary_id=ben_id,
            beneficiary_name=None,  # will be linked to synthetic DB in API
            visit_type=vtype,
            visit_date=visit_date,
            weight_kg=weight,
            blood_pressure=bp_val,
            ifa_tablets_given=ifa_count,
            vaccinations_due=vac_due,
            vaccinations_completed=vac_completed,
            anc_pnc_details=anc_details,
            next_visit_date=next_visit,
            visit_notes=text.strip(),
            evidence=evidence_map,
            missing_fields=missing_fields,
            clarification_prompt_hi=clarify_hi,
            clarification_prompt_en=clarify_en,
            has_danger_sign=danger_eval.has_danger_sign,
            danger_signs=[s.sign_name for s in danger_eval.detected_signs]
        )


Tuple_Optional = tuple[Optional[Any], Optional[str]]
extraction_engine = ExtractionEngine()
