import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Volume2, 
  FileText, 
  Calendar, 
  Scale, 
  Syringe, 
  UserCheck, 
  AlertCircle,
  Sparkles,
  Edit3
} from 'lucide-react';
import { VisitRecordExtraction } from '../../types/visit';

interface StructuredReviewProps {
  extraction: VisitRecordExtraction;
  onReadAloud: () => void;
  onConfirmSave: () => void;
  onApplyCorrection: (spokenCorrection: string) => void;
  isSaving: boolean;
}

export const StructuredReview: React.FC<StructuredReviewProps> = ({
  extraction,
  onReadAloud,
  onConfirmSave,
  onApplyCorrection,
  isSaving,
}) => {
  const [correctionInput, setCorrectionInput] = useState('');
  const [showManualCorrection, setShowManualCorrection] = useState(false);

  const handleQuickCorrection = (sample: string) => {
    onApplyCorrection(sample);
  };

  return (
    <div className="w-full bg-white border border-slate-200 rounded-2xl shadow-lg p-4 sm:p-5 my-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-teal-600" />
          <h3 className="font-bold text-slate-900 text-sm sm:text-base">
            Structured Healthcare Visit Record
          </h3>
        </div>
        <button
          onClick={onReadAloud}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-teal-50 text-teal-800 text-xs font-semibold hover:bg-teal-100 border border-teal-200 transition"
          title="Voice Read-Back"
        >
          <Volume2 className="w-4 h-4 text-teal-600" />
          <span>Read Aloud</span>
        </button>
      </div>

      {/* Grid of Extracted Fields */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
        {/* Beneficiary */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1">
            <span className="flex items-center space-x-1">
              <UserCheck className="w-3.5 h-3.5 text-teal-600" />
              <span>Beneficiary</span>
            </span>
            {extraction.evidence?.beneficiary_id && (
              <span className="text-[10px] bg-teal-100 text-teal-800 px-1.5 py-0.2 rounded font-medium">
                Spoken
              </span>
            )}
          </div>
          <div className="text-sm font-bold text-slate-900">
            {extraction.beneficiary_id ? (
              <span>
                {extraction.beneficiary_id}
                {extraction.beneficiary_name && (
                  <span className="text-slate-600 font-normal ml-1.5">
                    ({extraction.beneficiary_name})
                  </span>
                )}
              </span>
            ) : (
              <span className="text-amber-600 font-medium italic">Unspecified (Ask worker)</span>
            )}
          </div>
        </div>

        {/* Visit Type */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1">
            <span className="flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5 text-teal-600" />
              <span>Visit Type & Date</span>
            </span>
            <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-medium">
              {extraction.visit_date}
            </span>
          </div>
          <div className="text-sm font-bold text-slate-900">
            <span className="inline-block px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 font-bold mr-2">
              {extraction.visit_type || 'GENERAL'}
            </span>
          </div>
        </div>

        {/* Weight */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1">
            <span className="flex items-center space-x-1">
              <Scale className="w-3.5 h-3.5 text-teal-600" />
              <span>Weight</span>
            </span>
            {extraction.evidence?.weight_kg && (
              <span className="text-[10px] bg-teal-100 text-teal-800 px-1.5 py-0.2 rounded font-medium">
                {extraction.evidence.weight_kg.spoken_source}
              </span>
            )}
          </div>
          <div className="text-sm font-bold text-slate-900">
            {extraction.weight_kg !== null && extraction.weight_kg !== undefined ? (
              <span>{extraction.weight_kg} kg</span>
            ) : (
              <span className="text-slate-400 italic">Not recorded</span>
            )}
            {extraction.blood_pressure && (
              <span className="text-xs text-slate-600 ml-3">
                BP: <strong className="text-slate-900">{extraction.blood_pressure}</strong>
              </span>
            )}
          </div>
        </div>

        {/* Next Visit Date */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1">
            <span className="flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5 text-teal-600" />
              <span>Next Scheduled Visit</span>
            </span>
          </div>
          <div className="text-sm font-bold text-slate-900">
            {extraction.next_visit_date ? (
              <span className="text-teal-700">{extraction.next_visit_date}</span>
            ) : (
              <span className="text-amber-600 font-medium italic">Pending Schedule</span>
            )}
          </div>
        </div>
      </div>

      {/* Vaccinations Given & Due */}
      <div className="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
        <div className="flex items-center space-x-1 text-xs text-slate-500 font-semibold mb-2">
          <Syringe className="w-3.5 h-3.5 text-teal-600" />
          <span>Vaccinations Tracked (National Immunisation Schedule)</span>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          {extraction.vaccinations_completed && extraction.vaccinations_completed.length > 0 && (
            <div className="flex items-center space-x-1 bg-emerald-50 text-emerald-800 px-2 py-1 rounded-lg border border-emerald-200">
              <span className="font-bold">Given:</span>
              <span>{extraction.vaccinations_completed.join(', ')}</span>
            </div>
          )}
          {extraction.vaccinations_due && extraction.vaccinations_due.length > 0 && (
            <div className="flex items-center space-x-1 bg-amber-50 text-amber-800 px-2 py-1 rounded-lg border border-amber-200">
              <span className="font-bold">Due:</span>
              <span>{extraction.vaccinations_due.join(', ')}</span>
            </div>
          )}
          {(!extraction.vaccinations_completed || extraction.vaccinations_completed.length === 0) &&
           (!extraction.vaccinations_due || extraction.vaccinations_due.length === 0) && (
            <span className="text-slate-400 italic">No vaccines administered during this visit</span>
          )}
        </div>
      </div>

      {/* Voice Clarification Prompt if Missing Fields */}
      {extraction.missing_fields && extraction.missing_fields.length > 0 && (
        <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start space-x-2 text-xs text-amber-800">
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong className="block font-semibold">Clarification Required by Voice:</strong>
            <p className="mt-0.5">{extraction.clarification_prompt_hi}</p>
          </div>
        </div>
      )}

      {/* Spoken Correction Drawer */}
      <div className="mt-3 pt-3 border-t border-slate-100">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-600 flex items-center">
            <Sparkles className="w-3 h-3 mr-1 text-teal-600" />
            Spoken Natural Corrections:
          </span>
          <button
            onClick={() => setShowManualCorrection(!showManualCorrection)}
            className="text-xs text-teal-600 hover:text-teal-700 font-medium"
          >
            {showManualCorrection ? 'Hide' : 'Quick Voice Corrections'}
          </button>
        </div>

        {showManualCorrection && (
          <div className="mt-2 p-2.5 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <div className="flex flex-wrap gap-1.5 text-xs">
              <button
                type="button"
                onClick={() => handleQuickCorrection("No, weight is 2.8 kilo")}
                className="px-2 py-1 bg-white border border-slate-200 rounded-lg hover:border-teal-400 text-slate-700"
              >
                "No, weight is 2.8 kilo"
              </button>
              <button
                type="button"
                onClick={() => handleQuickCorrection("Nahi agla visit 25 tareekh ko hai")}
                className="px-2 py-1 bg-white border border-slate-200 rounded-lg hover:border-teal-400 text-slate-700"
              >
                "Nahi agla visit 25 tareekh ko hai"
              </button>
              <button
                type="button"
                onClick={() => handleQuickCorrection("Beneficiary ID BEN-001 hai")}
                className="px-2 py-1 bg-white border border-slate-200 rounded-lg hover:border-teal-400 text-slate-700"
              >
                "Beneficiary ID BEN-001 hai"
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Spoken Confirmation Action Bar */}
      <div className="mt-4 pt-3 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-2">
        <p className="text-xs text-slate-500 font-medium text-center sm:text-left">
          Say <strong className="text-teal-700">"Haan save karo"</strong> into mic, or tap button to confirm.
        </p>
        <button
          onClick={onConfirmSave}
          disabled={isSaving}
          className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white text-sm font-bold shadow-md shadow-teal-600/20 active:scale-95 transition flex items-center justify-center space-x-1.5"
        >
          <CheckCircle2 className="w-4 h-4" />
          <span>{isSaving ? 'Saving...' : 'Confirm & Save Visit (हाँ save करो)'}</span>
        </button>
      </div>
    </div>
  );
};
