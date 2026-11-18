import React, { useState, useEffect } from 'react';
import { Mic, RefreshCw, Shield, Sparkles, BookOpen, Stethoscope, HeartHandshake } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { StatCards } from './components/Dashboard/StatCards';
import { ReferralAlertsList } from './components/Dashboard/ReferralAlertsList';
import { FollowUpBoard } from './components/Dashboard/FollowUpBoard';
import { BeneficiaryList } from './components/Beneficiaries/BeneficiaryList';
import { VoiceModal } from './components/VoiceAssistant/VoiceModal';
import { api } from './services/api';
import { Beneficiary } from './types/beneficiary';
import { FollowUpTask } from './types/followUp';

export const App: React.FC = () => {
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('hi-IN-codemix');
  const [isLiveGnani, setIsLiveGnani] = useState(false);
  const [loading, setLoading] = useState(true);

  // Dashboard Data
  const [stats, setStats] = useState({
    total_visits: 0,
    pregnancy_visits: 0,
    newborn_visits: 0,
    immunisation_visits: 0,
    urgent_referrals: 0,
    pending_follow_ups: 0,
    overdue_follow_ups: 0,
    high_risk_beneficiaries: 0,
    recent_visits: [] as any[],
    urgent_tasks: [] as any[],
  });

  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([]);
  const [followUpTasks, setFollowUpTasks] = useState<FollowUpTask[]>([]);

  // Load Data
  const loadAllData = async () => {
    try {
      setLoading(true);
      const [healthRes, statsRes, benRes, taskRes] = await Promise.all([
        api.getHealth(),
        api.getDashboardStats(),
        api.getBeneficiaries(),
        api.getFollowUps(),
      ]);

      setIsLiveGnani(healthRes.gnani_live_api);
      setStats(statsRes);
      setBeneficiaries(benRes);
      setFollowUpTasks(taskRes);
      setLoading(false);
    } catch (err) {
      console.warn('Error loading dashboard data:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleStartBeneficiaryVisit = (ben: Beneficiary) => {
    setIsVoiceOpen(true);
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      await api.completeFollowUp(taskId);
      loadAllData();
    } catch (err) {
      console.warn('Error completing task:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-24">
      {/* Navbar with AI Badge & Language Selector */}
      <Navbar
        onOpenVoice={() => setIsVoiceOpen(true)}
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
        isLiveGnani={isLiveGnani}
      />

      {/* Main Content Container */}
      <main className="max-w-6xl mx-auto px-4 py-4 sm:py-6">
        
        {/* Hero Field Header */}
        <div className="bg-gradient-to-r from-teal-700 via-teal-800 to-emerald-900 text-white rounded-3xl p-5 sm:p-7 shadow-lg mb-6 relative overflow-hidden">
          <div className="relative z-10 max-w-2xl">
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/15 backdrop-blur-md border border-white/20 mb-3">
              <Sparkles className="w-3.5 h-3.5 text-teal-300" />
              <span>Voice AI Field Register for ASHA Workers</span>
            </div>
            <h2 className="text-xl sm:text-3xl font-extrabold tracking-tight leading-tight">
              Record visits naturally by speech. Zero typing between houses.
            </h2>
            <p className="mt-2 text-xs sm:text-sm text-teal-100/90 font-medium leading-relaxed">
              Speaks Indic code-mixed speech (Hinglish/Hindi), validates structured healthcare records,
              reads back for verbal confirmation, and automatically flags danger signs per MoHFW guidelines.
            </p>

            <div className="mt-4 flex flex-wrap items-center gap-3">
              <button
                onClick={() => setIsVoiceOpen(true)}
                className="px-5 py-2.5 rounded-xl bg-white text-teal-900 hover:bg-teal-50 font-bold text-sm shadow-md active:scale-95 transition flex items-center space-x-2"
              >
                <Mic className="w-4 h-4 text-teal-700" />
                <span>Start Spoken Visit Note</span>
              </button>

              <button
                onClick={loadAllData}
                className="px-3.5 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium text-xs backdrop-blur-sm border border-white/10 transition flex items-center space-x-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh Register</span>
              </button>
            </div>
          </div>

          {/* Decorative Background Elements */}
          <div className="absolute right-[-40px] bottom-[-40px] opacity-10 pointer-events-none">
            <Stethoscope className="w-72 h-72 text-white" />
          </div>
        </div>

        {/* 1. Stat Cards (Module 6) */}
        <StatCards stats={stats} />

        {/* 2. Urgent Referral Alerts (Module 4 Danger Shield) */}
        <ReferralAlertsList
          urgentTasks={stats.urgent_tasks}
          onSelectBeneficiary={(id) => {
            setIsVoiceOpen(true);
          }}
        />

        {/* 3. Follow-Up Task Register (Module 5) */}
        <FollowUpBoard
          tasks={followUpTasks}
          onCompleteTask={handleCompleteTask}
        />

        {/* 4. Catchment Beneficiaries (Synthetic Data) */}
        <BeneficiaryList
          beneficiaries={beneficiaries}
          onStartVoiceVisit={handleStartBeneficiaryVisit}
        />

        {/* Public Health & Responsible AI Baseline Banner */}
        <footer className="mt-10 pt-6 border-t border-slate-200 text-xs text-slate-500 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-teal-600" />
            <span>
              <strong>Responsible AI:</strong> Synthetic data only • No clinical diagnosis or dosages • MoHFW / IMNCI referral protocols
            </span>
          </div>
          <div className="text-[11px] text-slate-400">
            Gnani Voice AI Platform • PS1 Healthcare Prototype
          </div>
        </footer>
      </main>

      {/* Floating Action Microphone Button (Mobile-First Accessible) */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsVoiceOpen(true)}
          aria-label="Record Visit by Voice"
          className="w-16 h-16 rounded-full bg-gradient-to-r from-teal-600 to-emerald-600 text-white shadow-2xl shadow-teal-700/50 flex items-center justify-center hover:scale-110 active:scale-95 transition-all duration-200 border-2 border-white ring-4 ring-teal-200/50"
        >
          <Mic className="w-8 h-8 stroke-[2.2]" />
        </button>
      </div>

      {/* Voice Assistant Modal / Drawer (Modules 1, 2, 3, 4) */}
      <VoiceModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
        onVisitSaved={loadAllData}
        selectedLanguage={selectedLanguage}
      />
    </div>
  );
};
