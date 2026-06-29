"""
Background Removal Service
GPU-accelerated background removal using RVM (Robust Video Matting)
"""
import os
import logging
from typing import Optional, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """
    GPU-accelerated background removal using RVM
    
    RVM is specifically designed for video matting and works well in real-time.
    """
    
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
        self._device = "cuda"
    
    def _load_model(self):
        """Load RVM model"""
        try:
            # RVM can be loaded via torch hub
            import torch
            
            logger.info("Loading Robust Video Matting (RVM) model...")
            
            # Load RVM model
            self._model = torch.hub.load(
                'PeterL1n/RobustVideoMatting',
                'resnet50',
                pretrained=True
            )
            
            self._model = self._model.to(f"{self._device}:0").eval()
            logger.info("RVM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load RVM model: {e}")
            raise
    
    @property
    def model(self):
        """Lazy load model"""
        if self._model is None:
            self._load_model()
        return self._model
    
    def remove_background(
        self,
        video_path: str,
        output_path: str,
        background_color: Tuple[int, int, int] = (0, 0, 0),
        background_image: Optional[str] = None,
        segmentation_threshold: float = 0.5,
    ) -> str:
        """
        Remove background from video
        
        Args:
            video_path: Path to input video
            output_path: Path to output video
            background_color: RGB tuple for solid color background
            background_image: Path to background image
            segmentation_threshold: Alpha threshold (0-1)
            
        Returns:
            Path to output video
        """
        from app.core.gpu_manager import gpu_manager
        import torch
        import cv2
        from torchvision.transforms import ToTensor, ToPILImage
        from model.RVM.inference import VideoMatting
        
        # Acquire GPU
        device_id = gpu_manager.acquire_device()
        
        try:
            # Initialize video capture
            cap = cv2.VideoCapture(video_path)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Load RVM model
            model = self.model.to(f"{self._device}:{device_id}")
            
            # Background preparation
            if background_image:
                bg_img = cv2.imread(background_image)
                bg_tensor = ToTensor()(bg_img).unsqueeze(0).to(f"{self._device}:{device_id}")
            else:
                bg_tensor = torch.tensor(background_color).view(1, 3, 1, 1).float()
                bg_tensor = bg_tensor.to(f"{self._device}:{device_id}")
            
            # Process video
            frame_count = 0
            rec = [None] * 4  # RVM recurrent states
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Preprocess
                src = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                src_tensor = ToTensor()(src).unsqueeze(0).to(f"{self._device}:{device_id}")
                
                # Inference
                with torch.no_grad():
                    fgr, pha, *rec = model(src_tensor, *rec)
                
                # Composite
                fgr = fgr.cpu().numpy()[0].transpose(1, 2, 0)
                pha = pha.cpu().numpy()[0, 0]
                
                # Apply threshold
                alpha = (pha > segmentation_threshold).astype(np.float32)
                
                # Create output frame
                if background_image:
                    bg = cv2.resize(bg_img, (width, height))
                else:
                    bg = background_color
                
                fgr_rgb = (fgr * 255).clip(0, 255).astype(np.uint8)
                output_frame = (fgr_rgb * alpha[:, :, np.newaxis] + 
                              np.array(bg) * (1 - alpha[:, :, np.newaxis])).astype(np.uint8)
                
                out.write(output_frame)
                
                frame_count += 1
                if frame_count % 30 == 0:
                    progress = frame_count / total_frames
                    logger.info(f"Processing: {progress:.1%}")
            
            cap.release()
            out.release()
            
            logger.info(f"Background removal complete: {output_path}")
            return output_path
            
        finally:
            gpu_manager.release_device(device_id)
    
    def remove_background_single_image(
        self,
        image_path: str,
        output_path: str,
        background_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> str:
        """Remove background from single image"""
        import cv2
        from PIL import Image
        from torchvision.transforms import ToTensor
        
        # Load image
        img = Image.open(image_path)
        img_tensor = ToTensor()(img).unsqueeze(0)
        
        # Process with model (simplified for single image)
        # In production, use RMBG-1.4 or similar model for images
        
        # For now, return original (placeholder)
        img.save(output_path)
        return output_path


# Global instance
bg_removal = BackgroundRemovalService()
