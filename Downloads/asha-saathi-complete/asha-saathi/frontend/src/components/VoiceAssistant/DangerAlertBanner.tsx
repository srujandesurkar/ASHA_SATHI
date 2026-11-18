import React from 'react';
import { AlertOctagon, PhoneCall, Building2, ShieldAlert, Volume2 } from 'lucide-react';
import { DangerShieldResult } from '../../types/danger';

interface DangerAlertBannerProps {
  dangerResult: DangerShieldResult;
  onSpeakAlert?: () => void;
}

export const DangerAlertBanner: React.FC<DangerAlertBannerProps> = ({
  dangerResult,
  onSpeakAlert,
}) => {
  if (!dangerResult.has_danger_sign) return null;

  return (
    <div className="my-3 p-4 bg-red-600 text-white rounded-2xl shadow-xl border-2 border-red-700 animate-danger-pulse">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
            <AlertOctagon className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-widest bg-red-800/80 px-2.5 py-0.5 rounded-full border border-red-400">
              Emergency Danger Sign Detected
            </span>
            <h3 className="text-base font-extrabold tracking-tight mt-1">
              Immediate PHC / FRU Referral Required
            </h3>
          </div>
        </div>

        {onSpeakAlert && (
          <button
            onClick={onSpeakAlert}
            className="p-2 bg-white/20 hover:bg-white/30 rounded-xl transition text-white"
            title="Read Alert Aloud"
          >
            <Volume2 className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Detected Signs */}
      <div className="mt-3 bg-red-800/60 rounded-xl p-3 border border-red-400/40">
        <p className="text-xs font-semibold text-red-200 uppercase tracking-wide">
          Identified Clinical Danger Signs:
        </p>
        <ul className="mt-1 space-y-1">
          {dangerResult.detected_signs.map((sign, idx) => (
            <li key={idx} className="flex items-start text-xs sm:text-sm font-medium">
              <span className="text-red-300 mr-2">•</span>
              <span>
                <strong className="text-white">{sign.sign_name}</strong>
                <span className="text-red-200 text-xs ml-1.5">
                  (Matched: "{sign.matched_term}")
                </span>
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* Spoken Referral Instruction */}
      {dangerResult.spoken_alert_hi && (
        <div className="mt-3 text-xs sm:text-sm bg-white/10 rounded-lg p-2.5 font-medium border border-white/10">
          <span className="text-red-200 font-bold block text-[11px] uppercase tracking-wider">
            Official Spoken Referral Notice:
          </span>
          <p className="italic text-white mt-0.5">"{dangerResult.spoken_alert_hi}"</p>
        </div>
      )}

      {/* Guideline Citation & Safety Notice */}
      <div className="mt-3 pt-2.5 border-t border-red-500/50 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-red-100 space-y-1 sm:space-y-0">
        <div className="flex items-center space-x-1">
          <ShieldAlert className="w-3.5 h-3.5 text-red-300" />
          <span>Protocol: MoHFW High-Risk Pregnancy / IMNCI Sick Newborn Protocol</span>
        </div>
        <span className="font-semibold text-white">
          Rule: Referral only • No medicine/diagnosis given
        </span>
      </div>
    </div>
  );
};
