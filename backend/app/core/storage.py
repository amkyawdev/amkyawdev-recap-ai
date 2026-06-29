"""
S3/R2 Storage Client
"""
import os
import logging
from typing import Optional, BinaryIO
from datetime import timedelta
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


logger = logging.getLogger(__name__)


class StorageClient:
    """S3/R2 compatible storage client"""
    
    def __init__(self):
        self.client = None
        self.resource = None
        self._initialize()
    
    def _initialize(self):
        """Initialize S3 client"""
        if not settings.S3_ENDPOINT_URL:
            logger.warning("S3 endpoint not configured")
            return
        
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )
            self.resource = boto3.resource(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )
            logger.info("S3 client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if storage is available"""
        return self.client is not None
    
    def upload_file(self, file_path: str, key: str, content_type: Optional[str] = None) -> bool:
        """
        Upload a file to storage
        
        Args:
            file_path: Local file path
            key: Storage key (path)
            content_type: MIME type
            
        Returns:
            True if successful
        """
        if not self.is_available:
            return False
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_file(
                file_path,
                settings.S3_BUCKET_NAME,
                key,
                ExtraArgs=extra_args
            )
            logger.info(f"Uploaded {file_path} to {key}")
            return True
        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def upload_fileobj(self, file_obj: BinaryIO, key: str, content_type: Optional[str] = None) -> bool:
        """Upload a file object"""
        if not self.is_available:
            return False
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(
                file_obj,
                settings.S3_BUCKET_NAME,
                key,
                ExtraArgs=extra_args
            )
            return True
        except ClientError as e:
            logger.error(f"Upload failed: {e}")
            return False
    
    def download_file(self, key: str, file_path: str) -> bool:
        """Download a file from storage"""
        if not self.is_available:
            return False
        
        try:
            self.client.download_file(settings.S3_BUCKET_NAME, key, file_path)
            return True
        except ClientError as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def get_presigned_url(self, key: str, expires: int = 3600) -> Optional[str]:
        """
        Get a presigned URL for temporary access
        
        Args:
            key: Storage key
            expires: Expiration time in seconds
            
        Returns:
            Presigned URL or None
        """
        if not self.is_available:
            return None
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': key},
                ExpiresIn=expires
            )
            return url
        except ClientError as e:
            logger.error(f"Presigned URL generation failed: {e}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """Delete a file from storage"""
        if not self.is_available:
            return False
        
        try:
            self.client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """List files with optional prefix"""
        if not self.is_available:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=settings.S3_BUCKET_NAME,
                Prefix=prefix
            )
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"List failed: {e}")
            return []
    
    def file_exists(self, key: str) -> bool:
        """Check if file exists"""
        if not self.is_available:
            return False
        
        try:
            self.client.head_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            return True
        except ClientError:
            return False


# Global storage client
storage = StorageClient()
