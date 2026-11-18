"""
ASHA Saathi - Gnani Voice Service Layer
---------------------------------------
Integration with official Gnani AI voice APIs:
- Gnani Prisma v3.0: Streaming speech-to-text with Indic code-mix support.
- Gnani Timbre: Text-to-speech synthesis for read-backs and emergency alerts.
- Healthcare keyterm prompting for medical vocabulary.
- Clearly-labeled Demo Mode when live credentials are not set.
"""
import json
import base64
from typing import AsyncGenerator, Dict, Any, Optional
import httpx

from app.config import settings


class GnaniService:
    def __init__(self):
        self.api_key = settings.GNANI_API_KEY
        self.token = settings.GNANI_TOKEN
        self.ws_url = settings.GNANI_PRISMA_WS_URL
        self.tts_url = settings.GNANI_TIMBRE_TTS_URL
        self.keyterms = settings.HEALTHCARE_KEYTERMS

    @property
    def is_live(self) -> bool:
        """Indicates whether real Gnani API credentials are active."""
        return settings.is_gnani_configured

    async def synthesize_speech(self, text: str, language: str = "hi-IN", speaker: str = "female") -> Dict[str, Any]:
        """
        Synthesize speech using Gnani Timbre API, or return a labeled demo audio payload.
        """
        if self.is_live:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "language": language,
                "audio_format": "wav",
                "speaker": speaker
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(self.tts_url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        audio_base64 = base64.b64encode(resp.content).decode("utf-8")
                        return {
                            "status": "success",
                            "is_demo_mode": False,
                            "audio_format": "wav",
                            "audio_base64": audio_base64,
                            "text": text
                        }
            except Exception as e:
                # Log error and fall back to labeled demo mode
                print(f"[Gnani Timbre Error]: {e}. Falling back to demo mode.")

        # Labeled Demo Mode: return labeled simulation with metadata
        return {
            "status": "success",
            "is_demo_mode": True,
            "demo_label": "Gnani Timbre Demo Mode (Web Speech Synthesis fallback)",
            "audio_format": "text_to_browser_tts",
            "audio_base64": None,
            "text": text,
            "language": language
        }

    def get_prisma_streaming_config(self, language: str = "hi-IN-codemix") -> Dict[str, Any]:
        """
        Returns initialization configuration for Gnani Prisma v3.0 streaming STT WebSocket.
        Includes health keyterm prompting and noise robustness configuration.
        """
        return {
            "service": "prisma_v3_streaming",
            "language": language,
            "code_mix": True,
            "keyterms": self.keyterms,
            "sample_rate": 16000,
            "encoding": "LINEAR16",
            "is_live_api": self.is_live,
            "demo_mode": not self.is_live
        }


gnani_service = GnaniService()
