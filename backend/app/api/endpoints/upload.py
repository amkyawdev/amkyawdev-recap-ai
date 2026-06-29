"""
Upload API Endpoints
Video upload to S3/R2 storage
"""
import os
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.storage import storage


router = APIRouter()


class UploadResponse(BaseModel):
    success: bool
    file_id: str
    filename: str
    size: int
    content_type: str
    local_path: Optional[str] = None
    cloud_url: Optional[str] = None
    uploaded_at: datetime


class UploadProgress(BaseModel):
    file_id: str
    filename: str
    progress: float
    status: str  # uploading, processing, completed, failed
    error: Optional[str] = None


# In-memory tracking (use Redis in production)
_upload_progress = {}


class ChunkedUploadSession:
    """Track chunked upload session"""
    def __init__(self, file_id: str, filename: str, total_chunks: int):
        self.file_id = file_id
        self.filename = filename
        self.total_chunks = total_chunks
        self.uploaded_chunks = 0
        self.chunks = {}
        self.created_at = datetime.now()
    
    @property
    def progress(self) -> float:
        if self.total_chunks == 0:
            return 0
        return self.uploaded_chunks / self.total_chunks
    
    def add_chunk(self, chunk_number: int, data: bytes):
        self.chunks[chunk_number] = data
        self.uploaded_chunks += 1
    
    def is_complete(self) -> bool:
        return self.uploaded_chunks >= self.total_chunks


