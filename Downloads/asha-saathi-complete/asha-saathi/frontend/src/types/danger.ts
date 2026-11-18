export interface DangerSignMatch {
  category: 'PREGNANCY' | 'NEWBORN';
  sign_code: string;
  sign_name: string;
  matched_term: string;
  severity: 'EMERGENCY' | 'URGENT';
  guideline_source: string;
  immediate_action: string;
}

export interface DangerShieldResult {
  has_danger_sign: boolean;
  priority: 'EMERGENCY' | 'URGENT' | 'NORMAL';
  detected_signs: DangerSignMatch[];
  negations_detected: string[];
  spoken_alert_hi?: string;
  spoken_alert_en?: string;
  referral_required: boolean;
  recommended_facility?: string;
}
