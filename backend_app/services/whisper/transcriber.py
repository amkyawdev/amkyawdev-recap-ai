"""
Whisper Speech-to-Text Service
"""
import os
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from app.core.config import settings
from app.core.gpu_manager import gpu_manager


logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """Transcription result"""
    text: str
    language: str
    language_probability: float
    duration: float
    segments: List[Dict]
    words: Optional[List[Dict]] = None


class WhisperService:
    """Whisper-based speech recognition service"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._model = None
        self._model_size = settings.WHISPER_MODEL
        self._device = settings.WHISPER_DEVICE
    
    @property
    def model(self):
        """Lazy load Whisper model"""
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            import whisper
            
            device = gpu_manager.get_device() if self._device == "cuda" else "cpu"
            logger.info(f"Loading Whisper model: {self._model_size} on {device}")
            
            self._model = whisper.load_model(self._model_size, device=device)
            logger.info("Whisper model loaded successfully")
            
        except ImportError:
            logger.error("Whisper not installed. Run: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        verbose: bool = False,
        temperature: float = 0.0,
        condition_on_previous_text: bool = True,
        initial_prompt: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (None for auto-detect)
            task: "transcribe" or "translate"
            verbose: Print progress
            temperature: Sampling temperature
            condition_on_previous_text: Use previous segment as context
            initial_prompt: Initial prompt for better context
            
        Returns:
            TranscriptionResult object
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Acquire GPU for inference
        device_id = None
        if self._device == "cuda":
            device_id = gpu_manager.acquire_device()
        
        try:
            options = {
                "language": language,
                "task": task,
                "verbose": verbose,
                "temperature": temperature,
                "condition_on_previous_text": condition_on_previous_text,
            }
            
            if initial_prompt:
                options["initial_prompt"] = initial_prompt
            
            result = self.model.transcribe(audio_path, **options)
            
            return TranscriptionResult(
                text=result["text"],
                language=result.get("language", "unknown"),
                language_probability=result.get("language_probability", 0.0),
                duration=result.get("duration", 0.0),
                segments=result.get("segments", []),
                words=result.get("words"),
            )
            
        finally:
            if device_id is not None:
                gpu_manager.release_device(device_id)
    
    def transcribe_video(
        self,
        video_path: str,
        audio_output_path: Optional[str] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe video file (extracts audio first)
        
        Args:
            video_path: Path to video file
            audio_output_path: Optional path to save extracted audio
            **kwargs: Additional options for transcribe()
            
        Returns:
            TranscriptionResult object
        """
        import subprocess
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Extract audio
        if audio_output_path is None:
            audio_output_path = video_path.replace(
                os.path.splitext(video_path)[1], ".wav"
            )
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            "-y", audio_output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        try:
            return self.transcribe(audio_output_path, **kwargs)
        finally:
            # Cleanup temp audio if we created it
            if audio_output_path != video_path and os.path.exists(audio_output_path):
                os.unlink(audio_output_path)
    
    def segment_by_time(
        self,
        audio_path: str,
        max_segment_duration: float = 30.0,
        **kwargs
    ) -> List[TranscriptionResult]:
        """
        Transcribe audio with time-limited segments
        
        Useful for real-time processing or streaming.
        """
        result = self.transcribe(audio_path, **kwargs)
        
        segments = []
        for seg in result.segments:
            if seg.get("end", 0) - seg.get("start", 0) <= max_segment_duration:
                segments.append(seg)
        
        return segments
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper models"""
        return ["tiny", "base", "small", "medium", "large"]
    
    def get_model_info(self) -> Dict:
        """Get information about current model"""
        return {
            "model_size": self._model_size,
            "device": self._device,
            "loaded": self._model is not None,
        }


# Global instance
whisper_service = WhisperService()
