# Official Public Health Guidelines & Clinical Safety Protocols

ASHA Saathi's **Danger Shield Engine** is grounded exclusively in official public-health guidelines published by the Ministry of Health & Family Welfare (MoHFW), Government of India, and the World Health Organization (WHO).

---

## 1. Primary Guideline Citations

### A. Integrated Management of Neonatal and Childhood Illness (IMNCI)
- **Authority**: Ministry of Health & Family Welfare (MoHFW), Government of India, in collaboration with WHO and UNICEF.
- **Document**: *IMNCI Chart Booklet: Management of the Young Infant (Age 0 up to 2 Months)*.
- **Protocols Referenced**:
  1. **Possible Serious Bacterial Infection / Sepsis**:
     - Convulsions or fits.
     - Fast breathing (60 breaths per minute or more).
     - Severe chest indrawing (pasli chalna).
     - High body temperature (fever > 37.5°C or hot to touch).
     - Hypothermia (temperature < 35.5°C or cold to touch).
  2. **Severe Malnutrition & Feeding Problems**:
     - Not able to feed or suckle at all.
     - Stopped feeding after birth.
  3. **Lethargy / Unconsciousness**:
     - Abnormally sleepy, difficult to wake, or floppy/limp body.

### B. Home Based Newborn Care (HBNC) - ASHA Modules 6 & 7
- **Authority**: National Health Mission (NHM), Child Health Division, MoHFW, Govt of India.
- **Document**: *ASHA Training Modules 6 & 7: Skills That Save Lives (HBNC Operational Guidelines)*.
- **Protocols Referenced**:
  - Visit schedule: Day 1, 3, 7, 14, 21, 28 for institutional deliveries; extra Day 1 visit for home deliveries.
  - Temperature monitoring: Checking abdomen and soles for cold stress (Kangaroo Mother Care indication).
  - Cord care: Checking for bleeding, foul smell, or pus.
  - Mandatory immediate referral protocol to Primary Health Centre (PHC) / Special Newborn Care Unit (SNCU).

### C. Antenatal Care (ANC) & High-Risk Pregnancy Guidelines
- **Authority**: Maternal Health Division, MoHFW, Government of India.
- **Document**: *Guidelines for Antenatal Care and Skilled Attendance at Birth by ANMs/LHVs/SNs*.
- **Protocols Referenced**:
  - Four mandatory ANC visits: 1st within 12 weeks, 2nd 14–26 weeks, 3rd 28–34 weeks, 4th 36 weeks to term.
  - Identification of Danger Signs in Pregnancy:
    1. **Vaginal bleeding** (Antepartum Hemorrhage / Placenta Praevia / Abruptio Placentae).
    2. **Severe headache with blurring of vision** (Severe Pre-eclampsia).
    3. **Convulsions or loss of consciousness** (Eclampsia).
    4. **Severe abdominal pain**.
    5. **High fever with chills**.
    6. **Swelling of face, hands, and feet (edema)**.
    7. **Foul-smelling vaginal discharge or leaking amniotic fluid**.

---

## 2. Danger Shield Triage Decision Matrix

| Condition Code | Spoken Indic / English Keywords | Clinical Guideline | Severity | Mandatory Action |
|---|---|---|---|---|
| `PREG_BLEEDING` | "vaginal bleeding", "khoon aana", "khoon beh raha", "raktsrav", "spotting" | MoHFW ANC Guidelines Sec 4.2 | **EMERGENCY** | Refer immediately to First Referral Unit (FRU) / PHC. Rest in left lateral position. |
| `PREG_CONVULSIONS` | "convulsions", "fits", "daure padna", "jhatke aana", "mirgi" | MoHFW Eclampsia Protocol | **EMERGENCY** | Immediate emergency ambulance transfer to FRU. Keep airway clear. |
| `PREG_SEVERE_HEADACHE` | "severe headache", "blurred vision", "tez sir dard", "dhundhla dikhna" | MoHFW Pre-eclampsia Guideline | **EMERGENCY** | Refer to PHC for BP check & Magnesium Sulfate if indicated at center. |
| `NB_HIGH_FEVER` | "newborn fever", "infant fever", "tez bukhar", "garam hai", "102 degree" | IMNCI Young Infant Chart (p. 4) | **EMERGENCY** | Immediate referral to SNCU/PHC. Keep baby warm, no cold sponging. |
| `NB_HYPOTHERMIA` | "cold to touch", "baby is cold", "sharir thanda", "thanda pad gaya" | IMNCI Hypothermia Protocol | **EMERGENCY** | Immediate skin-to-skin Kangaroo Mother Care (KMC) + urgent PHC referral. |
| `NB_POOR_FEEDING` | "unable to feed", "not drinking milk", "doodh nahi pee raha", "cannot suckle" | IMNCI General Danger Signs | **EMERGENCY** | Check latch; if unable to feed at all, transport urgently to SNCU. |
| `NB_FAST_BREATHING` | "fast breathing", "chest indrawing", "pasli chal rahi hai", "tez saans" | IMNCI ARI Guideline (>60 breaths/min) | **EMERGENCY** | Immediate PHC referral. Keep infant warm during transit. |
| `NB_LETHARGY` | "lethargic", "unconscious", "bachha sust hai", "jag nahi raha", "behosh" | IMNCI Sick Infant Protocol | **EMERGENCY** | Urgent hospital transfer to SNCU/PHC. |

---

## 3. Explicit Negation Handling Rules

In rural healthcare dictation, ASHA workers frequently report negative findings to confirm good health:
- *"Koi bleeding nahi ho rahi hai"* (No bleeding is occurring)
- *"Bukhar nahi hai normal hai"* (No fever, it is normal)
- *"Bachha doodh theek se pee raha hai"* (Baby is drinking milk properly)

The **Danger Shield Engine** parses a 45-character semantic window around detected tokens. If an affirmative negation token (e.g. `nahi`, `no`, `not`, `denies`, `theek`) modifies the symptom, the engine classifies the symptom as **negative**, logs the negation reason, and suppresses false emergency alerts.

---

## 4. Responsible AI Guardrails & Limitations

1. **Zero Diagnostic Claims**: ASHA Saathi never generates medical diagnoses (e.g., it never states "The patient has sepsis" or "The mother has pre-eclampsia"). It identifies *danger signs* and prompts *referral*.
2. **Zero Treatment or Prescription Advice**: The system never suggests medications, antibiotics, or dosages.
3. **No Autonomous Decision-Making**: All referrals are strictly deterministically mapped from the approved MoHFW/IMNCI rulebook. General LLMs have no authority over danger sign decisions.
4. **Data Privacy (DPDP Act Compliance)**:
   - Uses 100% synthetic beneficiary data.
   - Session transcripts are encrypted at rest and discarded post-session.
   - Raw audio streams are never stored on persistent storage.
