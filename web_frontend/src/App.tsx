import { useState, useRef } from 'react'
import { generateRecap, type RecapRequest } from './api/client'

// Icons
const SettingsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
);

const MovieIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="20" x="2" y="2" rx="2.18" ry="2.18"/><line x1="7" x2="7" y1="2" y2="22"/><line x1="17" x2="17" y1="2" y2="22"/><line x1="2" x2="22" y1="12" y2="12"/><line x1="2" x2="7" y1="7" y2="7"/><line x1="2" x2="7" y1="17" y2="17"/><line x1="17" x2="22" y1="17" y2="17"/><line x1="17" x2="22" y1="7" y2="7"/></svg>
);

const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" x2="12" y1="5" y2="19"/><line x1="5" x2="19" y1="12" y2="12"/></svg>
);

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
);

const EditIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
);

const RobotIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
);

const ExportIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v12"/><path d="m8 11 4 4 4-4"/><path d="M8 5H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-4"/></svg>
);

const CloudIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>
);

const CopyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
);

const TimelineIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 6h10"/><path d="M6 12h9"/><path d="M11 18h7"/></svg>
);

const CutIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" x2="8.12" y1="4" y2="15.88"/><line x1="14.47" x2="20" y1="14.48" y2="20"/><line x1="8.12" x2="12" y1="8.12" y2="12"/></svg>
);

const EffectsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
);

const RenderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 7h10"/><path d="M7 12h10"/><path d="M7 17h10"/></svg>
);

const FolderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
);

const BackIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
);

const PlayIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
);

const PauseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><rect width="4" height="16" x="6" y="4"/><rect width="4" height="16" x="14" y="4"/></svg>
);

type Screen = 'home' | 'recap' | 'editor' | 'export';

