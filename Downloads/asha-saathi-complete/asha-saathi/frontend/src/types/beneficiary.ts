export interface Beneficiary {
  id: string;
  name: string;
  age?: number;
  phone?: string;
  village: string;
  asha_id: string;
  category: 'PREGNANT' | 'NEWBORN' | 'MOTHER_INFANT' | 'CHILD';
  lmp_date?: string;
  edd_date?: string;
  parity?: number;
  infant_dob?: string;
  infant_gender?: string;
  birth_weight_kg?: number;
  high_risk: boolean;
  high_risk_reason?: string;
  created_at?: string;
}
