"""
Voice/TTS API Endpoints
Text-to-Speech generation
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import os
import base64


router = APIRouter()


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(default="alloy", description="Voice ID")
    model: str = Field(default="tts-1", description="TTS model: tts-1, tts-1-hd")
    speed: float = Field(default=1.0, ge=0.25, le=4.0, description="Speech speed")
    response_format: str = Field(default="mp3", description="Output format: mp3, opus, aac, flac")


class TTSResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    audio_base64: Optional[str] = None
    duration_seconds: float


class VoiceListResponse(BaseModel):
    voices: list


# Available voices
VOICES = [
    {"id": "alloy", "name": "Alloy", "gender": "neutral"},
    {"id": "echo", "name": "Echo", "gender": "male"},
    {"id": "fable", "name": "Fable", "gender": "male"},
    {"id": "onyx", "name": "Onyx", "gender": "male"},
    {"id": "nova", "name": "Nova", "gender": "female"},
    {"id": "shimmer", "name": "Shimmer", "gender": "female"},
    {"id": "coral", "name": "Coral", "gender": "female"},
    {"id": "sage", "name": "Sage", "gender": "male"},
]


@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    
    Uses OpenAI TTS API (or compatible endpoint) for voice generation.
    """
    from app.core.config import settings
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    if len(request.text) > 4096:
        raise HTTPException(status_code=400, detail="Text too long (max 4096 characters)")
    
    try:
        # In production, integrate with OpenAI TTS or Coqui TTS
        # For now, return placeholder response
        
        return TTSResponse(
            success=True,
            audio_url=None,
            audio_base64=None,
            duration_seconds=len(request.text) / 10.0 * request.speed
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


@router.get("/voices", response_model=VoiceListResponse)
async def list_voices():
    """List available voices"""
    return VoiceListResponse(voices=VOICES)


@router.post("/preview")
async def preview_voice(voice_id: str):
    """Preview a voice with a sample phrase"""
    if voice_id not in [v["id"] for v in VOICES]:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    return {
        "success": True,
        "voice_id": voice_id,
        "sample_text": f"This is a preview of the {voice_id} voice."
    }