function App() {
  const [screen, setScreen] = useState<Screen>('home');
  const [gpuAvailable] = useState(false);
  
  // Video state
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  // Recap screen state
  const [transcript, setTranscript] = useState('');
  const [videoName] = useState('No video loaded');
  const [recapDuration, setRecapDuration] = useState(5);
  const [style, setStyle] = useState('engaging');
  const [model, setModel] = useState('Claude Sonnet');
  const [script, setScript] = useState('');
  const [recapLoading, setRecapLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Export screen state
  const [exportFormat, setExportFormat] = useState('mp4');
  const [exportQuality, setExportQuality] = useState('high');
  const [exportLocation, setExportLocation] = useState('local');
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  // Handle video upload
  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setVideoFile(file);
      setVideoUrl(URL.createObjectURL(file));
      setVideoName(file.name);
    }
  };

  // Video controls
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const seekTo = (time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const setVideoName = (name: string) => {
    // We'll use this to update the name in editor
  };

  // Recap functions
  const handleGenerateRecap = async () => {
    if (!transcript.trim()) {
      setError('Please enter or generate transcript');
      return;
    }

    setRecapLoading(true);
    setError('');

    try {
      const request: RecapRequest = {
        transcript,
        duration_minutes: recapDuration,
        style,
        target_audience: 'general',
      };
      const result = await generateRecap(request);
      setScript(result.script);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recap');
    } finally {
      setRecapLoading(false);
    }
  };

  const copyScript = () => {
    navigator.clipboard.writeText(script);
    alert('Script copied!');
  };

  // Export functions
  const applyPreset = (preset: string) => {
    switch (preset) {
      case 'youtube':
        setExportFormat('mp4');
        setExportQuality('ultra');
        break;
      case 'tiktok':
      case 'instagram':
        setExportFormat('mp4');
        setExportQuality('high');
        break;
      case 'twitter':
        setExportFormat('mp4');
        setExportQuality('medium');
        break;
    }
  };

  const startExport = () => {
    setExporting(true);
    setExportProgress(0);
    const interval = setInterval(() => {
      setExportProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setExporting(false);
          alert('Export completed!');
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // ==================== HOME SCREEN ====================
  if (screen === 'home') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <header className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
              Recap AI
            </h1>
            <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <SettingsIcon />
            </button>
          </header>

          <div className="bg-gray-800/80 backdrop-blur rounded-xl p-4 mb-6 border border-gray-700">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-600/20 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>
              </div>
              <div>
                <p className="font-medium">{gpuAvailable ? 'GPU: Available' : 'CPU Mode'}</p>
                <p className="text-sm text-gray-400">{gpuAvailable ? 'Ready for rendering' : 'GPU not available'}</p>
              </div>
            </div>
          </div>

          <h2 className="text-lg font-semibold mb-4">Recent Projects</h2>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <label className="flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-xl transition-colors cursor-pointer">
              <PlusIcon />
              New Project
            </label>
            <label className="flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white font-medium py-3 px-4 rounded-xl transition-colors cursor-pointer">
              <UploadIcon />
              Import Video
              <input type="file" accept="video/*" className="hidden" onChange={handleVideoUpload} />
            </label>
          </div>

          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-4 gap-3">
            <button 
              onClick={() => videoUrl && setScreen('editor')}
              className={`flex flex-col items-center gap-2 bg-gray-800/80 backdrop-blur p-4 rounded-xl border border-gray-700 transition-colors ${!videoUrl ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-700/80'}`}
              disabled={!videoUrl}
            >
              <div className="p-2 bg-blue-600/20 rounded-lg text-blue-400">
                <EditIcon />
              </div>
              <span className="text-xs">Edit</span>
              <span className="text-xs text-gray-500">Trim & effects</span>
            </button>
            
            <button 
              onClick={() => setScreen('recap')}
              className="flex flex-col items-center gap-2 bg-gray-800/80 hover:bg-gray-700/80 backdrop-blur p-4 rounded-xl border border-gray-700 transition-colors"
            >
              <div className="p-2 bg-purple-600/20 rounded-lg text-purple-400">
                <RobotIcon />
              </div>
              <span className="text-xs">AI Recap</span>
              <span className="text-xs text-gray-500">Generate script</span>
            </button>
            
            <button 
              onClick={() => videoUrl && setScreen('export')}
              className={`flex flex-col items-center gap-2 bg-gray-800/80 backdrop-blur p-4 rounded-xl border border-gray-700 transition-colors ${!videoUrl ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-700/80'}`}
              disabled={!videoUrl}
            >
              <div className="p-2 bg-green-600/20 rounded-lg text-green-400">
                <ExportIcon />
              </div>
              <span className="text-xs">Export</span>
              <span className="text-xs text-gray-500">Share video</span>
            </button>
            
            <button className="flex flex-col items-center gap-2 bg-gray-800/80 hover:bg-gray-700/80 backdrop-blur p-4 rounded-xl border border-gray-700 transition-colors">
              <div className="p-2 bg-cyan-600/20 rounded-lg text-cyan-400">
                <CloudIcon />
              </div>
              <span className="text-xs">Cloud</span>
              <span className="text-xs text-gray-500">Upload/Sync</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==================== EDITOR SCREEN ====================
  if (screen === 'editor') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white flex flex-col">
        {/* Header */}
        <header className="flex items-center gap-4 p-4 border-b border-gray-700">
          <button onClick={() => setScreen('home')} className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <BackIcon />
          </button>
          <h1 className="text-xl font-bold flex-1">Editor</h1>
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
          </button>
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          </button>
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          </button>
        </header>

        {/* Video Preview */}
        <div className="flex-1 p-4">
          <div className="bg-gray-800 rounded-xl overflow-hidden relative" style={{ aspectRatio: '16/9' }}>
            {videoUrl ? (
              <video 
                ref={videoRef}
                src={videoUrl}
                className="w-full h-full object-contain bg-black"
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <MovieIcon />
                  <p className="mt-2">No video loaded</p>
                </div>
              </div>
            )}
            
            {/* Play button overlay */}
            {videoUrl && (
              <button 
                onClick={togglePlay}
                className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors"
              >
                {isPlaying ? <PauseIcon /> : <PlayIcon />}
              </button>
            )}
          </div>
        </div>

        {/* Tools Panel */}
        <div className="px-4 pb-2">
          <div className="flex gap-2 overflow-x-auto pb-2">
            <button className="flex flex-col items-center gap-1 bg-gray-800 hover:bg-gray-700 p-3 rounded-xl border border-gray-700 min-w-[70px]">
              <CutIcon />
              <span className="text-xs">Trim</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-gray-800 hover:bg-gray-700 p-3 rounded-xl border border-gray-700 min-w-[70px]">
              <EffectsIcon />
              <span className="text-xs">Effects</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-gray-800 hover:bg-gray-700 p-3 rounded-xl border border-gray-700 min-w-[70px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>
              <span className="text-xs">Captions</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-gray-800 hover:bg-gray-700 p-3 rounded-xl border border-gray-700 min-w-[70px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              <span className="text-xs">Text</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-gray-800 hover:bg-gray-700 p-3 rounded-xl border border-gray-700 min-w-[70px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
              <span className="text-xs">Filters</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-gray-800 hover:bg-gray-700 p-3 rounded-xl border border-gray-700 min-w-[70px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3"/><path d="M21 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3"/><path d="M4 12h16"/><path d="m15 9-3 3-3-3"/></svg>
              <span className="text-xs">Merge</span>
            </button>
          </div>
        </div>

        {/* Timeline */}
        <div className="px-4 pb-2">
          <div className="bg-gray-800 rounded-xl p-3 border border-gray-700">
            <div className="flex items-center gap-4 mb-2">
              <span className="text-xs text-gray-400 w-12">{formatTime(currentTime)}</span>
              <input
                type="range"
                min="0"
                max={duration || 100}
                value={currentTime}
                onChange={(e) => seekTo(Number(e.target.value))}
                className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <span className="text-xs text-gray-400 w-12 text-right">{formatTime(duration)}</span>
            </div>
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-gray-700">
          <div className="grid grid-cols-4 gap-3">
            <button 
              onClick={() => setScreen('recap')}
              className="flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-xl transition-colors"
            >
              <RobotIcon />
              <span className="text-sm">AI Recap</span>
            </button>
            <button className="flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-xl transition-colors">
              <EffectsIcon />
              <span className="text-sm">Effects</span>
            </button>
            <button className="flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-xl transition-colors">
              <RenderIcon />
              <span className="text-sm">Render</span>
            </button>
            <button 
              onClick={() => setScreen('export')}
              className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-xl transition-colors"
            >
              <ExportIcon />
              <span className="text-sm">Export</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==================== RECAP SCREEN ====================
  if (screen === 'recap') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <header className="flex items-center gap-4 mb-6">
            <button onClick={() => setScreen('editor')} className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <BackIcon />
            </button>
            <h1 className="text-xl font-bold">AI Recap</h1>
          </header>

          <div className="bg-gray-800/80 backdrop-blur rounded-xl p-4 mb-6 border border-gray-700">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-600/20 rounded-lg text-purple-400">
                <MovieIcon />
              </div>
              <div>
                <p className="font-medium">{videoFile?.name || 'No video loaded'}</p>
                <p className="text-sm text-gray-400">Duration: {formatTime(duration)}</p>
              </div>
            </div>
          </div>

          <h3 className="text-lg font-semibold mb-3">Transcript</h3>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste or type transcript..."
            className="w-full h-40 bg-gray-800/80 backdrop-blur rounded-xl p-4 text-white placeholder-gray-500 resize-none focus:ring-2 focus:ring-purple-500 focus:outline-none border border-gray-700 mb-6"
          />

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full bg-gray-800/80 border border-gray-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
              >
                <option value="engaging">Engaging</option>
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
                <option value="technical">Technical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-gray-800/80 border border-gray-700 rounded-xl p-3 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
              >
                <option value="Claude Sonnet">Claude Sonnet</option>
                <option value="GPT-4o">GPT-4o</option>
                <option value="GPT-4o Mini">GPT-4o Mini</option>
                <option value="Llama 3">Llama 3</option>
              </select>
            </div>
          </div>

          <div className="bg-gray-800/80 backdrop-blur rounded-xl p-4 mb-6 border border-gray-700">
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-400 w-20">Duration</span>
              <input
                type="range"
                min="1"
                max="30"
                value={recapDuration}
                onChange={(e) => setRecapDuration(Number(e.target.value))}
                className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <span className="text-sm w-16 text-right">{recapDuration} min</span>
            </div>
          </div>

          <button
            onClick={handleGenerateRecap}
            disabled={recapLoading}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl transition-all mb-6"
          >
            <RobotIcon />
            {recapLoading ? 'Generating...' : 'Generate Recap'}
          </button>

          {error && (
            <div className="p-4 bg-red-900/50 border border-red-500 rounded-xl text-red-200 mb-6">
              {error}
            </div>
          )}

          {script && (
            <>
              <div className="bg-gray-800/80 backdrop-blur rounded-xl p-4 mb-4 border border-gray-700">
                <h3 className="text-lg font-semibold mb-3">Generated Script</h3>
                <pre className="whitespace-pre-wrap text-gray-300 bg-gray-900/50 rounded-lg p-4 max-h-64 overflow-y-auto">
                  {script}
                </pre>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <button className="flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-xl transition-colors">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                  Edit Script
                </button>
                <button className="flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-xl transition-colors">
                  <TimelineIcon />
                  Apply to Timeline
                </button>
                <button onClick={copyScript} className="flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-3 px-4 rounded-xl transition-colors">
                  <CopyIcon />
                  Copy
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  // ==================== EXPORT SCREEN ====================
  if (screen === 'export') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <header className="flex items-center gap-4 mb-6">
            <button onClick={() => setScreen('editor')} className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <BackIcon />
            </button>
            <h1 className="text-xl font-bold">Export</h1>
          </header>

          {/* Video Preview */}
          <div className="bg-gray-800/80 backdrop-blur rounded-xl p-4 mb-6 border border-gray-700">
            <div className="flex items-center gap-4">
              <div className="bg-gray-900 rounded-lg p-3" style={{ aspectRatio: '16/9', width: '120px' }}>
                {videoUrl && <video src={videoUrl} className="w-full h-full object-contain" />}
              </div>
              <div>
                <p className="font-medium">{videoFile?.name || 'Video'}</p>
                <p className="text-sm text-gray-400">1920x1080 • 30fps</p>
              </div>
            </div>
          </div>

          {/* Format Selection */}
          <h3 className="text-lg font-semibold mb-3">Format</h3>
          <div className="grid grid-cols-3 gap-3 mb-6">
            {['mp4', 'webm', 'mov'].map((format) => (
              <button
                key={format}
                onClick={() => setExportFormat(format)}
                className={`py-3 px-4 rounded-xl font-medium transition-colors ${
                  exportFormat === format
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
                }`}
              >
                {format.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Quality Selection */}
          <h3 className="text-lg font-semibold mb-3">Quality</h3>
          <div className="grid grid-cols-4 gap-3 mb-6">
            {[
              { id: 'low', label: 'Low', sub: '480p' },
              { id: 'medium', label: 'Medium', sub: '720p' },
              { id: 'high', label: 'High', sub: '1080p' },
              { id: 'ultra', label: 'Ultra', sub: '4K' },
            ].map((q) => (
              <button
                key={q.id}
                onClick={() => setExportQuality(q.id)}
                className={`py-3 px-2 rounded-xl transition-colors ${
                  exportQuality === q.id
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
                }`}
              >
                <div className="font-medium text-sm">{q.label}</div>
                <div className={`text-xs ${exportQuality === q.id ? 'text-purple-200' : 'text-gray-500'}`}>{q.sub}</div>
              </button>
            ))}
          </div>

          {/* Export Location */}
          <h3 className="text-lg font-semibold mb-3">Export Location</h3>
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              onClick={() => setExportLocation('local')}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-colors ${
                exportLocation === 'local'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
              }`}
            >
              <FolderIcon />
              Save to Device
            </button>
            <button
              onClick={() => setExportLocation('cloud')}
              className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl transition-colors ${
                exportLocation === 'cloud'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
              }`}
            >
              <CloudIcon />
              Cloud
            </button>
          </div>

          {/* Quick Presets */}
          <h3 className="text-lg font-semibold mb-3">Quick Presets</h3>
          <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
            {['YouTube', 'TikTok', 'Instagram', 'Twitter'].map((preset) => (
              <button
                key={preset}
                onClick={() => applyPreset(preset.toLowerCase())}
                className="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white py-2 px-4 rounded-full text-sm whitespace-nowrap transition-colors"
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Progress */}
          {exporting && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Exporting...</span>
                <span className="text-sm text-gray-400">{exportProgress}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-600 transition-all duration-300"
                  style={{ width: `${exportProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Export Button */}
          <button
            onClick={startExport}
            disabled={exporting}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 text-white font-semibold py-4 rounded-xl transition-all"
          >
            <ExportIcon />
            {exporting ? 'Exporting...' : 'Export Video'}
          </button>
        </div>
      </div>
    );
  }

  return null;
}

export default App;
