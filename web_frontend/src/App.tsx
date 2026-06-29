import { useState, useRef } from 'react'
import { generateRecap, type RecapRequest } from './api/client'
import LoadingScreen from './components/LoadingScreen'

// Icons
const SettingsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
);

const MovieIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="20" x="2" y="2" rx="2.18" ry="2.18"/><line x1="7" x2="7" y1="2" y2="22"/><line x1="17" x2="17" y1="2" y2="22"/><line x1="2" x2="22" y1="12" y2="12"/><line x1="2" x2="7" y1="7" y2="7"/><line x1="2" x2="7" y1="17" y2="17"/><line x1="17" x2="22" y1="17" y2="17"/><line x1="17" x2="22" y1="7" y2="7"/></svg>
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
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="20" x2="8.12" y1="4" y2="15.88"/><line x1="14.47" x2="20" y1="14.48" y2="20"/><line x1="8.12" x2="12" y1="8.12" y2="12"/></svg>
);

const EffectsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
);

const RenderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M7 7h10"/><path d="M7 12h10"/><path d="M7 17h10"/></svg>
);

const FolderIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
);

const BackIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
);

const PlayIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
);

const PauseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><rect width="4" height="16" x="6" y="4"/><rect width="4" height="16" x="14" y="4"/></svg>
);

const SparklesIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>
);

type Screen = 'home' | 'recap' | 'editor' | 'export';