_chunks_sessions: dict[str, ChunkedUploadSession] = {}


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    upload_to_cloud: bool = True,
    background_tasks: BackgroundTasks = None
):
    """
    Upload video file
    
    Supports direct upload and streams to S3/R2.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.SUPPORTED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {settings.SUPPORTED_VIDEO_FORMATS}"
        )
    
    file_id = f"video_{uuid.uuid4().hex[:12]}"
    local_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Write file
    try:
        with open(local_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        size = len(content)
        
        # Check size limit
        max_size = settings.MAX_VIDEO_SIZE_MB * 1024 * 1024
        if size > max_size:
            os.unlink(local_path)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max: {settings.MAX_VIDEO_SIZE_MB}MB"
            )
        
        response = UploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            size=size,
            content_type=file.content_type or "video/mp4",
            local_path=local_path,
            uploaded_at=datetime.now()
        )
        
        # Upload to cloud
        if upload_to_cloud and storage.is_available:
            cloud_key = f"uploads/{datetime.now().strftime('%Y/%m/%d')}/{file_id}{ext}"
            if storage.upload_file(local_path, cloud_key, file.content_type):
                response.cloud_url = storage.get_presigned_url(cloud_key)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload/presigned")
async def get_upload_url(
    filename: str,
    content_type: str = "video/mp4",
    file_size: Optional[int] = None
):
    """
    Get presigned URL for direct upload to S3/R2
    
    Frontend can upload directly to storage without passing through backend.
    """
    if not storage.is_available:
        raise HTTPException(status_code=500, detail="Cloud storage not configured")
    
    file_id = f"video_{uuid.uuid4().hex[:12]}"
    ext = os.path.splitext(filename)[1].lower()
    cloud_key = f"uploads/{datetime.now().strftime('%Y/%m/%d')}/{file_id}{ext}"
    
    try:
        # Generate presigned PUT URL
        presigned_url = storage.client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': cloud_key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            "success": True,
            "file_id": file_id,
            "upload_url": presigned_url,
            "cloud_key": cloud_key,
            "method": "PUT",
            "headers": {
                "Content-Type": content_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate URL: {str(e)}")


@router.post("/upload/chunked/init")
async def init_chunked_upload(
    filename: str,
    total_chunks: int,
    file_size: int,
    content_type: str = "video/mp4"
):
    """Initialize chunked upload session"""
    file_id = f"video_{uuid.uuid4().hex[:12]}"
    
    session = ChunkedUploadSession(file_id, filename, total_chunks)
    _chunks_sessions[file_id] = session
    
    return {
        "success": True,
        "file_id": file_id,
        "total_chunks": total_chunks,
        "chunk_size": file_size // total_chunks if total_chunks > 0 else 0
    }


@router.post("/upload/chunked/{file_id}")
async def upload_chunk(
    file_id: str,
    chunk_number: int,
    chunk: UploadFile = File(...)
):
    """Upload a chunk of the file"""
    if file_id not in _chunks_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = _chunks_sessions[file_id]
    
    if chunk_number >= session.total_chunks:
        raise HTTPException(status_code=400, detail="Invalid chunk number")
    
    try:
        data = await chunk.read()
        session.add_chunk(chunk_number, data)
        
        return {
            "success": True,
            "file_id": file_id,
            "chunk_number": chunk_number,
            "uploaded_chunks": session.uploaded_chunks,
            "total_chunks": session.total_chunks,
            "progress": session.progress
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunk upload failed: {str(e)}")


@router.post("/upload/chunked/{file_id}/complete")
async def complete_chunked_upload(
    file_id: str,
    upload_to_cloud: bool = True
):
    """Complete chunked upload and merge chunks"""
    if file_id not in _chunks_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = _chunks_sessions[file_id]
    
    if not session.is_complete():
        raise HTTPException(
            status_code=400,
            detail=f"Upload incomplete. {session.uploaded_chunks}/{session.total_chunks} chunks uploaded"
        )
    
    try:
        # Merge chunks
        ext = os.path.splitext(session.filename)[1].lower()
        output_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
        
        with open(output_path, "wb") as out:
            for i in range(session.total_chunks):
                out.write(session.chunks[i])
        
        # Calculate total size
        total_size = sum(len(c) for c in session.chunks.values())
        
        # Upload to cloud
        cloud_url = None
        if upload_to_cloud and storage.is_available:
            cloud_key = f"uploads/{datetime.now().strftime('%Y/%m/%d')}/{file_id}{ext}"
            storage.upload_file(output_path, cloud_key, f"video/{ext.lstrip('.')}")
            cloud_url = storage.get_presigned_url(cloud_key)
        
        # Cleanup session
        del _chunks_sessions[file_id]
        
        return UploadResponse(
            success=True,
            file_id=file_id,
            filename=session.filename,
            size=total_size,
            content_type="video/mp4",
            local_path=output_path,
            cloud_url=cloud_url,
            uploaded_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete upload: {str(e)}")


@router.get("/files")
async def list_uploaded_files(prefix: str = ""):
    """List uploaded files from storage"""
    if not storage.is_available:
        # List from local storage
        files = []
        if os.path.exists(settings.UPLOAD_DIR):
            for f in os.listdir(settings.UPLOAD_DIR):
                path = os.path.join(settings.UPLOAD_DIR, f)
                if os.path.isfile(path):
                    files.append({
                        "filename": f,
                        "size": os.path.getsize(path),
                        "path": path
                    })
        return {"files": files, "source": "local"}
    
    # List from cloud
    cloud_files = storage.list_files(prefix=f"uploads/{prefix}")
    return {
        "files": [
            {
                "key": f['Key'],
                "size": f['Size'],
                "last_modified": f.get('LastModified')
            }
            for f in cloud_files
        ],
        "source": "cloud"
    }


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    # Try local
    for ext in settings.SUPPORTED_VIDEO_FORMATS:
        path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
        if os.path.exists(path):
            os.unlink(path)
            return {"success": True, "message": "File deleted locally"}
    
    # Try cloud
    if storage.is_available:
        files = storage.list_files(prefix="uploads/")
        for f in files:
            if file_id in f['Key']:
                storage.delete_file(f['Key'])
                return {"success": True, "message": "File deleted from cloud"}
    
    raise HTTPException(status_code=404, detail="File not found")
