"""
Render API Endpoints
GPU-accelerated video rendering
"""
import os
import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.gpu_manager import gpu_manager


router = APIRouter()


# Render Job Models
class RenderJob(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: float = 0.0
    created_at: datetime
    completed_at: Optional[datetime] = None
    input_path: str
    output_path: Optional[str] = None
    settings: dict = {}
    error: Optional[str] = None


class RenderRequest(BaseModel):
    input_path: str = Field(..., description="Input video file path")
    output_path: Optional[str] = None
    codec: str = Field(default="h264_nvenc", description="Video codec")
    quality: str = Field(default="high", description="Quality preset: low, medium, high, ultra")
    resolution: str = Field(default="1080p", description="Output resolution")
    fps: Optional[float] = None
    bitrate: Optional[str] = None
    gpu_device: Optional[int] = None


class RenderResponse(BaseModel):
    success: bool
    job_id: str
    status: str
    output_path: Optional[str] = None


# Quality presets
QUALITY_PRESETS = {
    "low": {"crf": 28, "bitrate": "2M"},
    "medium": {"crf": 23, "bitrate": "5M"},
    "high": {"crf": 18, "bitrate": "10M"},
    "ultra": {"crf": 15, "bitrate": "20M"},
}

# Resolution presets
RESOLUTION_PRESETS = {
    "480p": {"width": 854, "height": 480},
    "720p": {"width": 1280, "height": 720},
    "1080p": {"width": 1920, "height": 1080},
    "1440p": {"width": 2560, "height": 1440},
    "4k": {"width": 3840, "height": 2160},
}

# In-memory job storage (use Redis in production)
_render_jobs = {}


@router.get("/status")
async def get_gpu_status():
    """Get GPU rendering status"""
    return gpu_manager.get_status()


@router.get("/jobs")
async def list_render_jobs():
    """List all render jobs"""
    jobs = []
    for job_id, job in _render_jobs.items():
        jobs.append({
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "input_path": job.input_path,
            "output_path": job.output_path,
            "error": job.error,
        })
    return {"jobs": jobs, "total": len(jobs)}


@router.get("/jobs/{job_id}")
async def get_render_job(job_id: str):
    """Get specific render job status"""
    if job_id not in _render_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = _render_jobs[job_id]
    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "input_path": job.input_path,
        "output_path": job.output_path,
        "error": job.error,
    }


@router.post("/submit")
async def submit_render_job(request: RenderRequest, background_tasks: BackgroundTasks):
    """Submit a new render job"""
    if not os.path.exists(request.input_path):
        raise HTTPException(status_code=404, detail="Input video not found")
    
    job_id = f"render_{uuid.uuid4().hex[:12]}"
    output = request.output_path or os.path.join(
        settings.OUTPUT_DIR, f"{job_id}.mp4"
    )
    
    # Create job
    job = RenderJob(
        job_id=job_id,
        status="queued",
        progress=0.0,
        created_at=datetime.now(),
        input_path=request.input_path,
        output_path=output,
        settings={
            "codec": request.codec,
            "quality": request.quality,
            "resolution": request.resolution,
            "fps": request.fps,
            "bitrate": request.bitrate,
            "gpu_device": request.gpu_device,
        }
    )
    
    _render_jobs[job_id] = job
    
    # Queue for background processing
    background_tasks.add_task(
        process_render_job,
        job_id,
        request.input_path,
        output,
        request.codec,
        request.quality,
        request.resolution,
        request.fps,
        request.bitrate,
        request.gpu_device
    )
    
    return RenderResponse(
        success=True,
        job_id=job_id,
        status="queued",
        output_path=output
    )