function App() {
  // All hooks must be called before any conditional return
  const [loading, setLoading] = useState(true);
  const [screen, setScreen] = useState<Screen>('home');
  const [gpuAvailable] = useState(true);
  
  // Video state
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  // Recap screen state
  const [transcript, setTranscript] = useState('');
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

  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setVideoFile(file);
      setVideoUrl(URL.createObjectURL(file));
    }
  };

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

  const handleGenerateRecap = async () => {
    if (!transcript.trim()) {
      setError('Please enter transcript');
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
    alert('Copied!');
  };

  const applyPreset = (preset: string) => {
    switch (preset) {
      case 'youtube': setExportFormat('mp4'); setExportQuality('ultra'); break;
      case 'tiktok': case 'instagram': setExportFormat('mp4'); setExportQuality('high'); break;
      case 'twitter': setExportFormat('mp4'); setExportQuality('medium'); break;
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

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // ==================== HOME SCREEN ====================
  if (screen === 'home') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 text-white">
        <div className="container mx-auto px-4 py-8 max-w-5xl">
          
          {/* Header */}
          <header className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
                <SparklesIcon />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-violet-400 via-purple-400 to-fuchsia-400 bg-clip-text text-transparent">
                  Recap AI
                </h1>
                <p className="text-xs text-slate-500">Video Recap Generator</p>
              </div>
            </div>
            <button className="p-3 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 transition-all hover:scale-105">
              <SettingsIcon />
            </button>
          </header>

          {/* GPU Status */}
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-5 mb-8 border border-slate-700/50">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-emerald-400"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></svg>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-emerald-400">{gpuAvailable ? 'GPU Accelerated' : 'CPU Mode'}</p>
                <p className="text-sm text-slate-400">{gpuAvailable ? 'Ready for fast rendering' : 'Using software rendering'}</p>
              </div>
              <div className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
                {gpuAvailable ? 'Active' : 'Idle'}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <label className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-6 border border-slate-700/50 hover:border-violet-500/50 transition-all cursor-pointer group hover:shadow-lg hover:shadow-violet-500/10">
              <div className="flex flex-col items-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg shadow-violet-500/30">
                  <PlusIcon />
                </div>
                <span className="font-semibold text-lg">New Project</span>
                <span className="text-sm text-slate-500">Start fresh</span>
              </div>
            </label>
            <label className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-6 border border-slate-700/50 hover:border-cyan-500/50 transition-all cursor-pointer group hover:shadow-lg hover:shadow-cyan-500/10">
              <div className="flex flex-col items-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg shadow-cyan-500/30">
                  <UploadIcon />
                </div>
                <span className="font-semibold text-lg">Import Video</span>
                <span className="text-sm text-slate-500">Upload from device</span>
              </div>
              <input type="file" accept="video/*" className="hidden" onChange={handleVideoUpload} />
            </label>
          </div>

          {/* Quick Actions */}
          <h2 className="text-lg font-semibold mb-4 text-slate-300">Quick Actions</h2>
          <div className="grid grid-cols-4 gap-3">
            {[
              { icon: <EditIcon />, label: 'Editor', sub: 'Trim & effects', color: 'blue', action: () => videoUrl && setScreen('editor') },
              { icon: <RobotIcon />, label: 'AI Recap', sub: 'Generate script', color: 'violet', action: () => setScreen('recap') },
              { icon: <ExportIcon />, label: 'Export', sub: 'Share video', color: 'emerald', action: () => videoUrl && setScreen('export') },
              { icon: <CloudIcon />, label: 'Cloud', sub: 'Upload/Sync', color: 'sky', action: () => {} },
            ].map((item, i) => (
              <button 
                key={i}
                onClick={item.action}
                disabled={!videoUrl && item.color !== 'violet'}
                className={`bg-slate-800/60 backdrop-blur-xl rounded-2xl p-4 border border-slate-700/50 transition-all hover:shadow-lg ${!videoUrl && item.color !== 'violet' ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className={`w-10 h-10 rounded-xl bg-${item.color}-500/20 border border-${item.color}-500/30 flex items-center justify-center mx-auto mb-3 text-${item.color}-400`}>
                  {item.icon}
                </div>
                <p className="font-medium text-sm">{item.label}</p>
                <p className="text-xs text-slate-500">{item.sub}</p>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ==================== EDITOR SCREEN ====================
  if (screen === 'editor') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 text-white flex flex-col">
        {/* Header */}
        <header className="flex items-center gap-4 p-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <button onClick={() => setScreen('home')} className="p-2 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 transition-colors">
            <BackIcon />
          </button>
          <h1 className="text-xl font-bold flex-1">Video Editor</h1>
          <div className="flex gap-2">
            <button className="p-2 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 text-slate-400 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
            </button>
            <button className="p-2 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 text-slate-400 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            </button>
          </div>
        </header>

        {/* Video Preview */}
        <div className="flex-1 p-4">
          <div className="bg-black rounded-2xl overflow-hidden relative shadow-2xl shadow-violet-500/10" style={{ aspectRatio: '16/9' }}>
            {videoUrl ? (
              <video 
                ref={videoRef}
                src={videoUrl}
                className="w-full h-full object-contain"
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
              />
            ) : (
              <div className="flex items-center justify-center h-full bg-gradient-to-br from-slate-800 to-slate-900">
                <div className="text-center text-slate-500">
                  <MovieIcon />
                  <p className="mt-3">No video loaded</p>
                </div>
              </div>
            )}
            
            {videoUrl && (
              <button 
                onClick={togglePlay}
                className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors group"
              >
                <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:scale-110 transition-transform">
                  {isPlaying ? <PauseIcon /> : <PlayIcon />}
                </div>
              </button>
            )}
          </div>
        </div>

        {/* Tools Panel */}
        <div className="px-4 pb-2">
          <div className="flex gap-2 overflow-x-auto pb-2">
            {[
              { icon: <CutIcon />, label: 'Trim' },
              { icon: <EffectsIcon />, label: 'Effects' },
              { icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/></svg>, label: 'Captions' },
              { icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>, label: 'Text' },
              { icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>, label: 'Filters' },
              { icon: <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3"/><path d="M21 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3"/><path d="M4 12h16"/></svg>, label: 'Merge' },
            ].map((tool, i) => (
              <button key={i} className="bg-slate-800/60 backdrop-blur-xl rounded-xl p-3 border border-slate-700/50 hover:border-violet-500/50 transition-all min-w-[70px]">
                <div className="text-slate-400 flex justify-center mb-1">{tool.icon}</div>
                <span className="text-xs text-slate-400">{tool.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Timeline */}
        <div className="px-4 pb-2">
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-xl p-4 border border-slate-700/50">
            <div className="flex items-center gap-4 mb-3">
              <span className="text-xs text-slate-500 w-12">{formatTime(currentTime)}</span>
              <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all"
                  style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                />
              </div>
              <span className="text-xs text-slate-500 w-12 text-right">{formatTime(duration)}</span>
            </div>
            <input
              type="range"
              min="0"
              max={duration || 100}
              value={currentTime}
              onChange={(e) => seekTo(Number(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-violet-500"
            />
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <div className="grid grid-cols-4 gap-3">
            <button onClick={() => setScreen('recap')} className="flex flex-col items-center gap-1 bg-slate-800/50 hover:bg-slate-700/50 py-3 px-2 rounded-xl transition-all border border-slate-700/50 hover:border-violet-500/50">
              <RobotIcon />
              <span className="text-xs">AI Recap</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-slate-800/50 hover:bg-slate-700/50 py-3 px-2 rounded-xl transition-all border border-slate-700/50 hover:border-blue-500/50">
              <EffectsIcon />
              <span className="text-xs">Effects</span>
            </button>
            <button className="flex flex-col items-center gap-1 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 py-3 px-2 rounded-xl transition-all shadow-lg shadow-violet-500/30">
              <RenderIcon />
              <span className="text-xs">Render</span>
            </button>
            <button onClick={() => setScreen('export')} className="flex flex-col items-center gap-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 py-3 px-2 rounded-xl transition-all shadow-lg shadow-emerald-500/30">
              <ExportIcon />
              <span className="text-xs">Export</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==================== RECAP SCREEN ====================
  if (screen === 'recap') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 text-white">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <header className="flex items-center gap-4 mb-8">
            <button onClick={() => setScreen('editor')} className="p-2 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 transition-colors">
              <BackIcon />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
                <RobotIcon />
              </div>
              <h1 className="text-xl font-bold">AI Recap Generator</h1>
            </div>
          </header>

          {/* Video Info */}
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-5 mb-6 border border-slate-700/50">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-xl bg-violet-500/20 border border-violet-500/30 flex items-center justify-center text-violet-400">
                <MovieIcon />
              </div>
              <div className="flex-1">
                <p className="font-semibold">{videoFile?.name || 'No video loaded'}</p>
                <p className="text-sm text-slate-400">{videoUrl ? 'Ready for transcription' : 'Import a video to get started'}</p>
              </div>
            </div>
          </div>

          {/* Transcript */}
          <h3 className="text-lg font-semibold mb-3 text-slate-300">Transcript</h3>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste or type transcript here..."
            className="w-full h-40 bg-slate-800/60 backdrop-blur-xl rounded-2xl p-4 text-white placeholder-slate-500 resize-none focus:ring-2 focus:ring-violet-500 focus:outline-none border border-slate-700/50 mb-6"
          />

          {/* Settings */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm text-slate-400 mb-2 font-medium">Script Style</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full bg-slate-800/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 focus:outline-none"
              >
                <option value="engaging">Engaging</option>
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
                <option value="technical">Technical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-2 font-medium">AI Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-slate-800/60 backdrop-blur-xl border border-slate-700/50 rounded-xl p-3 text-white focus:ring-2 focus:ring-violet-500 focus:outline-none"
              >
                <option value="Claude Sonnet">Claude Sonnet</option>
                <option value="GPT-4o">GPT-4o</option>
                <option value="GPT-4o Mini">GPT-4o Mini</option>
                <option value="Llama 3">Llama 3</option>
              </select>
            </div>
          </div>

          {/* Duration */}
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-5 mb-6 border border-slate-700/50">
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-400 font-medium w-20">Duration</span>
              <input
                type="range"
                min="1"
                max="30"
                value={recapDuration}
                onChange={(e) => setRecapDuration(Number(e.target.value))}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-violet-500"
              />
              <span className="text-sm w-16 text-right font-medium">{recapDuration} min</span>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerateRecap}
            disabled={recapLoading}
            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-2xl transition-all shadow-xl shadow-violet-500/30 mb-6"
          >
            <RobotIcon />
            {recapLoading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Generating...
              </span>
            ) : 'Generate Recap Script'}
          </button>

          {error && (
            <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 mb-6">
              {error}
            </div>
          )}

          {script && (
            <>
              <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-5 mb-4 border border-slate-700/50">
                <h3 className="text-lg font-semibold mb-3 text-slate-300">Generated Script</h3>
                <pre className="whitespace-pre-wrap text-slate-300 bg-slate-900/50 rounded-xl p-4 max-h-72 overflow-y-auto text-sm leading-relaxed">
                  {script}
                </pre>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <button className="flex items-center justify-center gap-2 bg-slate-800/60 hover:bg-slate-700/60 text-white py-3 px-4 rounded-xl transition-all border border-slate-700/50 hover:border-slate-600">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                  Edit
                </button>
                <button className="flex items-center justify-center gap-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white py-3 px-4 rounded-xl transition-all shadow-lg shadow-violet-500/20">
                  <TimelineIcon />
                  Apply
                </button>
                <button onClick={copyScript} className="flex items-center justify-center gap-2 bg-slate-800/60 hover:bg-slate-700/60 text-white py-3 px-4 rounded-xl transition-all border border-slate-700/50 hover:border-slate-600">
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
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 text-white">
        <div className="container mx-auto px-4 py-6 max-w-4xl">
          <header className="flex items-center gap-4 mb-8">
            <button onClick={() => setScreen('editor')} className="p-2 rounded-xl bg-slate-800/50 hover:bg-slate-700/50 transition-colors">
              <BackIcon />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
                <ExportIcon />
              </div>
              <h1 className="text-xl font-bold">Export Video</h1>
            </div>
          </header>

          {/* Video Preview */}
          <div className="bg-slate-800/60 backdrop-blur-xl rounded-2xl p-5 mb-6 border border-slate-700/50">
            <div className="flex items-center gap-4">
              <div className="bg-slate-900 rounded-xl overflow-hidden" style={{ aspectRatio: '16/9', width: '140px' }}>
                {videoUrl && <video src={videoUrl} className="w-full h-full object-cover" />}
              </div>
              <div>
                <p className="font-semibold">{videoFile?.name || 'Video'}</p>
                <p className="text-sm text-emerald-400 mt-1">Ready to export</p>
              </div>
            </div>
          </div>

          {/* Format */}
          <h3 className="text-lg font-semibold mb-3 text-slate-300">Format</h3>
          <div className="grid grid-cols-3 gap-3 mb-6">
            {['mp4', 'webm', 'mov'].map((format) => (
              <button
                key={format}
                onClick={() => setExportFormat(format)}
                className={`py-4 px-4 rounded-xl font-semibold transition-all ${
                  exportFormat === format
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                    : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700/60 border border-slate-700/50'
                }`}
              >
                {format.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Quality */}
          <h3 className="text-lg font-semibold mb-3 text-slate-300">Quality</h3>
          <div className="grid grid-cols-4 gap-3 mb-6">
            {[
              { id: 'low', label: '480p', sub: 'Fast' },
              { id: 'medium', label: '720p', sub: 'Good' },
              { id: 'high', label: '1080p', sub: 'Best' },
              { id: 'ultra', label: '4K', sub: 'Ultra' },
            ].map((q) => (
              <button
                key={q.id}
                onClick={() => setExportQuality(q.id)}
                className={`py-3 px-2 rounded-xl transition-all ${
                  exportQuality === q.id
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                    : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700/60 border border-slate-700/50'
                }`}
              >
                <div className="font-semibold text-sm">{q.label}</div>
                <div className={`text-xs ${exportQuality === q.id ? 'text-emerald-200' : 'text-slate-500'}`}>{q.sub}</div>
              </button>
            ))}
          </div>

          {/* Location */}
          <h3 className="text-lg font-semibold mb-3 text-slate-300">Export To</h3>
          <div className="grid grid-cols-2 gap-3 mb-6">
            <button
              onClick={() => setExportLocation('local')}
              className={`flex items-center justify-center gap-3 py-4 px-4 rounded-xl transition-all ${
                exportLocation === 'local'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                  : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700/60 border border-slate-700/50'
              }`}
            >
              <FolderIcon />
              <span className="font-semibold">Device</span>
            </button>
            <button
              onClick={() => setExportLocation('cloud')}
              className={`flex items-center justify-center gap-3 py-4 px-4 rounded-xl transition-all ${
                exportLocation === 'cloud'
                  ? 'bg-gradient-to-r from-sky-500 to-blue-500 text-white shadow-lg shadow-sky-500/30'
                  : 'bg-slate-800/60 text-slate-300 hover:bg-slate-700/60 border border-slate-700/50'
              }`}
            >
              <CloudIcon />
              <span className="font-semibold">Cloud</span>
            </button>
          </div>

          {/* Presets */}
          <h3 className="text-lg font-semibold mb-3 text-slate-300">Quick Presets</h3>
          <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
            {['YouTube', 'TikTok', 'Instagram', 'Twitter'].map((preset) => (
              <button
                key={preset}
                onClick={() => applyPreset(preset.toLowerCase())}
                className="bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700/50 text-white py-2 px-5 rounded-full text-sm font-medium whitespace-nowrap transition-all hover:border-sky-500/50"
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Progress */}
          {exporting && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">Exporting...</span>
                <span className="text-sm text-emerald-400 font-medium">{exportProgress}%</span>
              </div>
              <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-300"
                  style={{ width: `${exportProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Export Button */}
          <button
            onClick={startExport}
            disabled={exporting}
            className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:opacity-50 text-white font-semibold py-4 rounded-2xl transition-all shadow-xl shadow-emerald-500/30"
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
