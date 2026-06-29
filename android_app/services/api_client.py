"""
API Client for Android App
Handles all HTTP communication with backend
"""
import os
import json
import logging
from typing import Optional, Dict, List, Any
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API Error"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class APIClient:
    """
    HTTP API Client
    
    Handles all communication with the backend API.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Backend API URL (defaults to localhost for development)
        """
        self.base_url = base_url or os.environ.get('API_URL', 'http://localhost:8000/api/v1')
        self.timeout = 30
        self._session_token = None
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """
        Make HTTP request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            files: Files to upload
            headers: Additional headers
            
        Returns:
            Response JSON
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        headers = headers or {}
        if self._session_token:
            headers['Authorization'] = f"Bearer {self._session_token}"
        
        headers['Content-Type'] = 'application/json'
        
        try:
            if method in ('GET', 'DELETE'):
                if data:
                    url = f"{url}?{urlencode(data)}"
                body = None
            else:
                body = json.dumps(data).encode('utf-8') if data else None
            
            request = Request(url, data=body, headers=headers, method=method)
            
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
                
        except HTTPError as e:
            try:
                error_body = json.loads(e.read().decode('utf-8'))
                message = error_body.get('detail', error_body.get('error', str(e)))
            except:
                message = str(e)
            raise APIError(message, e.code)
            
        except URLError as e:
            raise APIError(f"Network error: {e.reason}")
    
    def set_token(self, token: str):
        """Set session token"""
        self._session_token = token
    
    # ==================== GPU Status ====================
    
    def get_gpu_status(self) -> Dict:
        """Get GPU rendering status"""
        return self._make_request('GET', '/render/status')
    
    def get_codecs(self) -> Dict:
        """Get available video codecs"""
        return self._make_request('GET', '/render/codecs')
    
    # ==================== Recap ====================
    
    def generate_recap(
        self,
        transcript: str,
        duration_minutes: float = 5,
        style: str = 'engaging',
        target_audience: str = 'general',
    ) -> Dict:
        """
        Generate AI recap script
        
        Args:
            transcript: Video transcript text
            duration_minutes: Target duration
            style: Script style
            target_audience: Target audience
            
        Returns:
            Generated script and metadata
        """
        return self._make_request('POST', '/recap/generate', {
            'transcript': transcript,
            'duration_minutes': duration_minutes,
            'style': style,
            'target_audience': target_audience,
        })
    
    def transcribe_video(self, video_path: str, language: str = 'auto') -> Dict:
        """
        Transcribe video to text
        
        Args:
            video_path: Path to video file
            language: Language code
            
        Returns:
            Transcription result
        """
        return self._make_request('POST', '/recap/transcribe', {
            'video_url': video_path,
            'language': language,
        })
    
    def get_models(self) -> Dict:
        """Get available AI models"""
        return self._make_request('GET', '/recap/models')
    
    def get_styles(self) -> Dict:
        """Get available script styles"""
        return self._make_request('GET', '/recap/styles')
    
    # ==================== Video Edit ====================
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get video metadata"""
        return self._make_request('GET', f'/video/info/{video_path}')
    
    def trim_video(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
    ) -> Dict:
        """Trim video"""
        return self._make_request('POST', '/video/trim', {
            'video_path': video_path,
            'start_time': start_time,
            'end_time': end_time,
        })
    
    def merge_videos(self, video_paths: List[str]) -> Dict:
        """Merge multiple videos"""
        return self._make_request('POST', '/video/merge', {
            'video_paths': video_paths,
        })
    
    def apply_effects(self, video_path: str, effects: List[Dict]) -> Dict:
        """Apply effects to video"""
        return self._make_request('POST', '/video/effects', {
            'video_path': video_path,
            'effects': effects,
        })
    
    # ==================== Render ====================
    
    def submit_render_job(
        self,
        input_path: str,
        codec: str = 'h264_nvenc',
        quality: str = 'high',
        resolution: str = '1080p',
    ) -> Dict:
        """Submit render job"""
        return self._make_request('POST', '/render/submit', {
            'input_path': input_path,
            'codec': codec,
            'quality': quality,
            'resolution': resolution,
        })
    
    def get_render_job(self, job_id: str) -> Dict:
        """Get render job status"""
        return self._make_request('GET', f'/render/jobs/{job_id}')
    
    def list_render_jobs(self) -> Dict:
        """List all render jobs"""
        return self._make_request('GET', '/render/jobs')
    
    def cancel_render_job(self, job_id: str) -> Dict:
        """Cancel render job"""
        return self._make_request('DELETE', f'/render/jobs/{job_id}')
    
    # ==================== Export ====================
    
    def export_video(
        self,
        video_path: str,
        format: str = 'mp4',
        quality: str = 'high',
        resolution: str = '1080p',
        upload_to_cloud: bool = True,
    ) -> Dict:
        """Export video"""
        return self._make_request('POST', '/export/export', {
            'video_path': video_path,
            'format': format,
            'quality': quality,
            'resolution': resolution,
            'upload_to_cloud': upload_to_cloud,
        })
    
    def get_export_presets(self) -> Dict:
        """Get export presets"""
        return self._make_request('GET', '/export/presets')
    
    # ==================== Upload ====================
    
    def upload_video(self, file_path: str, upload_to_cloud: bool = True) -> Dict:
        """Upload video file"""
        # For file uploads, we'd use multipart form data
        # This is simplified for demonstration
        return self._make_request('POST', '/upload/upload', {
            'file_path': file_path,
            'upload_to_cloud': upload_to_cloud,
        })
    
    def get_upload_url(self, filename: str, content_type: str = 'video/mp4') -> Dict:
        """Get presigned upload URL"""
        return self._make_request('POST', '/upload/presigned', {
            'filename': filename,
            'content_type': content_type,
        })
    
    def list_files(self, prefix: str = '') -> Dict:
        """List uploaded files"""
        return self._make_request('GET', '/upload/files', {'prefix': prefix})
    
    # ==================== Hybrid Decision ====================
    
    def get_render_decision(
        self,
        video_size_mb: float,
        duration_seconds: float,
        resolution: str = '1080p',
        effects: List[Dict] = None,
        client_gpu_available: bool = False,
    ) -> Dict:
        """Get render location decision"""
        return self._make_request('POST', '/hybrid/decide', {
            'video_size_mb': video_size_mb,
            'video_duration_seconds': duration_seconds,
            'video_resolution': resolution,
            'effects': effects or [],
            'client_gpu_available': client_gpu_available,
        })
    
    def compare_render_options(
        self,
        video_size_mb: float,
        duration_seconds: float,
        resolution: str = '1080p',
        effects_count: int = 0,
    ) -> Dict:
        """Compare on-device vs cloud rendering"""
        return self._make_request('GET', '/hybrid/compare', {
            'video_size_mb': video_size_mb,
            'duration_seconds': duration_seconds,
            'resolution': resolution,
            'effects_count': effects_count,
        })
    
    # ==================== Voice/TTS ====================
    
    def text_to_speech(
        self,
        text: str,
        voice: str = 'alloy',
        speed: float = 1.0,
    ) -> Dict:
        """Convert text to speech"""
        return self._make_request('POST', '/voice/tts', {
            'text': text,
            'voice': voice,
            'speed': speed,
        })
    
    def get_voices(self) -> Dict:
        """Get available voices"""
        return self._make_request('GET', '/voice/voices')


# Global instance
api_client = APIClient()
