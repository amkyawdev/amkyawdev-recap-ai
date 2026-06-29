"""
Translation Service
Supports multiple translation APIs and local models
"""
import os
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from app.core.config import settings
from app.core.gpu_manager import gpu_manager


logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Translation result"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float = 1.0
    alternatives: Optional[List[str]] = None


class TranslationService:
    """Multi-provider translation service"""
    
    def __init__(self):
        self._openrouter_client = None
        
        # Supported languages
        self.languages = {
            "en": "English",
            "my": "Myanmar (Burmese)",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "th": "Thai",
            "vi": "Vietnamese",
            "id": "Indonesian",
            "ms": "Malay",
            "hi": "Hindi",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ar": "Arabic",
            "lo": "Lao",
            "km": "Khmer",
            "tl": "Tagalog",
        }
    
    def _get_openrouter_client(self):
        """Get or create OpenRouter client"""
        if self._openrouter_client is None:
            import json
            import urllib.request
            import urllib.error
            
            api_key = settings.OPENROUTER_API_KEY or os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OpenRouter API key not configured")
            
            self._openrouter_client = {
                "api_key": api_key,
                "base_url": "https://openrouter.ai/api/v1"
            }
        
        return self._openrouter_client
    
    def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        style: str = "neutral",
    ) -> TranslationResult:
        """
        Translate text using OpenRouter API
        
        Args:
            text: Text to translate
            source_language: Source language code (or "auto")
            target_language: Target language code
            style: Translation style (neutral, formal, casual, preserve_formatting)
            
        Returns:
            TranslationResult object
        """
        client = self._get_openrouter_client()
        
        source_lang = self.languages.get(source_language, source_language)
        target_lang = self.languages.get(target_language, target_language)
        
        style_instructions = {
            "neutral": "Translate naturally and accurately.",
            "formal": "Use formal language appropriate for professional contexts.",
            "casual": "Use casual, conversational language.",
            "preserve_formatting": "Preserve the original formatting, line breaks, and structure.",
        }
        
        system_prompt = f"""You are a professional translator. Translate the following text from {source_lang} to {target_lang}.
{style_instructions.get(style, style_instructions['neutral'])}
Only return the translation, nothing else."""
        
        try:
            import json
            
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text[:8000]}  # Limit text length
                ],
                "temperature": 0.3,
                "max_tokens": 4000,
            }
            
            data = json.dumps(payload).encode("utf-8")
            
            req = urllib.request.Request(
                f"{client['base_url']}/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {client['api_key']}",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
            
            translated_text = result["choices"][0]["message"]["content"].strip()
            
            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                confidence=0.95,
            )
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"Translation API error {e.code}: {error_body}")
        except Exception as e:
            raise Exception(f"Translation failed: {e}")
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str = "en",
        source_language: str = "auto",
    ) -> List[TranslationResult]:
        """
        Translate multiple texts
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            List of TranslationResult objects
        """
        combined_text = "\n---\n".join(texts)
        
        result = self.translate(
            combined_text,
            source_language=source_language,
            target_language=target_language,
        )
        
        # Split back into individual translations
        translations = result.translated_text.split("\n---\n")
        
        return [
            TranslationResult(
                original_text=original,
                translated_text=translated.strip(),
                source_language=source_language,
                target_language=target_language,
            )
            for original, translated in zip(texts, translations)
        ]
    
    def translate_subtitles(
        self,
        subtitle_text: str,
        target_language: str,
        source_language: str = "auto",
        format: str = "srt"
    ) -> str:
        """
        Translate subtitles (SRT/VTT format)
        
        Preserves timing and formatting.
        """
        import re
        
        if format == "srt":
            # SRT format: index, time, text
            pattern = r"(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\s*\n([\s\S]*?)(?=\n\n\d+\s*\n|\Z)"
        elif format == "vtt":
            # VTT format
            pattern = r"(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*\n([\s\S]*?)(?=\n\n|\Z)"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        segments = re.findall(pattern, subtitle_text, re.MULTILINE)
        
        translated_segments = []
        for segment in segments:
            if format == "srt":
                index, start, end, text = segment
                translated = self.translate(text, source_language, target_language)
                translated_segments.append(
                    f"{index}\n{start} --> {end}\n{translated.translated_text}"
                )
            else:
                start, end, text = segment
                translated = self.translate(text, source_language, target_language)
                translated_segments.append(
                    f"{start} --> {end}\n{translated.translated_text}"
                )
        
        if format == "srt":
            return "\n\n".join(translated_segments)
        else:
            return "WEBVTT\n\n" + "\n\n".join(translated_segments)
    
    def detect_language(self, text: str) -> Dict[str, float]:
        """
        Detect language of text
        
        Returns dict of language codes with confidence scores.
        """
        # Simple heuristic-based detection
        # In production, use a proper language detection library
        
        text_lower = text.lower()
        
        # Myanmar (Burmese) - has unique characters
        if any('\u1000' <= c <= '\u109f' for c in text):
            return {"my": 0.99}
        
        # Thai
        if any('\u0e00' <= c <= '\u0e7f' for c in text):
            return {"th": 0.99}
        
        # Chinese
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return {"zh": 0.99}
        
        # Japanese
        if any('\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in text):
            return {"ja": 0.90, "zh": 0.80}
        
        # Korean
        if any('\uac00' <= c <= '\ud7af' for c in text):
            return {"ko": 0.99}
        
        # Arabic
        if any('\u0600' <= c <= '\u06ff' for c in text):
            return {"ar": 0.99}
        
        # Use OpenRouter for complex cases
        try:
            client = self._get_openrouter_client()
            
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Detect the language of the following text. Return ONLY the ISO 639-1 language code (e.g., 'en', 'my', 'zh')."},
                    {"role": "user", "content": text[:500]}
                ],
                "temperature": 0.0,
            }
            
            data = json.dumps(payload).encode("utf-8")
            
            req = urllib.request.Request(
                f"{client['base_url']}/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {client['api_key']}",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
            
            lang_code = result["choices"][0]["message"]["content"].strip().lower()
            
            return {lang_code: 0.95}
            
        except:
            return {"en": 0.50}
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported languages"""
        return self.languages.copy()
    
    def get_language_name(self, code: str) -> str:
        """Get language name from code"""
        return self.languages.get(code, code)


# Global instance
translator = TranslationService()