async def process_render_job(
    job_id: str,
    input_path: str,
    output_path: str,
    codec: str,
    quality: str,
    resolution: str,
    fps: float | None,
    bitrate: str | None,
    gpu_device: int | None
):
    """Background task to process render job"""
    import subprocess
    
    job = _render_jobs.get(job_id)
    if not job:
        return
    
    job.status = "processing"
    
    try:
        # Acquire GPU
        if gpu_device is None:
            gpu_device = gpu_manager.acquire_device()
        else:
            gpu_manager.acquire_device(gpu_device)
        
        # Build FFmpeg command
        preset = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["high"])
        res = RESOLUTION_PRESETS.get(resolution, RESOLUTION_PRESETS["1080p"])
        
        cmd = ['ffmpeg', '-i', input_path]
        
        # Video filter for resolution
        vf_filters = [f"scale={res['width']}:{res['height']}:force_original_aspect_ratio=decrease"]
        
        # Codec specific settings
        if codec == "h264_nvenc":
            cmd.extend([
                '-c:v', 'h264_nvenc',
                '-preset', 'p4',  # Medium quality
                '-tune', 'hq',
                '-rc', 'vbr',
                '-cq', str(preset['crf']),
            ])
        elif codec == "hevc_nvenc":
            cmd.extend([
                '-c:v', 'hevc_nvenc',
                '-preset', 'p4',
                '-tune', 'hq',
                '-rc', 'vbr',
                '-cq', str(preset['crf']),
            ])
        elif codec == "h264_amf":
            cmd.extend(['-c:v', 'h264_amf', '-quality', 'balanced'])
        elif codec == "h264_qsv":
            cmd.extend(['-c:v', 'h264_qsv', '-preset', 'medium', '-global_quality', str(preset['crf'])])
        else:
            # Software encoding
            cmd.extend(['-c:v', 'libx264', '-crf', str(preset['crf']), '-preset', 'medium'])
        
        # Apply filters
        cmd.extend(['-vf', ','.join(vf_filters)])
        
        # FPS
        if fps:
            cmd.extend(['-r', str(fps)])
        
        # Audio
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
        
        # Output
        cmd.extend(['-y', output_path])
        
        # Update progress
        job.progress = 0.1
        
        # Run FFmpeg
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor progress
        while True:
            line = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            
            # Parse time for progress
            if 'time=' in line:
                # Extract time=XX:XX:XX
                import re
                match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    job.progress = min(0.9, current_time / 300)  # Estimate based on 5 min
        
        if process.returncode == 0:
            job.status = "completed"
            job.progress = 1.0
            job.completed_at = datetime.now()
        else:
            raise Exception("FFmpeg process failed")
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
    finally:
        gpu_manager.release_device(gpu_device or 0)


@router.delete("/jobs/{job_id}")
async def cancel_render_job(job_id: str):
    """Cancel a render job"""
    if job_id not in _render_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = _render_jobs[job_id]
    
    if job.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    job.status = "failed"
    job.error = "Cancelled by user"
    
    return {"success": True, "message": "Job cancelled"}


@router.get("/codecs")
async def list_codecs():
    """List available video codecs"""
    status = gpu_manager.get_status()
    has_nvidia = any('NVIDIA' in d.get('name', '') for d in status.get('devices', []))
    
    codecs = [
        {"id": "h264_nvenc", "name": "H.264 (NVENC)", "vendor": "NVIDIA", "gpu": True, "available": has_nvidia},
        {"id": "hevc_nvenc", "name": "H.265/HEVC (NVENC)", "vendor": "NVIDIA", "gpu": True, "available": has_nvidia},
        {"id": "h264_amf", "name": "H.264 (AMF)", "vendor": "AMD", "gpu": True, "available": False},
        {"id": "h264_qsv", "name": "H.264 (QuickSync)", "vendor": "Intel", "gpu": True, "available": False},
        {"id": "libx264", "name": "H.264 (Software)", "vendor": "CPU", "gpu": False, "available": True},
        {"id": "libx265", "name": "H.265/HEVC (Software)", "vendor": "CPU", "gpu": False, "available": True},
        {"id": "libvpx-vp9", "name": "VP9 (Software)", "vendor": "CPU", "gpu": False, "available": True},
    ]
    
    return {"codecs": codecs, "gpu_available": gpu_manager.is_available}
