"""
Celery Render Worker
Background rendering tasks
"""
import os
import logging
from celery import Task
from celery_worker import celery_app
from app.core.gpu_manager import gpu_manager

logger = logging.getLogger(__name__)


class RenderTask(Task):
    """Base class for render tasks with GPU management"""
    
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Cleanup after task completion"""
        if hasattr(self, '_device_id'):
            gpu_manager.release_device(self._device_id)
    
    def before_start(self, task_id, args, kwargs):
        """Acquire GPU before starting"""
        self._device_id = gpu_manager.acquire_device()


@celery_app.task(
    bind=True,
    base=RenderTask,
    name="render_video",
    max_retries=3,
    default_retry_delay=60,
)
def render_video(
    self,
    input_path: str,
    output_path: str,
    settings: dict
):
    """
    Render video with specified settings
    
    Args:
        input_path: Input video file path
        output_path: Output video file path
        settings: Render settings (codec, quality, resolution, etc.)
    """
    import subprocess
    
    logger.info(f"Starting render: {input_path} -> {output_path}")
    
    # Get settings
    codec = settings.get('codec', 'libx264')
    quality = settings.get('quality', 'high')
    resolution = settings.get('resolution', '1080p')
    
    # Quality presets
    crf_values = {
        'low': '28',
        'medium': '23',
        'high': '18',
        'ultra': '15'
    }
    crf = crf_values.get(quality, '23')
    
    # Resolution
    res_map = {
        '480p': '854:480',
        '720p': '1280:720',
        '1080p': '1920:1080',
        '1440p': '2560:1440',
        '4k': '3840:2160'
    }
    scale = res_map.get(resolution, res_map['1080p'])
    
    # Build command
    cmd = ['ffmpeg', '-i', input_path]
    
    if codec == 'h264_nvenc':
        cmd.extend(['-c:v', 'h264_nvenc', '-preset', 'p4', '-tune', 'hq'])
    elif codec == 'hevc_nvenc':
        cmd.extend(['-c:v', 'hevc_nvenc', '-preset', 'p4'])
    elif codec == 'h264_qsv':
        cmd.extend(['-c:v', 'h264_qsv'])
    elif codec == 'h264_amf':
        cmd.extend(['-c:v', 'h264_amf'])
    else:
        cmd.extend(['-c:v', 'libx264', '-crf', crf, '-preset', 'medium'])
    
    cmd.extend(['-vf', f'scale={scale}:force_original_aspect_ratio=decrease'])
    cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
    cmd.extend(['-y', output_path])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hours
        )
        
        if result.returncode == 0:
            logger.info(f"Render complete: {output_path}")
            return {
                'success': True,
                'output_path': output_path,
                'device_id': self._device_id
            }
        else:
            raise Exception(result.stderr)
            
    except subprocess.TimeoutExpired:
        raise Exception("Render timed out after 2 hours")
    except Exception as e:
        logger.error(f"Render failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=RenderTask,
    name="apply_effects",
    max_retries=2,
)
def apply_effects(
    self,
    input_path: str,
    output_path: str,
    effects: list
):
    """
    Apply AI effects to video
    
    Args:
        input_path: Input video path
        output_path: Output video path
        effects: List of effect dictionaries
    """
    import subprocess
    
    logger.info(f"Applying {len(effects)} effects to {input_path}")
    
    filters = []
    
    for effect in effects:
        effect_type = effect.get('type')
        value = effect.get('value', 1.0)
        
        if effect_type == 'brightness':
            filters.append(f"eq=brightness={value}")
        elif effect_type == 'contrast':
            filters.append(f"eq=contrast={value}")
        elif effect_type == 'saturation':
            filters.append(f"eq=saturation={value}")
        elif effect_type == 'blur':
            filters.append(f"boxblur={value}")
        elif effect_type == 'grayscale':
            filters.append("hue=s=0")
        elif effect_type == 'sepia':
            filters.append("colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131")
        elif effect_type == 'invert':
            filters.append("negate")
        elif effect_type == 'sharpen':
            filters.append(f"unsharp=5:5:{value}:5:5:{value}")
    
    if not filters:
        raise ValueError("No valid effects provided")
    
    cmd = [
        'ffmpeg', '-i', input_path,
        '-vf', ','.join(filters),
        '-c:a', 'copy',
        '-y', output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {'success': True, 'output_path': output_path}
        else:
            raise Exception(result.stderr)
            
    except Exception as e:
        logger.error(f"Effects failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    base=RenderTask,
    name="transcribe_video",
    max_retries=3,
    default_retry_delay=30,
)
def transcribe_video_task(
    self,
    video_path: str,
    output_path: str = None,
    language: str = None,
    model_size: str = "base"
):
    """
    Transcribe video to text
    
    Args:
        video_path: Path to video file
        output_path: Optional path to save transcript
        language: Language code or None for auto
        model_size: Whisper model size
    """
    from app.services.whisper.transcriber import whisper_service
    
    logger.info(f"Transcribing: {video_path}")
    
    try:
        result = whisper_service.transcribe_video(
            video_path,
            language=language
        )
        
        transcript = {
            'text': result.text,
            'language': result.language,
            'duration': result.duration,
            'segments': result.segments,
        }
        
        if output_path:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'transcript': transcript,
            'output_path': output_path
        }
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    bind=True,
    name="cleanup_render_files",
    max_retries=1,
)
def cleanup_render_files(self, file_paths: list):
    """Cleanup temporary render files"""
    import glob
    
    cleaned = 0
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.unlink(path)
                cleaned += 1
            else:
                # Try glob pattern
                for p in glob.glob(path):
                    os.unlink(p)
                    cleaned += 1
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")
    
    return {'cleaned': cleaned}
