"""
Recap API Endpoints
AI-powered video recap generation
"""
import os
import json
import re
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from app.core.config import settings


router = APIRouter()


# Request/Response Models
class RecapRequest(BaseModel):
    transcript: str = Field(..., description="Video transcript text")
    duration_minutes: float = Field(default=5, ge=1, le=60, description="Target duration in minutes")
    style: str = Field(default="engaging", description="Script style: engaging, formal, casual, technical")
    target_audience: str = Field(default="general", description="Target audience description")
    include_timestamps: bool = Field(default=True, description="Include timestamps in script")
    model: str = Field(default="anthropic/claude-3.5-sonnet", description="AI model to use")


class RecapResponse(BaseModel):
    success: bool
    script: str
    duration_estimate: float
    key_topics: List[str]
    hashtags: List[str]
    processing_time_ms: int


class TranscriptRequest(BaseModel):
    video_url: str = Field(..., description="URL to video file")
    language: str = Field(default="auto", description="Language code or 'auto' for detection")
    model_size: str = Field(default="base", description="Whisper model size: tiny, base, small, medium, large")


class TranscriptResponse(BaseModel):
    success: bool
    transcript_id: str
    text: str
    language: str
    duration: float
    segments: List[dict]


# OpenRouter API Client (for backend)
class OpenRouterClient:
    """OpenRouter API client for backend"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
    
    def _make_request(self, messages: List[dict], model: str = "anthropic/claude-3.5-sonnet", 
                      temperature: float = 0.7, max_tokens: Optional[int] = None) -> dict:
        import urllib.request
        import urllib.error
        
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.environ.get("VERCEL_URL", "https://recap-ai.vercel.app"),
            "X-Title": "Recap AI Backend",
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"OpenRouter API Error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def generate_recap(self, transcript: str, duration: float, style: str, 
                       audience: str, include_timestamps: bool) -> dict:
        """Generate recap script from transcript"""
        
        system_prompt = f"""You are a professional video script writer. Create an engaging recap script that:
- Captures key points and highlights
- Maintains viewer engagement
- Is suitable for {duration} minute video
- Targets {audience} audience
- Uses {style} tone
{'Include timestamps for each section.' if include_timestamps else ''}
"""

        user_prompt = f"""Create a recap script from this transcript:

---
{transcript[:8000]}  # Limit to avoid token limits
---

Format with clear sections: Introduction, Main Highlights, Key Takeaways, Conclusion."""

        response = self._make_request(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="anthropic/claude-3.5-sonnet",
            temperature=0.7,
            max_tokens=4000
        )
        
        return response["choices"][0]["message"]["content"]
    
    def extract_topics(self, text: str, num: int = 5) -> List[str]:
        """Extract key topics"""
        response = self._make_request(
            messages=[
                {"role": "system", "content": "Extract key topics from text. Return ONLY a JSON array of strings."},
                {"role": "user", "content": f"Extract {num} key topics:\n\n{text[:4000]}"}
            ],
            model="openai/gpt-4o-mini",
            temperature=0.3
        )
        
        content = response["choices"][0]["message"]["content"]
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return [t.strip() for t in content.split('\n') if t.strip()][:num]
    
    def generate_hashtags(self, content: str, num: int = 10) -> List[str]:
        """Generate hashtags"""
        response = self._make_request(
            messages=[
                {"role": "system", "content": "Generate relevant hashtags. Return ONLY a JSON array with # symbol."},
                {"role": "user", "content": f"Generate {num} hashtags:\n\n{content[:2000]}"}
            ],
            model="openai/gpt-4o-mini",
            temperature=0.7
        )
        
        content = response["choices"][0]["message"]["content"]
        hashtags = re.findall(r'#\w+', content)
        return hashtags[:num]


@router.post("/generate", response_model=RecapResponse)
async def generate_recap(request: RecapRequest):
    """
    Generate AI-powered recap script from transcript
    
    Uses OpenRouter API to generate an engaging video recap script.
    """
    if not settings.OPENROUTER_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API not configured. Set OPENROUTER_API_KEY."
        )
    
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript is required")
    
    start_time = datetime.now()
    
    try:
        client = OpenRouterClient()
        
        # Generate script
        script = client.generate_recap(
            transcript=request.transcript,
            duration=request.duration_minutes,
            style=request.style,
            audience=request.target_audience,
            include_timestamps=request.include_timestamps
        )
        
        # Extract topics
        topics = client.extract_topics(request.transcript, num=5)
        
        # Generate hashtags
        hashtags = client.generate_hashtags(request.transcript, num=10)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return RecapResponse(
            success=True,
            script=script,
            duration_estimate=request.duration_minutes,
            key_topics=topics,
            hashtags=hashtags,
            processing_time_ms=int(processing_time)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recap generation failed: {str(e)}")


@router.post("/transcribe", response_model=TranscriptResponse)
async def transcribe_video(request: TranscriptRequest):
    """
    Transcribe video audio to text
    
    Downloads video and extracts audio for transcription.
    """
    import whisper
    import subprocess
    import tempfile
    
    try:
        # Download video to temp file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        # Download from URL (simplified - would need proper URL handling)
        # For now, assume video is uploaded locally
        if request.video_url.startswith('/'):
            video_path = request.video_url
        else:
            # Download from URL
            import urllib.request
            urllib.request.urlretrieve(request.video_url, video_path)
        
        # Extract audio
        audio_path = video_path.replace('.mp4', '.wav')
        subprocess.run([
            'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1', audio_path, '-y'
        ], capture_output=True)
        
        # Load Whisper model
        model = whisper.load_model(request.model_size, device="cuda" if settings.WHISPER_DEVICE == "cuda" else "cpu")
        
        # Transcribe
        result = model.transcribe(audio_path, language=None if request.language == "auto" else request.language)
        
        # Cleanup temp files
        if video_path != request.video_url:
            os.unlink(video_path)
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        
        return TranscriptResponse(
            success=True,
            transcript_id=f"tr_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            text=result["text"],
            language=result.get("language", "unknown"),
            duration=result.get("duration", 0),
            segments=result.get("segments", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.get("/models")
async def list_available_models():
    """List available AI models"""
    return {
        "models": [
            {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "provider": "Anthropic"},
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic"},
            {"id": "openai/gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "provider": "OpenAI"},
            {"id": "meta-llama/llama-3-70b-instruct", "name": "Llama 3 70B", "provider": "Meta"},
            {"id": "google/gemini-pro", "name": "Gemini Pro", "provider": "Google"},
        ]
    }


@router.get("/styles")
async def list_script_styles():
    """List available script styles"""
    return {
        "styles": [
            {"id": "engaging", "name": "Engaging", "description": "Dynamic and captivating"},
            {"id": "formal", "name": "Formal", "description": "Professional and structured"},
            {"id": "casual", "name": "Casual", "description": "Relaxed and conversational"},
            {"id": "technical", "name": "Technical", "description": "Detailed and precise"},
            {"id": "educational", "name": "Educational", "description": "Clear explanations"},
        ]
    }
