import React, { useState, useEffect, useRef } from 'react';
import { X, Mic, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';
import { MicButton } from './MicButton';
import { AudioVisualizer } from './AudioVisualizer';
import { LiveTranscript } from './LiveTranscript';
import { DangerAlertBanner } from './DangerAlertBanner';
import { StructuredReview } from './StructuredReview';
import { api } from '../../services/api';
import { speechSynthesizer } from '../../services/speechSynthesizer';
import { VisitRecordExtraction } from '../../types/visit';
import { DangerShieldResult } from '../../types/danger';

interface VoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVisitSaved: () => void;
  selectedLanguage: string;
}

export const VoiceModal: React.FC<VoiceModalProps> = ({
  isOpen,
  onClose,
  onVisitSaved,
  selectedLanguage,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [statusMessage, setStatusMessage] = useState('Initializing ASHA Saathi...');
  const [extraction, setExtraction] = useState<VisitRecordExtraction | null>(null);
  const [dangerResult, setDangerResult] = useState<DangerShieldResult | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [sessionSuccess, setSessionSuccess] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition & First Turn AI Disclosure on Open
  useEffect(() => {
    if (!isOpen) {
      speechSynthesizer.stop();
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      setIsListening(false);
      setTranscript('');
      setExtraction(null);
      setDangerResult(null);
      setSessionSuccess(null);
      return;
    }

    // First Turn: Call AI intro endpoint and speak disclosure
    const initVoiceTurn = async () => {
      try {
        setIsProcessing(true);
        setStatusMessage('AI Sahayak shuru ho raha hai...');
        const intro = await api.getVoiceIntro(selectedLanguage);

        setIsProcessing(false);
        setStatusMessage('Namaste! ASHA Saathi sun raha hai. Mic dabayein.');

        // Speak AI disclosure
        setIsSpeaking(true);
        speechSynthesizer.speak(intro.text_hi, {
          audioBase64: intro.audio_payload?.audio_base64,
          language: selectedLanguage,
          onStart: () => setIsSpeaking(true),
          onEnd: () => setIsSpeaking(false),
        });
      } catch (err) {
        setIsProcessing(false);
        setStatusMessage('Tap microphone button to start speaking.');
      }
    };

    initVoiceTurn();

    // Setup Web Speech Recognition if available
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = selectedLanguage.startsWith('en') ? 'en-IN' : 'hi-IN';

      recognition.onstart = () => {
        setIsListening(true);
        setStatusMessage('Sun raha hoon... Boliye (e.g. BEN-001 ANC checkup, wajan 52 kilo)');
      };

      recognition.onresult = (event: any) => {
        let currentText = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          currentText += event.results[i][0].transcript;
        }
        setTranscript(currentText);

        // Check for spoken confirmation phrase on the fly!
        const lower = currentText.toLowerCase();
        if (extraction && (lower.includes('haan save') || lower.includes('yes save') || lower.includes('confirm'))) {
          handleConfirmSave();
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition event:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }

    return () => {
      speechSynthesizer.stop();
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [isOpen, selectedLanguage]);

  // Toggle Microphone
  const toggleRecording = () => {
    if (isListening) {
      // Stop recording and process
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      if (transcript.trim()) {
        processTranscript(transcript);
      }
    } else {
      // Start recording
      speechSynthesizer.stop();
      setIsSpeaking(false);
      setTranscript('');
      setExtraction(null);
      setDangerResult(null);
      setSessionSuccess(null);

      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (e) {
          console.warn('Recognition start caught:', e);
          setIsListening(true);
        }
      } else {
        // Fallback for environments where Web Speech is restricted
        setIsListening(true);
        setStatusMessage('Listening simulated... Use test chips below or speak.');
      }
    }
  };

  // Process completed spoken transcript
  const processTranscript = async (textToProcess: string) => {
    try {
      setIsProcessing(true);
      setStatusMessage('Extracting structured visit fields & evaluating danger signs...');

      // 1. Evaluate Danger Shield Deterministically
      const danger = await api.evaluateDangerSigns(textToProcess);
      setDangerResult(danger);

      // 2. Extract Structured Healthcare Fields
      const ext = await api.extractVisit(textToProcess);
      setExtraction(ext);

      setIsProcessing(false);

      // 3. If Danger Sign: Speak Immediate Emergency Referral Alert First!
      if (danger.has_danger_sign && danger.spoken_alert_hi) {
        setStatusMessage('EMERGENCY: Danger sign detected! Refer to PHC.');
        setIsSpeaking(true);
        speechSynthesizer.speak(danger.spoken_alert_hi, {
          language: selectedLanguage,
          onStart: () => setIsSpeaking(true),
          onEnd: () => {
            setIsSpeaking(false);
            // After alert, read back visit summary
            handleReadAloud(ext);
          },
        });
        return;
      }

      // 4. Voice Read-back of extracted fields
      setStatusMessage('Extracted successfully. Reading fields aloud for verification...');
      handleReadAloud(ext);
    } catch (err) {
      setIsProcessing(false);
      setStatusMessage('Error analyzing visit. Please repeat or check transcript.');
    }
  };

  // Voice Read-back Handler
  const handleReadAloud = async (recordToRead?: VisitRecordExtraction | null) => {
    const target = recordToRead || extraction;
    if (!target) return;

    try {
      const readback = await api.getVoiceReadback(target, selectedLanguage);
      setIsSpeaking(true);
      speechSynthesizer.speak(readback.readback_hi, {
        audioBase64: readback.audio_payload?.audio_base64,
        language: selectedLanguage,
        onStart: () => setIsSpeaking(true),
        onEnd: () => setIsSpeaking(false),
      });
    } catch (err) {
      console.warn('Readback error:', err);
    }
  };

  // Spoken Natural Correction Handler
  const handleApplyCorrection = async (correctionPhrase: string) => {
    if (!extraction) return;
    try {
      setIsProcessing(true);
      setStatusMessage(`Applying spoken correction: "${correctionPhrase}"...`);

      const resp = await api.submitVoiceCorrection(extraction, correctionPhrase);
      setExtraction(resp.updated_record as VisitRecordExtraction);
      setIsProcessing(false);

      // Read back the specific corrected field
      setIsSpeaking(true);
      speechSynthesizer.speak(resp.readback_speech_hi, {
        language: selectedLanguage,
        onStart: () => setIsSpeaking(true),
        onEnd: () => setIsSpeaking(false),
      });
      setStatusMessage(`Updated ${resp.field_modified}. Say "Haan save karo" to confirm.`);
    } catch (err) {
      setIsProcessing(false);
      setStatusMessage('Failed to update field.');
    }
  };

  // Final Confirmation & Save
  const handleConfirmSave = async () => {
    if (!extraction) return;

    try {
      setIsSaving(true);
      setStatusMessage('Saving confirmed visit record to field register...');

      const payload = {
        ...extraction,
        is_confirmed: true,
        has_danger_sign: dangerResult?.has_danger_sign || false,
        danger_sign_details: dangerResult?.detected_signs || [],
      };

      const saved = await api.confirmAndSaveVisit(payload);
      setIsSaving(false);
      setSessionSuccess(`Visit ${saved.id} successfully recorded! Follow-up tasks scheduled.`);

      // Spoken confirmation feedback
      setIsSpeaking(true);
      speechSynthesizer.speak("Visit record safaltapoorvak save ho gaya hai.", {
        language: selectedLanguage,
        onStart: () => setIsSpeaking(true),
        onEnd: () => {
          setIsSpeaking(false);
          setTimeout(() => {
            onVisitSaved();
            onClose();
          }, 1800);
        },
      });
    } catch (err: any) {
      setIsSaving(false);
      setStatusMessage(`Error: ${err.message}`);
    }
  };

  // Sample Selection (for Judge evaluation or simulated dictation)
  const handleSelectSample = (sampleText: string) => {
    setTranscript(sampleText);
    processTranscript(sampleText);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-slate-900/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl max-h-[92vh] bg-white rounded-3xl shadow-2xl overflow-y-auto flex flex-col border border-slate-200">
        
        {/* Modal Top Bar */}
        <div className="sticky top-0 z-20 bg-white/95 backdrop-blur-md px-5 py-3 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-teal-600 text-white flex items-center justify-center shadow-sm">
              <Mic className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm sm:text-base font-bold text-slate-900">
                AI Voice Visit Entry (ASHA Saathi)
              </h2>
              <span className="text-[11px] text-teal-700 font-semibold">
                Hands-Free Spoken Register • Zero Typing
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 sm:p-6 flex-1 flex flex-col">
          
          {/* Success Banner */}
          {sessionSuccess && (
            <div className="mb-4 p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-900 flex items-center space-x-3">
              <CheckCircle className="w-6 h-6 text-emerald-600 shrink-0" />
              <p className="text-sm font-bold">{sessionSuccess}</p>
            </div>
          )}

          {/* Danger Alert Banner (Module 4) */}
          {dangerResult && dangerResult.has_danger_sign && (
            <DangerAlertBanner
              dangerResult={dangerResult}
              onSpeakAlert={() => {
                if (dangerResult.spoken_alert_hi) {
                  speechSynthesizer.speak(dangerResult.spoken_alert_hi);
                }
              }}
            />
          )}

          {/* Central Animated Mic Button */}
          <MicButton
            isListening={isListening}
            isProcessing={isProcessing}
            isSpeaking={isSpeaking}
            onClick={toggleRecording}
            statusLabel={statusMessage}
          />

          {/* Audio Visualizer */}
          <AudioVisualizer
            isListening={isListening}
            barColor={dangerResult?.has_danger_sign ? '#dc2626' : '#0d9488'}
          />

          {/* Live Streaming Transcript */}
          <LiveTranscript
            transcript={transcript}
            isListening={isListening}
            onSelectSample={handleSelectSample}
          />

          {/* Structured Review & Spoken Confirmation (Module 2, 3) */}
          {extraction && (
            <StructuredReview
              extraction={extraction}
              onReadAloud={() => handleReadAloud()}
              onConfirmSave={handleConfirmSave}
              onApplyCorrection={handleApplyCorrection}
              isSaving={isSaving}
            />
          )}

        </div>
      </div>
    </div>
  );
};
