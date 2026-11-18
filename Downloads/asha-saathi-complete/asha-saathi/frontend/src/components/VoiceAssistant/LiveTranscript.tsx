import React from 'react';
import { Sparkles, MessageSquare, Mic, Volume2 } from 'lucide-react';

interface LiveTranscriptProps {
  transcript: string;
  isListening: boolean;
  onSelectSample?: (sampleText: string) => void;
}

const SAMPLE_HEALTH_PHRASES = [
  {
    label: "ANC Routine",
    text: "Beneficiary BEN-001 ka ANC checkup kiya. Wajan 52 kilo hai, BP 120/80 aur 30 IFA goli di. Agla visit 25 November ko hai."
  },
  {
    label: "Newborn HBNC",
    text: "Navjaat shishu BEN-002 ka HBNC checkup kiya. Bachhe ka wajan 2.8 kilo hai. Doodh theek se pee raha hai. Agla visit 2 hafte baad hoga."
  },
  {
    label: "Emergency Bleeding",
    text: "Beneficiary BEN-001 ko subah se vaginal bleeding ho rahi hai aur pet me bahut tez dard hai."
  },
  {
    label: "Newborn Fever",
    text: "BEN-002 navjaat shishu ka sharir garam hai, tez bukhar hai aur doodh nahi pee raha."
  },
  {
    label: "Negation Safe",
    text: "Labharthi bilkul theek hai, koi bleeding nahi hai aur bukhar bhi nahi hai. Normal checkup."
  },
  {
    label: "Immunisation",
    text: "Labharthi BEN-004 ko BCG aur OPV de diya hai. Pentavalent lagna baaki hai agle mahine. Wajan 3.5 kilo."
  }
];

export const LiveTranscript: React.FC<LiveTranscriptProps> = ({
  transcript,
  isListening,
  onSelectSample,
}) => {
  return (
    <div className="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 my-2">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-teal-600" />
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            Live Spoken Transcript
          </h4>
        </div>
        <div className="flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span className="text-[11px] font-semibold text-slate-500">
            {isListening ? 'Streaming STT (16kHz PCM)' : 'Transcript Ready'}
          </span>
        </div>
      </div>

      {/* Transcript Box */}
      <div className="min-h-[72px] bg-white rounded-xl p-3 border border-slate-200 shadow-inner text-sm text-slate-800 leading-relaxed font-medium">
        {transcript ? (
          <p className="whitespace-pre-wrap">{transcript}</p>
        ) : (
          <p className="text-slate-400 italic">
            Spoken notes will appear here in real-time as you speak in Hindi, Hinglish, or English...
          </p>
        )}
      </div>

      {/* Quick Test Chips for Hackathon Judges */}
      {onSelectSample && (
        <div className="mt-3 pt-2.5 border-t border-slate-200">
          <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-1.5 flex items-center">
            <Sparkles className="w-3 h-3 mr-1 text-teal-600" />
            Quick Test Dictation (Judge / Demo Shortcuts):
          </p>
          <div className="flex flex-wrap gap-1.5">
            {SAMPLE_HEALTH_PHRASES.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSelectSample(sample.text)}
                className="px-2.5 py-1 text-xs font-medium rounded-lg bg-teal-50 text-teal-800 border border-teal-200 hover:bg-teal-100 hover:border-teal-300 transition active:scale-95"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
