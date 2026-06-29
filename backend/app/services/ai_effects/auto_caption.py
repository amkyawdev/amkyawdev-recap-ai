"""
Auto Caption Service
Whisper + burn-in captions generation
"""
import os
import re
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CaptionStyle:
    """Caption styling options"""
    font_family: str = "Arial"
    font_size: int = 24
    font_color: str = "#FFFFFF"
    background_color: str = "#00000080"
    stroke_color: str = "#000000"
    stroke_width: int = 1
    position: str = "bottom"  # bottom, top, center
    alignment: str = "center"  # left, center, right
    max_chars_per_line: int = 42
    margin_percent: float = 0.05


@dataclass
class CaptionSegment:
    """Single caption segment"""
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None


class AutoCaptionService:
    """
    Automatic caption generation from video
    
    Uses Whisper for transcription and generates SRT/VTT files
    with optional burn-in to video.
    """
    
    def __init__(self):
        self.default_style = CaptionStyle()
    
    def generate_captions(
        self,
        video_path: str,
        output_path: str,
        format: str = "srt",
        language: Optional[str] = None,
        style: Optional[CaptionStyle] = None,
        burn_to_video: bool = False,
    ) -> str:
        """
        Generate captions from video
        
        Args:
            video_path: Path to video file
            output_path: Path for output caption/video
            format: Caption format (srt, vtt, ass)
            language: Language code or None for auto-detect
            style: Caption styling options
            burn_to_video: Whether to burn captions into video
            
        Returns:
            Path to output file (caption or video with captions)
        """
        from app.services.whisper.transcriber import whisper_service
        
        style = style or self.default_style
        
        # Transcribe video
        logger.info(f"Transcribing video: {video_path}")
        result = whisper_service.transcribe_video(video_path, language=language)
        
        # Convert to caption segments
        segments = self._create_segments(result.segments)
        
        # Generate caption file
        if format == "srt":
            caption_content = self._generate_srt(segments)
        elif format == "vtt":
            caption_content = self._generate_vtt(segments)
        elif format == "ass":
            caption_content = self._generate_ass(segments, style)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Save caption file
        caption_path = output_path.rsplit('.', 1)[0] + f'.{format}'
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(caption_content)
        
        logger.info(f"Captions saved: {caption_path}")
        
        if burn_to_video:
            # Burn captions into video
            video_with_captions = self._burn_captions(video_path, caption_path, output_path, style)
            return video_with_captions
        
        return caption_path
    
    def _create_segments(self, whisper_segments: List[Dict]) -> List[CaptionSegment]:
        """Convert Whisper segments to CaptionSegment list"""
        segments = []
        
        for seg in whisper_segments:
            text = seg.get('text', '').strip()
            if text:
                segments.append(CaptionSegment(
                    start_time=seg.get('start', 0),
                    end_time=seg.get('end', 0),
                    text=text,
                    speaker=seg.get('speaker'),
                ))
        
        return segments
    
    def _time_to_srt(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _time_to_vtt(self, seconds: float) -> str:
        """Convert seconds to VTT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def _generate_srt(self, segments: List[CaptionSegment]) -> str:
        """Generate SRT format captions"""
        lines = []
        
        for i, seg in enumerate(segments, 1):
            lines.append(str(i))
            lines.append(f"{self._time_to_srt(seg.start_time)} --> {self._time_to_srt(seg.end_time)}")
            lines.append(seg.text)
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_vtt(self, segments: List[CaptionSegment]) -> str:
        """Generate WebVTT format captions"""
        lines = ["WEBVTT", ""]
        
        for i, seg in enumerate(segments, 1):
            lines.append(f"{i}")
            lines.append(f"{self._time_to_vtt(seg.start_time)} --> {self._time_to_vtt(seg.end_time)}")
            lines.append(seg.text)
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_ass(self, segments: List[CaptionSegment], style: CaptionStyle) -> str:
        """Generate ASS/SSA format captions (for styling)"""
        lines = [
            "[Script Info]",
            "Title: Generated Captions",
            "ScriptType: v4.00+",
            "PlayDepth: 0",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,{style.font_family},{style.font_size},{style.font_color},{style.font_color},{style.stroke_color},,0,0,0,0,100,100,0,0,1,{style.stroke_width},0,2,10,10,10,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
        
        for seg in segments:
            start = self._seconds_to_ass_time(seg.start_time)
            end = self._seconds_to_ass_time(seg.end_time)
            text = seg.text.replace("\n", "\\N")
            lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
        
        return "\n".join(lines)
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def _burn_captions(
        self,
        video_path: str,
        caption_path: str,
        output_path: str,
        style: CaptionStyle,
    ) -> str:
        """Burn captions into video using FFmpeg"""
        import subprocess
        
        # Build FFmpeg filter for subtitles
        if caption_path.endswith('.srt'):
            subtitle_option = f"subtitles='{caption_path}'"
        elif caption_path.endswith('.ass'):
            subtitle_option = f"ass='{caption_path}'"
        else:
            subtitle_option = f"subtitles='{caption_path}'"
        
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', subtitle_option,
            '-c:a', 'copy',
            '-y', output_path
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"Captions burned to video: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise Exception(f"Failed to burn captions: {e.stderr}")
    
    def translate_captions(
        self,
        caption_path: str,
        output_path: str,
        target_language: str,
        source_language: str = "auto",
    ) -> str:
        """Translate existing caption file"""
        from app.services.translate.translator import translator
        
        # Read original captions
        with open(caption_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detect format
        if caption_path.endswith('.srt'):
            format = 'srt'
        elif caption_path.endswith('.vtt'):
            format = 'vtt'
        else:
            format = 'srt'
        
        # Translate
        translated = translator.translate_subtitles(
            content,
            target_language=target_language,
            source_language=source_language,
            format=format,
        )
        
        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        
        return output_path
    
    def get_style_presets(self) -> Dict[str, CaptionStyle]:
        """Get predefined caption style presets"""
        return {
            "default": CaptionStyle(
                font_size=24,
                font_color="#FFFFFF",
                background_color="#00000080",
            ),
            "large": CaptionStyle(
                font_size=36,
                font_color="#FFFFFF",
                background_color="#00000099",
            ),
            "minimal": CaptionStyle(
                font_size=20,
                font_color="#FFFFFF",
                background_color="#00000060",
            ),
            "social": CaptionStyle(
                font_size=28,
                font_color="#FFFFFF",
                background_color="#000000CC",
                max_chars_per_line=35,
            ),
            "accessibility": CaptionStyle(
                font_size=32,
                font_color="#FFFF00",
                background_color="#000000CC",
            ),
        }


# Global instance
auto_caption = AutoCaptionService()
