import { DangerSignMatch } from './danger';

export interface FieldEvidence {
  field_name: string;
  spoken_source: string;
  confidence: number;
  extracted_value: any;
}

export interface VisitRecord {
  id?: string;
  beneficiary_id?: string;
  beneficiary_name?: string;
  visit_type: string; // ANC, PNC, IMMUNISATION, NEWBORN
  visit_date: string;
  weight_kg?: number;
  blood_pressure?: string;
  ifa_tablets_given?: number;
  vaccinations_due: string[];
  vaccinations_completed: string[];
  anc_pnc_details?: Record<string, any>;
  next_visit_date?: string;
  visit_notes?: string;
  evidence: Record<string, FieldEvidence>;
  has_danger_sign: boolean;
  danger_sign_details?: DangerSignMatch[];
  referral_facility?: string;
  is_confirmed: boolean;
  created_at?: string;
}

export interface VisitRecordExtraction extends VisitRecord {
  missing_fields: string[];
  clarification_prompt_hi?: string;
  clarification_prompt_en?: string;
}
