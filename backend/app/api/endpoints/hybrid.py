"""
Hybrid Rendering Decision API
On-device vs Cloud rendering decision logic
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.gpu_manager import gpu_manager


router = APIRouter()


class RenderDecisionRequest(BaseModel):
    video_size_mb: float = Field(..., description="Video file size in MB")
    video_duration_seconds: float = Field(..., description="Video duration in seconds")
    video_resolution: str = Field(default="1080p", description="Video resolution")
    effects: list = Field(default_factory=list, description="List of effects to apply")
    output_quality: str = Field(default="high", description="Output quality")
    user_preference: Optional[str] = Field(default=None, description="User preference: on_device, cloud, auto")
    client_device: str = Field(default="desktop", description="Client device type")
    client_gpu_available: bool = Field(default=False, description="Client GPU availability")


class RenderDecision(BaseModel):
    decision: str  # on_device, cloud, hybrid
    recommended_location: str
    estimated_time_seconds: dict
    estimated_cost: dict
    reasoning: list[str]
    gpu_utilization: float
    network_estimate_mbps: float


# Rendering complexity weights
EFFECT_COMPLEXITY = {
    "trim": 1,
    "crop": 2,
    "watermark": 2,
    "subtitles": 3,
    "color_correction": 4,
    "filters": 4,
    "blur": 5,
    "transition": 3,
    "speed_change": 2,
    "background_removal": 15,
    "style_transfer": 20,
    "super_resolution": 25,
    "auto_caption": 10,
}

# Processing time estimates (seconds per effect complexity unit)
TIME_PER_UNIT_CLOUD = 0.5  # Faster cloud processing
TIME_PER_UNIT_ON_DEVICE = 3.0  # Slower on-device


def estimate_processing_complexity(
    video_size_mb: float,
    duration_seconds: float,
    resolution: str,
    effects: list
) -> float:
    """Calculate processing complexity score"""
    
    # Base complexity from size and duration
    base_score = (video_size_mb / 100) + (duration_seconds / 60)
    
    # Resolution multiplier
    res_multiplier = {
        "480p": 0.5,
        "720p": 1.0,
        "1080p": 2.0,
        "1440p": 4.0,
        "4k": 8.0,
    }.get(resolution, 1.0)
    
    complexity = base_score * res_multiplier
    
    # Add effect complexity
    for effect in effects:
        effect_type = effect.get('type', '')
        complexity += EFFECT_COMPLEXITY.get(effect_type, 3)
    
    return complexity


def estimate_cloud_bandwidth(video_size_mb: float) -> float:
    """Estimate required bandwidth for cloud upload (Mbps)"""
    # Assuming video needs to be uploaded for cloud processing
    upload_time_estimate = 30  # seconds
    video_bits = video_size_mb * 8 * 1024 * 1024
    return (video_bits / upload_time_estimate) / (1024 * 1024)


@router.post("/decide")
async def make_render_decision(request: RenderDecisionRequest):
    """
    Make intelligent rendering decision between on-device and cloud
    
    Considers:
    - Video complexity (size, duration, resolution)
    - Effects complexity
    - Client device capabilities
    - Network conditions
    - User preferences
    """
    
    gpu_status = gpu_manager.get_status()
    gpu_available = gpu_status.get('available', False)
    gpu_count = gpu_status.get('device_count', 0)
    
    # Calculate complexity
    complexity = estimate_processing_complexity(
        video_size_mb=request.video_size_mb,
        duration_seconds=request.video_duration_seconds,
        resolution=request.video_resolution,
        effects=request.effects
    )
    
    # Estimate cloud bandwidth
    cloud_bandwidth = estimate_cloud_bandwidth(request.video_size_mb)
    
    # Decision logic
    reasoning = []
    recommended = "auto"
    
    # Check user preference override
    if request.user_preference == "on_device":
        recommended = "on_device"
        reasoning.append("User preference: on-device rendering")
    elif request.user_preference == "cloud":
        recommended = "cloud"
        reasoning.append("User preference: cloud rendering")
    
    # Complexity-based decision
    if complexity > 50:
        if not gpu_available:
            recommended = "cloud"
            reasoning.append(f"High complexity ({complexity:.1f}) requires cloud GPU")
        elif request.client_device in ["mobile", "tablet"]:
            recommended = "cloud"
            reasoning.append("Mobile/tablet cannot handle high complexity")
        else:
            reasoning.append(f"High complexity ({complexity:.1f}) - recommend cloud for best performance")
    
    elif complexity < 10:
        recommended = "on_device"
        reasoning.append(f"Low complexity ({complexity:.1f}) - on-device is faster")
    
    # GPU availability
    if request.client_gpu_available and gpu_available:
        if recommended == "cloud":
            reasoning.append("Client has GPU - could use hybrid approach")
    
    # Network check
    if cloud_bandwidth > 50:
        reasoning.append(f"High bandwidth needed ({cloud_bandwidth:.1f} Mbps) - consider on-device")
    
    # Generate time estimates
    time_estimates = {}
    
    if gpu_available or request.client_gpu_available:
        time_estimates["on_device"] = complexity * TIME_PER_UNIT_ON_DEVICE
    else:
        time_estimates["on_device"] = complexity * TIME_PER_UNIT_ON_DEVICE * 3  # CPU fallback
    
    time_estimates["cloud"] = complexity * TIME_PER_UNIT_CLOUD
    time_estimates["difference"] = time_estimates["on_device"] - time_estimates["cloud"]
    
    # Cost estimates
    cost_estimates = {
        "on_device": {
            "electricity_usd": 0.001 * time_estimates["on_device"],  # ~1 cent per hour
            "wear_tear_usd": 0.01 * time_estimates["on_device"] / 3600
        },
        "cloud": {
            "compute_usd": 0.0005 * time_estimates["cloud"],  # GPU instance ~$1.8/hr
        }
    }
    
    # Calculate GPU utilization
    gpu_util = 0.0
    if gpu_available and gpu_count > 0:
        for device in gpu_status.get('devices', []):
            gpu_util = max(gpu_util, device.get('utilization_percent', 0))
    
    return RenderDecision(
        decision="auto" if recommended == "auto" else "user",
        recommended_location=recommended,
        estimated_time_seconds=time_estimates,
        estimated_cost=cost_estimates,
        reasoning=reasoning,
        gpu_utilization=gpu_util,
        network_estimate_mbps=cloud_bandwidth
    )


@router.get("/compare")
async def compare_render_options(
    video_size_mb: float = 100,
    duration_seconds: float = 300,
    resolution: str = "1080p",
    effects_count: int = 0
):
    """Compare rendering options side by side"""
    
    complexity = estimate_processing_complexity(
        video_size_mb=video_size_mb,
        duration_seconds=duration_seconds,
        resolution=resolution,
        effects=[{"type": "generic"}] * effects_count
    )
    
    cloud_bandwidth = estimate_cloud_bandwidth(video_size_mb)
    
    return {
        "input": {
            "size_mb": video_size_mb,
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "effects_count": effects_count
        },
        "complexity_score": complexity,
        "options": {
            "on_device": {
                "pros": [
                    "No upload time",
                    "Privacy (data stays local)",
                    "No internet required",
                    "No cloud costs"
                ],
                "cons": [
                    "Slower on CPU",
                    "Battery drain on mobile",
                    "Limited GPU memory"
                ],
                "estimated_time": complexity * TIME_PER_UNIT_ON_DEVICE,
                "estimated_cost_usd": 0
            },
            "cloud": {
                "pros": [
                    "Fast GPU processing",
                    "No local resource usage",
                    "Handles complex effects",
                    "Scalable power"
                ],
                "cons": [
                    "Upload time",
                    "Internet required",
                    "Privacy concerns",
                    "Cloud compute costs"
                ],
                "estimated_time": complexity * TIME_PER_UNIT_CLOUD,
                "estimated_cost_usd": 0.0005 * complexity * TIME_PER_UNIT_CLOUD
            }
        },
        "network_bandwidth_mbps": cloud_bandwidth,
        "recommendation": "cloud" if complexity > 30 else "on_device"
    }


@router.get("/capabilities")
async def get_render_capabilities():
    """Get current rendering capabilities"""
    gpu_status = gpu_manager.get_status()
    
    return {
        "cloud": {
            "gpu_available": gpu_status.get('available', False),
            "gpu_count": gpu_status.get('device_count', 0),
            "gpus": gpu_status.get('devices', []),
            "storage_available": True,  # Would check S3 status
        },
        "on_device": {
            "estimated_cpu_cores": os.cpu_count() if hasattr(os, 'cpu_count') else 4,
            "estimated_ram_gb": 16,  # Would get actual
            "gpu_available": gpu_status.get('available', False),
        }
    }


@router.get("/estimate")
async def estimate_render_time(
    video_duration_seconds: float,
    resolution: str,
    quality: str,
    render_location: str = "auto"
):
    """Estimate render time for specific settings"""
    
    complexity = estimate_processing_complexity(
        video_size_mb=video_duration_seconds * 0.5,  # Rough estimate
        duration_seconds=video_duration_seconds,
        resolution=resolution,
        effects=[]
    )
    
    # Adjust for quality
    quality_multiplier = {
        "low": 0.5,
        "medium": 1.0,
        "high": 1.5,
        "ultra": 2.5
    }.get(quality, 1.0)
    
    return {
        "estimated_seconds": {
            "on_device_cpu": complexity * TIME_PER_UNIT_ON_DEVICE * 3 * quality_multiplier,
            "on_device_gpu": complexity * TIME_PER_UNIT_ON_DEVICE * quality_multiplier,
            "cloud_gpu": complexity * TIME_PER_UNIT_CLOUD * quality_multiplier,
        },
        "estimated_minutes": {
            key: round(val / 60, 1)
            for key, val in {
                "on_device_cpu": complexity * TIME_PER_UNIT_ON_DEVICE * 3 * quality_multiplier,
                "on_device_gpu": complexity * TIME_PER_UNIT_ON_DEVICE * quality_multiplier,
                "cloud_gpu": complexity * TIME_PER_UNIT_CLOUD * quality_multiplier,
            }.items()
        }
    }
