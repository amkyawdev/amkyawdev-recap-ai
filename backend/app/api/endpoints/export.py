"""
Export API Endpoints
Video export with hardware encoding
"""
import os
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.storage import storage


router = APIRouter()


class ExportRequest(BaseModel):
    video_path: str = Field(..., description="Path to rendered video")
    format: str = Field(default="mp4", description="Export format: mp4, webm, mov, avi")
    quality: str = Field(default="high", description="Quality: low, medium, high, ultra")
    resolution: str = Field(default="1080p", description="Resolution: 480p, 720p, 1080p, 1440p, 4k")
    codec: str = Field(default="h264", description="Codec: h264, hevc, vp9")
    upload_to_cloud: bool = Field(default=True, description="Upload to S3/R2 after export")
    generate_thumbnail: bool = Field(default=True, description="Generate preview thumbnail")


class ExportResponse(BaseModel):
    success: bool
    export_id: str
    status: str
    local_path: Optional[str] = None
    cloud_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ExportPreset(BaseModel):
    id: str
    name: str
    format: str
    codec: str
    quality: str
    resolution: str
    description: str


# Presets
PRESETS = [
    ExportPreset(
        id="youtube_1080",
        name="YouTube 1080p",
        format="mp4",
        codec="h264",
        quality="high",
        resolution="1080p",
        description="Best for YouTube uploads"
    ),
    ExportPreset(
        id="youtube_4k",
        name="YouTube 4K",
        format="mp4",
        codec="hevc",
        quality="ultra",
        resolution="4k",
        description="Best quality for YouTube"
    ),
    ExportPreset(
        id="twitter",
        name="Twitter/X",
        format="mp4",
        codec="h264",
        quality="medium",
        resolution="720p",
        description="Optimized for Twitter/X"
    ),
    ExportPreset(
        id="instagram",
        name="Instagram",
        format="mp4",
        codec="h264",
        quality="medium",
        resolution="1080p",
        description="Instagram Reels/Stories"
    ),
    ExportPreset(
        id="tiktok",
        name="TikTok",
        format="mp4",
        codec="h264",
        quality="high",
        resolution="1080p",
        description="TikTok optimized (9:16)"
    ),
    ExportPreset(
        id="web_optimized",
        name="Web Optimized",
        format="webm",
        codec="vp9",
        quality="medium",
        resolution="720p",
        description="For web embedding"
    ),
    ExportPreset(
        id="archive",
        name="Archive",
        format="mkv",
        codec="hevc",
        quality="ultra",
        resolution="4k",
        description="Maximum quality archive"
    ),
]


@router.post("/export")
async def export_video(request: ExportRequest, background_tasks: BackgroundTasks):
    """Export video with specified settings"""
    import subprocess
    
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    
    export_id = f"export_{uuid.uuid4().hex[:12]}"
    output_dir = os.path.join(settings.OUTPUT_DIR, "exports")
    os.makedirs(output_dir, exist_ok=True)
    
    # Build output filename
    ext = request.format
    output_path = os.path.join(output_dir, f"{export_id}.{ext}")
    
    # Build FFmpeg command
    cmd = ['ffmpeg', '-i', request.video_path]
    
    # Quality settings
    quality_map = {
        "low": {"crf": 28, "bitrate": "2M"},
        "medium": {"crf": 23, "bitrate": "5M"},
        "high": {"crf": 18, "bitrate": "10M"},
        "ultra": {"crf": 15, "bitrate": "20M"},
    }
    
    # Resolution settings
    res_map = {
        "480p": "854:480",
        "720p": "1280:720",
        "1080p": "1920:1080",
        "1440p": "2560:1440",
        "4k": "3840:2160",
    }
    
    # Apply codec
    if request.codec == "h264":
        cmd.extend(['-c:v', 'libx264', '-crf', str(quality_map[request.quality]["crf"])])
    elif request.codec == "hevc":
        cmd.extend(['-c:v', 'libx265', '-crf', str(quality_map[request.quality]["crf"])])
    elif request.codec == "vp9":
        cmd.extend(['-c:v', 'libvpx-vp9', '-crf', str(quality_map[request.quality]["crf"]), '-b:v', '0'])
    
    # Apply resolution
    if request.resolution in res_map:
        cmd.extend(['-vf', f"scale={res_map[request.resolution]}"])
    
    # Audio
    if request.format == "webm":
        cmd.extend(['-c:a', 'libopus', '-b:a', '128k'])
    else:
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
    
    # Faststart for MP4 (web optimization)
    if request.format == "mp4":
        cmd.extend(['-movflags', '+faststart'])
    
    cmd.extend(['-y', output_path])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr}")
        
        response = {
            "success": True,
            "export_id": export_id,
            "status": "completed",
            "local_path": output_path,
        }
        
        # Upload to cloud
        if request.upload_to_cloud and storage.is_available:
            cloud_key = f"exports/{datetime.now().strftime('%Y/%m/%d')}/{export_id}.{ext}"
            if storage.upload_file(output_path, cloud_key, f"video/{ext}"):
                response["cloud_url"] = storage.get_presigned_url(cloud_key)
        
        # Generate thumbnail
        if request.generate_thumbnail:
            thumb_path = os.path.join(output_dir, f"{export_id}_thumb.jpg")
            thumb_cmd = [
                'ffmpeg', '-i', output_path,
                '-ss', '00:00:01',
                '-vframes', '1',
                '-q:v', '2',
                '-y', thumb_path
            ]
            subprocess.run(thumb_cmd, capture_output=True)
            
            if os.path.exists(thumb_path):
                if request.upload_to_cloud and storage.is_available:
                    thumb_key = f"thumbnails/{export_id}.jpg"
                    storage.upload_file(thumb_path, thumb_key, "image/jpeg")
                    response["thumbnail_url"] = storage.get_presigned_url(thumb_key)
                else:
                    response["thumbnail_url"] = thumb_path
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/presets")
async def list_presets():
    """List export presets"""
    return {"presets": [p.model_dump() for p in PRESETS]}


@router.get("/presets/{preset_id}")
async def get_preset(preset_id: str):
    """Get specific preset details"""
    for preset in PRESETS:
        if preset.id == preset_id:
            return preset
    raise HTTPException(status_code=404, detail="Preset not found")


@router.post("/presets/{preset_id}/apply")
async def apply_preset(preset_id: str, video_path: str):
    """Apply preset and export video"""
    preset = None
    for p in PRESETS:
        if p.id == preset_id:
            preset = p
            break
    
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    request = ExportRequest(
        video_path=video_path,
        format=preset.format,
        codec=preset.codec,
        quality=preset.quality,
        resolution=preset.resolution,
    )
    
    return await export_video(request, BackgroundTasks())
