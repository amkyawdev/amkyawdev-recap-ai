# Recap AI 🎬

<p align="center">
  <img src="android_app/icon.png" width="120" alt="Recap AI Logo">
</p>

<p align="center">
  <strong>AI-Powered Video Recap Generator with GPU Acceleration</strong>
  <br>
  FastAPI Backend • KivyMD Android App • React Web Frontend
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB.svg" alt="React">
  <img src="https://img.shields.io/badge/CUDA-12.3-76B900.svg" alt="CUDA">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Recap** | Generate engaging video scripts from transcripts |
| 🎙️ **Speech-to-Text** | Whisper-powered transcription with 90+ languages |
| 🌐 **Translation** | Multi-language subtitle generation |
| 🎨 **AI Effects** | Background removal, auto-captions, super resolution |
| ⚡ **GPU Rendering** | NVIDIA NVENC accelerated video processing |
| 🔄 **Hybrid Rendering** | Smart on-device vs cloud decision engine |
| 📱 **Cross-Platform** | Android, Web, Desktop support |

---

## 🚀 Quick Start

### 1. Setup Environment Variables

Create `.env` file:
```bash
cp .env.example .env
```

Add your OpenRouter API key:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
```

Get your API key from: https://openrouter.ai/keys

### 2. Deploy to Vercel

```bash
npm i -g vercel
vercel
```

Set environment variable in Vercel Dashboard:
- Go to Project Settings → Environment Variables
- Add `OPENROUTER_API_KEY` with your key

## 📡 API Endpoints

Base URL: `https://your-app.vercel.app/api/openrouter`

### POST /api/openrouter/recap
Generate video recap script from transcript.

**Request:**
```json
{
  "transcript": "Video transcript text...",
  "duration_minutes": 5,
  "style": "engaging",
  "target_audience": "general"
}
```

**Response:**
```json
{
  "success": true,
  "script": "Generated recap script..."
}
```

### POST /api/openrouter/summarize
Summarize content.

**Request:**
```json
{
  "text": "Long text to summarize...",
  "max_sentences": 5
}
```

### POST /api/openrouter/thumbnail
Generate thumbnail caption.

**Request:**
```json
{
  "topic": "Video topic",
  "style": "bold"
}
```

### POST /api/openrouter/topics
Extract key topics.

**Request:**
```json
{
  "text": "Content to analyze...",
  "num_topics": 5
}
```

### POST /api/openrouter/hashtags
Generate hashtags.

**Request:**
```json
{
  "content": "Video content...",
  "num_hashtags": 10
}
```

### POST /api/openrouter/chat
General chat with AI.

**Request:**
```json
{
  "messages": [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
  ],
  "model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7
}
```

## 🤖 Available Models

| Model | ID | Best For |
|-------|-----|----------|
| Claude 3 Haiku | `anthropic/claude-3-haiku` | Fast, cost-effective |
| Claude 3.5 Sonnet | `anthropic/claude-3.5-sonnet` | Best overall |
| GPT-4o | `openai/gpt-4o` | Complex reasoning |
| GPT-4o Mini | `openai/gpt-4o-mini` | Fast, affordable |
| Llama 3 70B | `meta-llama/llama-3-70b-instruct` | Open source |
| Gemini Pro | `google/gemini-pro` | Google ecosystem |

See all models: https://openrouter.ai/models

## 📱 Frontend Integration

```javascript
// In your React/Next.js app
import {
  generateRecapScript,
  summarizeContent,
  generateThumbnailCaption,
  extractKeyTopics,
  generateHashtags
} from './api-example.js';

// Generate recap script
const result = await generateRecapScript({
  transcript: "Video transcript...",
  durationMinutes: 5,
  style: "engaging"
});
console.log(result.script);

// Summarize content
const summary = await summarizeContent({
  text: "Long content...",
  maxSentences: 3
});

// Generate hashtags
const hashtags = await generateHashtags({
  content: "Video about AI...",
  numHashtags: 10
});
```

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENROUTER_API_KEY=sk-or-v1-your-key

# Test locally
python api/openrouter.py
```

## 📁 Project Structure

```
amkyawdev-recap-ai/
│
├── 📂 backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── recap.py              # AI Recap logic
│   │   │   │   ├── voice.py              # TTS logic
│   │   │   │   ├── video_edit.py         # Video editing
│   │   │   │   ├── render.py             # GPU rendering
│   │   │   │   ├── export.py             # Hardware encoding
│   │   │   │   ├── upload.py             # S3 upload
│   │   │   │   └── hybrid.py             # Render decision
│   │   │   └── api_router.py
│   │   ├── core/
│   │   │   ├── config.py                 # Settings
│   │   │   ├── gpu_manager.py            # GPU device management
│   │   │   ├── redis.py                 # Task queue
│   │   │   └── storage.py               # S3/R2 client
│   │   └── services/
│   │       ├── whisper/                 # Speech-to-text
│   │       ├── translate/               # Translation
│   │       ├── ai_effects/              # AI-powered effects
│   │       └── render_engine/           # GPU rendering
│   ├── Dockerfile.gpu                   # NVIDIA CUDA base
│   ├── docker-compose.yml               # GPU-enabled Docker
│   └── requirements.txt
│
├── 📂 android_app/                      # KivyMD Frontend
│   ├── main.py
│   ├── buildozer.spec                  # Buildozer config
│   ├── icon.png                        # App icon
│   ├── screens/
│   │   ├── home.py, recap.py, export.py
│   │   └── editor/
│   │       ├── editor_screen.py, timeline_widget.py
│   │       ├── preview_widget.py, tools_panel.py
│   │       └── gpu_status.py
│   └── services/
│       ├── api_client.py, websocket.py
│       └── render_decision.py
│
├── 📂 web_frontend/                     # React Web
│   ├── package.json
│   └── src/
│       ├── components/
│       ├── store/
│       └── api/
│
├── 📂 infrastructure/                    # IaC
│   ├── terraform/ (AWS/GCP)
│   └── kubernetes/
│
├── 📂 api/                            # Vercel Serverless
│   ├── openrouter.py
│   └── index.js
│
├── vercel.json
├── README.md
└── .env.example
```

## 💰 Pricing

OpenRouter uses credits system. Each request costs based on model:
- Claude Haiku: ~$0.25/1M tokens
- Claude Sonnet: ~$3/1M tokens
- GPT-4o Mini: ~$0.15/1M tokens

Monitor usage at: https://openrouter.ai/credits