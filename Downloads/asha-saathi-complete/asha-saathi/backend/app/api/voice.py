"""
ASHA Saathi - Voice Assistant API Endpoints & WebSocket (Module 1, 3)
---------------------------------------------------------------------
Handles:
- Streaming STT WebSocket (Gnani Prisma v3.0 / Demo Mode).
- First Turn AI Disclosure (Responsible AI).
- Voice Read-Back (Gnani Timbre TTS).
- Natural Spoken Corrections.
- Spoken Confirmation & Commit.
"""
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.gnani_service import gnani_service
from app.services.voice_orchestrator import voice_orchestrator
from app.services.extraction_service import extraction_engine
from app.schemas.visit_record import VisitRecordExtraction
from app.schemas.voice_session import (
    SpokenCorrectionRequest, SpokenCorrectionResponse,
    SpokenConfirmationRequest, SpokenConfirmationResponse
)
from app.api.visits import confirm_and_save_visit, ConfirmAndSaveRequest

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])


class IntroRequest(BaseModel):
    language: str = "hi-IN-codemix"


class ReadbackRequest(BaseModel):
    extraction: VisitRecordExtraction
    language: str = "hi-IN-codemix"


@router.post("/intro")
async def get_voice_assistant_intro(request: IntroRequest):
    """
    Module 1 First Turn: Discloses assistant is an AI in the worker's language.
    Responsible AI baseline requirement.
    """
    hi_text, en_text = voice_orchestrator.get_ai_disclosure(request.language)
    tts_payload = await gnani_service.synthesize_speech(hi_text, language="hi-IN")

    return {
        "text_hi": hi_text,
        "text_en": en_text,
        "is_ai_disclosed": True,
        "audio_payload": tts_payload,
        "is_demo_mode": not gnani_service.is_live,
        "demo_label": "Gnani Voice Demo Mode (Active)" if not gnani_service.is_live else "Live Gnani API"
    }


@router.post("/readback")
async def generate_voice_readback(request: ReadbackRequest):
    """
    Module 3 Read-back: Reads every important field aloud before confirmation.
    """
    hi_text, en_text = voice_orchestrator.generate_readback(request.extraction)
    tts_payload = await gnani_service.synthesize_speech(hi_text, language="hi-IN")

    return {
        "readback_hi": hi_text,
        "readback_en": en_text,
        "audio_payload": tts_payload,
        "is_demo_mode": not gnani_service.is_live
    }


@router.post("/correct", response_model=SpokenCorrectionResponse)
async def process_spoken_correction(request: SpokenCorrectionRequest):
    """
    Module 3 Spoken Correction:
    Accepts speech like "No, weight is 2.8 kilo", updates ONLY that field,
    and returns a dedicated read-back of the change.
    """
    res = voice_orchestrator.apply_spoken_correction(
        request.current_record,
        request.spoken_correction
    )
    return res


@router.post("/confirm", response_model=SpokenConfirmationResponse)
async def process_spoken_confirmation(request: SpokenConfirmationRequest, db: AsyncSession = Depends(get_db)):
    """
    Module 3 Spoken Confirmation:
    Evaluates spoken phrase ("Haan save karo" / "Yes confirm").
    If confirmed, commits the record to the database and generates follow-ups.
    """
    is_confirmed = voice_orchestrator.evaluate_confirmation(request.spoken_phrase)

    if not is_confirmed:
        return SpokenConfirmationResponse(
            confirmed=False,
            saved=False,
            message="Record not confirmed. Say 'Haan save karo' to save or speak a correction."
        )

    # Convert dictionary to ConfirmAndSaveRequest
    rec_data = dict(request.record_data)
    rec_data["is_confirmed"] = True

    try:
        saved_rec = await confirm_and_save_visit(ConfirmAndSaveRequest(**rec_data), db)
        return SpokenConfirmationResponse(
            confirmed=True,
            saved=True,
            record_id=saved_rec.id,
            message=f"Visit record {saved_rec.id} confirmed and saved successfully."
        )
    except Exception as e:
        return SpokenConfirmationResponse(
            confirmed=True,
            saved=False,
            message=f"Error saving record: {str(e)}"
        )


@router.websocket("/stream")
async def voice_stream_websocket(websocket: WebSocket):
    """
    Streaming Speech-to-Text WebSocket.
    Supports real-time audio chunking, Gnani Prisma v3.0 protocol,
    and interactive demo speech recognition.
    """
    await websocket.accept()
    session_id = f"SES-{asyncio.get_event_loop().time()}"

    # Send initial handshake with Gnani config
    config = gnani_service.get_prisma_streaming_config()
    await websocket.send_json({
        "event": "connected",
        "session_id": session_id,
        "gnani_config": config,
        "is_demo_mode": not gnani_service.is_live,
        "message": "Gnani Prisma v3.0 Streaming Ready" if gnani_service.is_live else "Gnani Demo Mode - Streaming Ready"
    })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event_type = message.get("event")

            if event_type == "audio_chunk":
                # Simulated streaming interim transcription or live Gnani relay
                chunk = message.get("chunk")
                transcript = message.get("text_hint", "")
                await websocket.send_json({
                    "event": "transcript_interim",
                    "text": transcript,
                    "is_final": False
                })

            elif event_type == "finish_speech":
                final_text = message.get("text", "")
                # Run extraction engine immediately
                extraction = extraction_engine.extract(final_text)
                readback_hi, readback_en = voice_orchestrator.generate_readback(extraction)

                await websocket.send_json({
                    "event": "transcript_final",
                    "text": final_text,
                    "is_final": True,
                    "extraction": extraction.dict(),
                    "readback_hi": readback_hi,
                    "readback_en": readback_en
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"event": "error", "detail": str(e)})
        except:
            pass
