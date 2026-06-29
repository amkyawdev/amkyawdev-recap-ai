"""
Video Edit API Endpoints
Video processing and editing operations
"""
import os
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field


router = APIRouter()


# Models
class VideoMetadata(BaseModel):
    width: int
    height: int
    duration: float
    fps: float
    codec: str
    bitrate: int
    file_size: int


class TrimRequest(BaseModel):
    video_path: str
    start_time: float
    end_time: float
    output_path: Optional[str] = None


class MergeRequest(BaseModel):
    video_paths: List[str]
    output_path: Optional[str] = None


class EffectsRequest(BaseModel):
    video_path: str
    effects: List[dict]
    output_path: Optional[str] = None


class SubtitleRequest(BaseModel):
    video_path: str
    subtitle_path: Optional[str] = None
    subtitle_text: Optional[str] = None
    style: dict = Field(default_factory=lambda: {
        "font_size": 24,
        "font_color": "white",
        "background": "black@0.5"
    })


@router.get("/info/{video_path:path}")
async def get_video_info(video_path: str):
    """Get video metadata and information"""
    import subprocess
    import json
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        # Find video stream
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video' and not video_stream:
                video_stream = stream
            elif stream['codec_type'] == 'audio' and not audio_stream:
                audio_stream = stream
        
        format_info = data.get('format', {})
        
        return {
            "success": True,
            "metadata": {
                "duration": float(format_info.get('duration', 0)),
                "size": int(format_info.get('size', 0)),
                "bitrate": int(format_info.get('bit_rate', 0)),
                "format": format_info.get('format_long_name', 'Unknown'),
            },
            "video": {
                "codec": video_stream.get('codec_name', 'Unknown') if video_stream else None,
                "width": video_stream.get('width', 0) if video_stream else 0,
                "height": video_stream.get('height', 0) if video_stream else 0,
                "fps": eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0,
            } if video_stream else None,
            "audio": {
                "codec": audio_stream.get('codec_name', 'Unknown') if audio_stream else None,
                "sample_rate": audio_stream.get('sample_rate', 0) if audio_stream else 0,
                "channels": audio_stream.get('channels', 0) if audio_stream else 0,
            } if audio_stream else None,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get video info: {str(e)}")


@router.post("/trim")
async def trim_video(request: TrimRequest):
    """Trim video to specified time range"""
    import subprocess
    
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    output = request.output_path or f"/tmp/trim_{uuid.uuid4().hex[:8]}.mp4"
    
    try:
        cmd = [
            'ffmpeg', '-i', request.video_path,
            '-ss', str(request.start_time),
            '-to', str(request.end_time),
            '-c', 'copy',
            '-y', output
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return {
            "success": True,
            "output_path": output,
            "duration": request.end_time - request.start_time
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Trim failed: {e.stderr}")


@router.post("/merge")
async def merge_videos(request: MergeRequest):
    """Merge multiple videos into one"""
    import subprocess
    
    # Check all files exist
    for path in request.video_paths:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail=f"Video not found: {path}")
    
    output = request.output_path or f"/tmp/merge_{uuid.uuid4().hex[:8]}.mp4"
    
    # Create temp file list
    list_file = f"/tmp/concat_{uuid.uuid4().hex[:8]}.txt"
    with open(list_file, 'w') as f:
        for path in request.video_paths:
            f.write(f"file '{path}'\n")
    
    try:
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            '-y', output
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return {
            "success": True,
            "output_path": output,
            "video_count": len(request.video_paths)
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {e.stderr}")
    finally:
        if os.path.exists(list_file):
            os.unlink(list_file)


@router.post("/add-subtitles")
async def add_subtitles(request: SubtitleRequest):
    """Add subtitles to video"""
    import subprocess
    
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    output = request.output_path or f"/tmp/subtitled_{uuid.uuid4().hex[:8]}.mp4"
    
    # Build subtitle filter
    style = request.style
    font_size = style.get('font_size', 24)
    font_color = style.get('font_color', 'white')
    bg = style.get('background', 'black@0.5')
    
    filter_str = f"subtitles=filename='{request.subtitle_path}':force_style='FontSize={font_size},PrimaryColour=&H{font_color}&,BackgroundColour={bg}'"
    
    if request.subtitle_text:
        # Create temp subtitle file
        subtitle_file = f"/tmp/subs_{uuid.uuid4().hex[:8]}.srt"
        with open(subtitle_file, 'w') as f:
            f.write(request.subtitle_text)
        filter_str = f"subtitles=filename='{subtitle_file}'"
    
    try:
        cmd = [
            'ffmpeg', '-i', request.video_path,
            '-vf', filter_str,
            '-c:a', 'copy',
            '-y', output
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return {
            "success": True,
            "output_path": output
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Subtitle failed: {e.stderr}")


@router.post("/effects")
async def apply_effects(request: EffectsRequest):
    """Apply video effects"""
    import subprocess
    
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    output = request.output_path or f"/tmp/effects_{uuid.uuid4().hex[:8]}.mp4"
    
    # Build filter chain
    filters = []
    for effect in request.effects:
        effect_type = effect.get('type')
        
        if effect_type == 'brightness':
            filters.append(f"eq=brightness={effect.get('value', 0)}")
        elif effect_type == 'contrast':
            filters.append(f"eq=contrast={effect.get('value', 1)}")
        elif effect_type == 'saturation':
            filters.append(f"eq=saturation={effect.get('value', 1)}")
        elif effect_type == 'blur':
            filters.append(f"boxblur={effect.get('radius', 2)}")
        elif effect_type == 'grayscale':
            filters.append("hue=s=0")
        elif effect_type == 'rotate':
            angle = effect.get('angle', 90)
            filters.append(f"rotate={angle}*PI/180")
        elif effect_type == 'speed':
            speed = effect.get('value', 1.0)
            filters.append(f"setpts={1/speed}*PTS")
    
    try:
        cmd = ['ffmpeg', '-i', request.video_path]
        
        if filters:
            cmd.extend(['-vf', ','.join(filters)])
        
        cmd.extend(['-c:a', 'copy', '-y', output])
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return {
            "success": True,
            "output_path": output,
            "effects_applied": len(effects)
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Effects failed: {e.stderr}")


@router.post("/thumbnail")
async def generate_thumbnail(video_path: str, timestamp: float = 0):
    """Generate thumbnail from video"""
    import subprocess
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    output = f"/tmp/thumb_{uuid.uuid4().hex[:8]}.jpg"
    
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-ss', str(timestamp),
            '-vframes', '1',
            '-q:v', '2',
            '-y', output
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return {
            "success": True,
            "thumbnail_path": output
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail failed: {e.stderr}")


@router.post("/watermark")
async def add_watermark(video_path: str, watermark_path: str, position: str = "右下"):
    """Add watermark to video"""
    import subprocess
    
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    if not os.path.exists(watermark_path):
        raise HTTPException(status_code=404, detail="Watermark image not found")
    
    output = f"/tmp/watermarked_{uuid.uuid4().hex[:8]}.mp4"
    
    # Position overlay
    positions = {
        "左上": "10:10",
        "右上": "W-w-10:10",
        "左下": "10:H-h-10",
        "右下": "W-w-10:H-h-10",
        "中央": "(W-w)/2:(H-h)/2",
    }
    
    pos = positions.get(position, positions["右下"])
    
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-i', watermark_path,
            '-filter_complex', f"[0:v][1:v]overlay={pos}",
            '-c:a', 'copy',
            '-y', output
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        return {
            "success": True,
            "output_path": output
        }
        
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Watermark failed: {e.stderr}")
