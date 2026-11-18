import React from 'react';
import { Mic, MicOff, Loader2, Volume2 } from 'lucide-react';

interface MicButtonProps {
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  onClick: () => void;
  statusLabel?: string;
}

export const MicButton: React.FC<MicButtonProps> = ({
  isListening,
  isProcessing,
  isSpeaking,
  onClick,
  statusLabel,
}) => {
  return (
    <div className="flex flex-col items-center justify-center my-4">
      <div className="relative">
        {/* Animated Ripple Circles when Listening */}
        {isListening && (
          <div className="absolute inset-0 rounded-full bg-teal-400/40 animate-voice-ripple pointer-events-none" />
        )}

        {/* Main Big Button */}
        <button
          onClick={onClick}
          disabled={isProcessing}
          aria-label="Start Voice Recording"
          className={`relative z-10 w-24 h-24 sm:w-28 sm:h-28 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-xl active:scale-95 ${
            isProcessing
              ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
              : isSpeaking
              ? 'bg-gradient-to-tr from-indigo-600 to-blue-500 text-white shadow-blue-500/30 ring-4 ring-blue-300'
              : isListening
              ? 'bg-gradient-to-tr from-rose-600 to-red-500 text-white shadow-red-500/40 ring-8 ring-red-200'
              : 'bg-gradient-to-tr from-teal-600 to-emerald-500 text-white shadow-teal-500/30 hover:shadow-teal-500/50 hover:scale-105'
          }`}
        >
          {isProcessing ? (
            <Loader2 className="w-10 h-10 animate-spin" />
          ) : isSpeaking ? (
            <Volume2 className="w-10 h-10 animate-pulse" />
          ) : isListening ? (
            <Mic className="w-11 h-11 animate-pulse" />
          ) : (
            <Mic className="w-11 h-11 stroke-[2.2]" />
          )}

          <span className="text-[11px] font-bold mt-1 tracking-wider uppercase">
            {isProcessing ? 'Thinking' : isSpeaking ? 'Speaking' : isListening ? 'Stop' : 'Speak'}
          </span>
        </button>
      </div>

      {/* Spoken Status Text */}
      <p className="mt-3 text-sm font-semibold text-slate-700 tracking-tight text-center px-4">
        {statusLabel || (isListening ? 'Boliye, ASHA Saathi sun raha hai...' : 'Tap the mic to record visit')}
      </p>
    </div>
  );
};
