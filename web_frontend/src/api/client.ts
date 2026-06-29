/**
 * API Client for Recap AI Web Frontend
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/openrouter';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== GPU Status ====================

export const getGPUStatus = async () => {
  const response = await api.get('/render/status');
  return response.data;
};

export const getCodecs = async () => {
  const response = await api.get('/render/codecs');
  return response.data;
};

// ==================== Recap ====================

export interface RecapRequest {
  transcript: string;
  duration_minutes: number;
  style: string;
  target_audience?: string;
}

export interface RecapResponse {
  success: boolean;
  script: string;
}

export const generateRecap = async (data: RecapRequest): Promise<RecapResponse> => {
  const response = await api.post('/recap', data);
  return response.data;
};

export const summarizeContent = async (text: string, maxSentences = 5) => {
  const response = await api.post('/summarize', { text, max_sentences: maxSentences });
  return response.data;
};

export const generateHashtags = async (content: string, numHashtags = 10) => {
  const response = await api.post('/hashtags', { content, num_hashtags: numHashtags });
  return response.data;
};

export const transcribeVideo = async (videoUrl: string, language = 'auto') => {
  const response = await api.post('/recap/transcribe', {
    video_url: videoUrl,
    language,
  });
  return response.data;
};

export const getModels = async () => {
  const response = await api.get('/recap/models');
  return response.data;
};

export const getStyles = async () => {
  const response = await api.get('/recap/styles');
  return response.data;
};

// ==================== Video Edit ====================

export const getVideoInfo = async (videoPath: string) => {
  const response = await api.get(`/video/info/${encodeURIComponent(videoPath)}`);
  return response.data;
};

export const trimVideo = async (videoPath: string, startTime: number, endTime: number) => {
  const response = await api.post('/video/trim', {
    video_path: videoPath,
    start_time: startTime,
    end_time: endTime,
  });
  return response.data;
};

export const mergeVideos = async (videoPaths: string[]) => {
  const response = await api.post('/video/merge', {
    video_paths: videoPaths,
  });
  return response.data;
};

export const applyEffects = async (videoPath: string, effects: any[]) => {
  const response = await api.post('/video/effects', {
    video_path: videoPath,
    effects,
  });
  return response.data;
};

// ==================== Render ====================

export interface RenderRequest {
  input_path: string;
  codec?: string;
  quality?: string;
  resolution?: string;
  gpu_device?: number;
}

export const submitRenderJob = async (data: RenderRequest) => {
  const response = await api.post('/render/submit', data);
  return response.data;
};

export const getRenderJob = async (jobId: string) => {
  const response = await api.get(`/render/jobs/${jobId}`);
  return response.data;
};

export const listRenderJobs = async () => {
  const response = await api.get('/render/jobs');
  return response.data;
};

export const cancelRenderJob = async (jobId: string) => {
  const response = await api.delete(`/render/jobs/${jobId}`);
  return response.data;
};

// ==================== Export ====================

export interface ExportRequest {
  video_path: string;
  format?: string;
  quality?: string;
  resolution?: string;
  upload_to_cloud?: boolean;
}

export const exportVideo = async (data: ExportRequest) => {
  const response = await api.post('/export/export', data);
  return response.data;
};

export const getExportPresets = async () => {
  const response = await api.get('/export/presets');
  return response.data;
};

// ==================== Hybrid Decision ====================

export interface DecisionRequest {
  video_size_mb: number;
  video_duration_seconds: number;
  video_resolution?: string;
  effects?: any[];
  client_gpu_available?: boolean;
}

export const getRenderDecision = async (data: DecisionRequest) => {
  const response = await api.post('/hybrid/decide', data);
  return response.data;
};

export const compareRenderOptions = async (
  videoSizeMb: number,
  durationSeconds: number,
  resolution = '1080p',
  effectsCount = 0
) => {
  const response = await api.get('/hybrid/compare', {
    params: {
      video_size_mb: videoSizeMb,
      duration_seconds: durationSeconds,
      resolution,
      effects_count: effectsCount,
    },
  });
  return response.data;
};

// ==================== Upload ====================

export const uploadVideo = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getUploadUrl = async (filename: string, contentType: string) => {
  const response = await api.post('/upload/presigned', {
    filename,
    content_type: contentType,
  });
  return response.data;
};

export const listFiles = async (prefix = '') => {
  const response = await api.get('/upload/files', { params: { prefix } });
  return response.data;
};

// ==================== Voice ====================

export const textToSpeech = async (text: string, voice = 'alloy', speed = 1.0) => {
  const response = await api.post('/voice/tts', {
    text,
    voice,
    speed,
  });
  return response.data;
};

export const getVoices = async () => {
  const response = await api.get('/voice/voices');
  return response.data;
};

export default api;
