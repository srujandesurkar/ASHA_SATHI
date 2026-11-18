import React from 'react';
import { Mic, ShieldCheck, Activity, Globe, Sparkles } from 'lucide-react';

interface NavbarProps {
  onOpenVoice: () => void;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
  isLiveGnani: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenVoice,
  selectedLanguage,
  onLanguageChange,
  isLiveGnani,
}) => {
  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        
        {/* Brand & AI Disclosure */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-600 to-emerald-600 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
            <Activity className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">ASHA Saathi</h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-teal-100 text-teal-800 border border-teal-200">
                <Sparkles className="w-3 h-3 mr-1 text-teal-600" />
                AI Voice Register
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium hidden sm:block">
              Indic Code-Mixed Voice Healthcare Assistant (MoHFW & IMNCI Aligned)
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Mode Pill */}
          <div className={`hidden md:inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${
            isLiveGnani 
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
              : 'bg-amber-50 text-amber-800 border-amber-200'
          }`}>
            <span className={`w-2 h-2 rounded-full mr-1.5 ${isLiveGnani ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'}`} />
            {isLiveGnani ? 'Gnani Prisma v3.0 Live' : 'Gnani Demo Mode'}
          </div>

          {/* Language Selector */}
          <div className="relative inline-flex items-center">
            <Globe className="w-4 h-4 absolute left-2.5 text-slate-400 pointer-events-none" />
            <select
              value={selectedLanguage}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs font-medium bg-slate-100 border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-2 focus:ring-teal-500"
            >
              <option value="hi-IN-codemix">Hindi (Hinglish)</option>
              <option value="en-IN">English (Indian)</option>
              <option value="mr-IN-codemix">Marathi</option>
              <option value="te-IN-codemix">Telugu</option>
              <option value="ta-IN-codemix">Tamil</option>
            </select>
          </div>

          {/* Big Voice Button in Navbar for fast field access */}
          <button
            onClick={onOpenVoice}
            className="flex items-center space-x-1.5 px-3 sm:px-4 py-2 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white rounded-xl text-sm font-semibold shadow-md shadow-teal-600/20 active:scale-95 transition-all"
          >
            <Mic className="w-4 h-4 animate-pulse" />
            <span>Voice Visit</span>
          </button>
        </div>

      </div>
    </header>
  );
};
