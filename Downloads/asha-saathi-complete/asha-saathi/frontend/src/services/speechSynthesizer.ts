/**
 * Audio / Speech Synthesizer Service
 * Handles Gnani Timbre audio playback and browser SpeechSynthesis fallback.
 */

class SpeechSynthesizer {
  private currentAudio: HTMLAudioElement | null = null;

  public speak(
    text: string,
    options?: {
      audioBase64?: string | null;
      language?: string;
      onStart?: () => void;
      onEnd?: () => void;
    }
  ) {
    this.stop();

    // 1. If Gnani Timbre base64 audio is provided, play high-fidelity WAV
    if (options?.audioBase64) {
      try {
        const audio = new Audio(`data:audio/wav;base64,${options.audioBase64}`);
        this.currentAudio = audio;
        if (options.onStart) audio.onplay = options.onStart;
        if (options.onEnd) audio.onended = options.onEnd;
        audio.play().catch(e => {
          console.warn('Audio play prevented by browser policy, falling back to Web Speech:', e);
          this.speakBrowserTts(text, options);
        });
        return;
      } catch (err) {
        console.warn('Failed to play base64 audio:', err);
      }
    }

    // 2. Fallback to Browser Web Speech API
    this.speakBrowserTts(text, options);
  }

  private speakBrowserTts(
    text: string,
    options?: {
      language?: string;
      onStart?: () => void;
      onEnd?: () => void;
    }
  ) {
    if (!('speechSynthesis' in window)) {
      console.warn('SpeechSynthesis not supported in this browser.');
      options?.onEnd?.();
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = options?.language?.startsWith('ta') ? 'ta-IN' :
                     options?.language?.startsWith('te') ? 'te-IN' :
                     options?.language?.startsWith('mr') ? 'mr-IN' :
                     options?.language?.startsWith('en') ? 'en-IN' : 'hi-IN';
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    if (options?.onStart) utterance.onstart = options.onStart;
    if (options?.onEnd) utterance.onend = options.onEnd;
    utterance.onerror = () => options?.onEnd?.();

    window.speechSynthesis.speak(utterance);
  }

  public stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }
}

export const speechSynthesizer = new SpeechSynthesizer();
