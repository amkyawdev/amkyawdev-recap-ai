import { useState, useEffect } from 'react';

interface LoadingScreenProps {
  onComplete?: () => void;
  minDuration?: number;
}

export default function LoadingScreen({ onComplete, minDuration = 2500 }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('Initializing...');

  useEffect(() => {
    const statusMessages = [
      'Initializing...',
      'Loading AI models...',
      'Preparing video engine...',
      'Connecting to GPU...',
      'Almost ready...',
    ];

    let currentIndex = 0;
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + Math.random() * 15 + 5;
      });
    }, 200);

    const statusInterval = setInterval(() => {
      currentIndex = (currentIndex + 1) % statusMessages.length;
      setStatusText(statusMessages[currentIndex]);
    }, 500);

    const completeTimer = setTimeout(() => {
      clearInterval(progressInterval);
      clearInterval(statusInterval);
      setProgress(100);
      setStatusText('Ready!');
      setTimeout(() => {
        onComplete?.();
      }, 400);
    }, minDuration);

    return () => {
      clearInterval(progressInterval);
      clearInterval(statusInterval);
      clearTimeout(completeTimer);
    };
  }, [minDuration, onComplete]);

  return (
    <div className="fixed inset-0 z-50 bg-gradient-to-br from-slate-950 via-slate-900 to-violet-950 flex flex-col items-center justify-center">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-fuchsia-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-500" />
      </div>

      {/* Logo */}
      <div className="relative z-10 mb-8">
        <div className="relative">
          {/* Outer ring */}
          <div className="w-28 h-28 rounded-full border-2 border-violet-500/30 animate-spin" style={{ animationDuration: '3s' }}>
            <div className="w-full h-full rounded-full border-2 border-transparent border-t-fuchsia-500" />
          </div>
          {/* Inner ring */}
          <div className="absolute inset-2 w-24 h-24 rounded-full border-2 border-fuchsia-500/30 animate-spin" style={{ animationDuration: '2s', animationDirection: 'reverse' }}>
            <div className="w-full h-full rounded-full border-2 border-transparent border-t-violet-500" />
          </div>
          {/* Center icon */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-2xl shadow-violet-500/50">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="28" 
                height="28" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="white" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className="animate-pulse"
              >
                <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
                <path d="M5 3v4"/>
                <path d="M19 17v4"/>
                <path d="M3 5h4"/>
                <path d="M17 19h4"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* App name */}
      <h1 className="relative z-10 text-4xl font-bold mb-2">
        <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-fuchsia-400 bg-clip-text text-transparent">
          Recap AI
        </span>
      </h1>
      <p className="relative z-10 text-slate-400 text-sm mb-12">Video Recap Generator</p>

      {/* Progress bar */}
      <div className="relative z-10 w-72 mb-4">
        <div className="h-1.5 bg-slate-800/50 rounded-full overflow-hidden backdrop-blur-sm border border-slate-700/30">
          <div 
            className="h-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      </div>

      {/* Status text */}
      <p className="relative z-10 text-slate-500 text-sm animate-pulse">{statusText}</p>

      {/* GPU indicator */}
      <div className="relative z-10 mt-8 flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/30 backdrop-blur-sm border border-slate-700/30">
        <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-xs text-slate-400">GPU Accelerated</span>
      </div>

      {/* Version */}
      <p className="absolute bottom-6 text-slate-600 text-xs">v1.0.0</p>
    </div>
  );
}
