import { Beneficiary } from '../types/beneficiary';
import { VisitRecord, VisitRecordExtraction } from '../types/visit';
import { FollowUpTask } from '../types/followUp';
import { DangerShieldResult } from '../types/danger';

const API_BASE = '/api';

export const api = {
  // Health
  async getHealth() {
    const res = await fetch('/health');
    return res.json();
  },

  // Dashboard
  async getDashboardStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error('Failed to fetch dashboard stats');
    return res.json();
  },

  // Beneficiaries
  async getBeneficiaries(search?: string, village?: string): Promise<Beneficiary[]> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (village) params.append('village', village);
    const res = await fetch(`${API_BASE}/beneficiaries?${params.toString()}`);
    return res.json();
  },

  // Follow-up Tasks
  async getFollowUps(status?: string): Promise<FollowUpTask[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    const res = await fetch(`${API_BASE}/follow-ups?${params.toString()}`);
    return res.json();
  },

  async completeFollowUp(taskId: string): Promise<FollowUpTask> {
    const res = await fetch(`${API_BASE}/follow-ups/${taskId}/complete`, {
      method: 'PATCH',
    });
    return res.json();
  },

  // Visits
  async extractVisit(speechText: string): Promise<VisitRecordExtraction> {
    const res = await fetch(`${API_BASE}/visits/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speech_text: speechText }),
    });
    if (!res.ok) throw new Error('Extraction failed');
    return res.json();
  },

  async confirmAndSaveVisit(record: Partial<VisitRecord>): Promise<VisitRecord> {
    const res = await fetch(`${API_BASE}/visits/confirm-and-save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to save visit record');
    }
    return res.json();
  },

  async getVisits(): Promise<VisitRecord[]> {
    const res = await fetch(`${API_BASE}/visits`);
    return res.json();
  },

  // Voice Assistant Flow
  async getVoiceIntro(language = 'hi-IN-codemix') {
    const res = await fetch(`${API_BASE}/voice/intro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language }),
    });
    return res.json();
  },

  async getVoiceReadback(extraction: VisitRecordExtraction, language = 'hi-IN-codemix') {
    const res = await fetch(`${API_BASE}/voice/readback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ extraction, language }),
    });
    return res.json();
  },

  async submitVoiceCorrection(currentRecord: Record<string, any>, spokenCorrection: string) {
    const res = await fetch(`${API_BASE}/voice/correct`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: 'SES-ACTIVE',
        spoken_correction: spokenCorrection,
        current_record: currentRecord,
      }),
    });
    return res.json();
  },

  async submitVoiceConfirmation(recordData: Record<string, any>, spokenPhrase: string) {
    const res = await fetch(`${API_BASE}/voice/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: 'SES-ACTIVE',
        spoken_phrase: spokenPhrase,
        record_data: recordData,
      }),
    });
    return res.json();
  },

  // Danger Shield direct check
  async evaluateDangerSigns(speechTranscript: string): Promise<DangerShieldResult> {
    const res = await fetch(`${API_BASE}/danger-signs/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speech_transcript: speechTranscript }),
    });
    return res.json();
  },
};
