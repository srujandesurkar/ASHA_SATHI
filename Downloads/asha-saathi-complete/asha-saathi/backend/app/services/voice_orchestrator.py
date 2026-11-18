"""
ASHA Saathi - Voice Orchestrator & Read-Back Engine (Module 3)
-------------------------------------------------------------
Coordinates the conversational flow:
1. First Turn AI Disclosure (Responsible AI).
2. Spoken Read-back of extracted fields.
3. Natural voice corrections (modifying only the changed field).
4. Spoken confirmation before database commit.
"""
import re
from typing import Dict, Any, Tuple
from app.schemas.visit_record import VisitRecordExtraction
from app.schemas.voice_session import SpokenCorrectionResponse, SpokenConfirmationResponse


class VoiceOrchestrator:

    @staticmethod
    def get_ai_disclosure(language: str = "hi-IN-codemix") -> Tuple[str, str]:
        """
        Discloses assistant is an AI in the user's language (Responsible AI baseline requirement).
        """
        hi_text = (
            "Namaste! Main ASHA Saathi hoon, ek AI swasthya sahayak. "
            "Aap apni bhasha me visit ki jaankari bolein, main field register taiyyar kar doonga."
        )
        en_text = (
            "Hello! I am ASHA Saathi, an AI healthcare assistant for ASHA workers. "
            "Please speak your visit notes in Hindi or English, and I will prepare the visit register."
        )
        return hi_text, en_text

    @staticmethod
    def generate_readback(extraction: VisitRecordExtraction) -> Tuple[str, str]:
        """
        Reads every important field aloud before requesting confirmation.
        """
        parts_hi = ["Vishesh vivaran padh raha hoon:"]
        parts_en = ["Reading out the visit summary:"]

        # Beneficiary
        if extraction.beneficiary_id:
            parts_hi.append(f"Labharthi ID {extraction.beneficiary_id}.")
            parts_en.append(f"Beneficiary ID {extraction.beneficiary_id}.")

        # Visit Type
        if extraction.visit_type:
            parts_hi.append(f"Visit type {extraction.visit_type}.")
            parts_en.append(f"Visit type {extraction.visit_type}.")

        # Weight
        if extraction.weight_kg is not None:
            parts_hi.append(f"Wajan {extraction.weight_kg} kilo.")
            parts_en.append(f"Weight {extraction.weight_kg} kg.")

        # Blood pressure
        if extraction.blood_pressure:
            parts_hi.append(f"Blood pressure {extraction.blood_pressure}.")
            parts_en.append(f"Blood pressure {extraction.blood_pressure}.")

        # Vaccinations completed
        if extraction.vaccinations_completed:
            vacs_done = ", ".join(extraction.vaccinations_completed)
            parts_hi.append(f"Lage hue teeke: {vacs_done}.")
            parts_en.append(f"Vaccinations given: {vacs_done}.")

        # Vaccinations due
        if extraction.vaccinations_due:
            vacs_due = ", ".join(extraction.vaccinations_due)
            parts_hi.append(f"Baaki teeke: {vacs_due}.")
            parts_en.append(f"Vaccinations due: {vacs_due}.")

        # Next visit
        if extraction.next_visit_date:
            parts_hi.append(f"Agli jaanch ki tareekh {extraction.next_visit_date}.")
            parts_en.append(f"Next scheduled visit is {extraction.next_visit_date}.")

        # Prompt for confirmation or correction
        parts_hi.append("Kya ye sabhi jaankari sahi hai? Save karne ke liye 'Haan save karo' bolein, ya correction batayein.")
        parts_en.append("Is this information accurate? Say 'Yes save it' to confirm, or speak your correction.")

        return " ".join(parts_hi), " ".join(parts_en)

    @staticmethod
    def apply_spoken_correction(current_record: Dict[str, Any], spoken_phrase: str) -> SpokenCorrectionResponse:
        """
        Applies natural voice corrections. Updates ONLY the target field.
        Examples:
        - "No, weight is 2.8 kilo" -> updates weight_kg to 2.8
        - "Nahi agla visit 25 November ko hai" -> updates next_visit_date
        - "Visit type PNC nahi ANC hai" -> updates visit_type
        - "Beneficiary ID BEN-004 hai" -> updates beneficiary_id
        """
        updated = dict(current_record)
        modified_field = "unknown"
        prev_val = None
        new_val = None

        text = spoken_phrase.strip().lower()

        # 1. Weight correction: "weight is 2.8", "wajan 3 kilo kar do", "no weight is 2.8"
        weight_match = re.search(r"(?:wajan|weight|vajan)?\s*(?:hai|is)?\s*(\d+(?:\.\d+)?)\s*(?:kilo|kg|kilogram)?\b", text)
        if ("weight" in text or "wajan" in text or "kilo" in text or "kg" in text) and weight_match:
            # find the number near weight
            num_match = re.search(r"(\d+(?:\.\d+)?)", text)
            if num_match:
                modified_field = "weight_kg"
                prev_val = updated.get("weight_kg")
                new_val = float(num_match.group(1))
                updated["weight_kg"] = new_val

        # 2. Next visit date correction: "agla visit 25 tareekh", "next visit is 20th"
        elif "next visit" in text or "agla visit" in text or "agli tareekh" in text or "november" in text:
            day_match = re.search(r"(\d{1,2})", text)
            if day_match:
                modified_field = "next_visit_date"
                prev_val = updated.get("next_visit_date")
                day = int(day_match.group(1))
                new_val = f"2026-11-{day:02d}"
                updated["next_visit_date"] = new_val

        # 3. Beneficiary ID correction: "ID BEN-005 hai"
        elif "ben-" in text or "id" in text or "labharthi" in text:
            id_match = re.search(r"\b(ben[-\s]?\d+)\b", text, re.IGNORECASE)
            if id_match:
                modified_field = "beneficiary_id"
                prev_val = updated.get("beneficiary_id")
                new_val = id_match.group(0).upper().replace(" ", "-")
                updated["beneficiary_id"] = new_val

        # 4. Visit type correction: "visit ANC hai" / "PNC visit"
        elif any(vt in text for vt in ["anc", "pnc", "immunisation", "newborn", "teekakaran"]):
            for vt in ["ANC", "PNC", "IMMUNISATION", "NEWBORN"]:
                if vt.lower() in text or (vt == "IMMUNISATION" and "teeka" in text):
                    modified_field = "visit_type"
                    prev_val = updated.get("visit_type")
                    new_val = vt
                    updated["visit_type"] = new_val
                    break

        # Read back modified field specifically
        hi_readback = f"Theek hai, {modified_field} ko badalkar {new_val} kar diya gaya hai. Kya ab record save karein?"
        en_readback = f"Updated {modified_field} to {new_val}. Would you like to confirm and save this record now?"

        return SpokenCorrectionResponse(
            field_modified=modified_field,
            previous_value=prev_val,
            updated_value=new_val,
            updated_record=updated,
            readback_speech_hi=hi_readback,
            readback_speech_en=en_readback,
            ready_for_confirmation=True
        )

    @staticmethod
    def evaluate_confirmation(spoken_phrase: str) -> bool:
        """
        Deterministic verification of spoken confirmation.
        Accepts: 'haan', 'save karo', 'yes', 'confirm', 'theek hai', 'done'
        Rejects: 'nahi', 'cancel', 'wait', 'mat karo', 'ruk jao'
        """
        text = spoken_phrase.strip().lower()

        rejection_tokens = ["nahi", "no", "cancel", "mat", "ruk", "wait", "change", "galat"]
        if any(tok in text for tok in rejection_tokens):
            return False

        confirmation_tokens = [
            "haan", "ha", "yes", "save", "confirm", "theek hai", "sahi hai",
            "kar do", "save karo", "done", "pakka", "ok", "okay"
        ]
        return any(tok in text for tok in confirmation_tokens)


voice_orchestrator = VoiceOrchestrator()
