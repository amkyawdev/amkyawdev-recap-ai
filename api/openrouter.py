"""
OpenRouter API Integration for Vercel Serverless Functions
Supports multiple AI models for video recap generation
"""

import os
import json
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Model(Enum):
    """Available OpenRouter models"""
    # Best for overall tasks
    CLAUDE_HAIKU = "anthropic/claude-3-haiku"
    CLAUDE_SONNET = "anthropic/claude-3.5-sonnet"
    
    # OpenAI models
    GPT4_O = "openai/gpt-4o"
    GPT4_O_MINI = "openai/gpt-4o-mini"
    GPT35_TURBO = "openai/gpt-3.5-turbo"
    
    # Open Source models
    LLAMA_3_8B = "meta-llama/llama-3-8b-instruct"
    LLAMA_3_70B = "meta-llama/llama-3-70b-instruct"
    MISTRAL_7B = "mistralai/mistral-7b-instruct"
    GEMINI_PRO = "google/gemini-pro"
    
    # Image models (for thumbnails/previews)
    SDXL = "stabilityai/stable-diffusion-xl-base-1.0"
    DALL_E_3 = "openai/dall-e-3"


@dataclass
class Message:
    """Chat message structure"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class OpenRouterResponse:
    """OpenRouter API response"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    raw_response: Dict[str, Any]


class OpenRouterClient:
    """OpenRouter API client for Vercel serverless functions"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: OpenRouter API key. Falls back to OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
    
    def _make_request(
        self,
        messages: List[Message],
        model: str = Model.CLAUDE_SONNET.value,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        extra_headers: Optional[Dict[str, str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make request to OpenRouter API"""
        import urllib.request
        import urllib.error
        
        url = f"{self.BASE_URL}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.environ.get("VERCEL_URL", "https://recap-ai.vercel.app"),
            "X-Title": "Recap AI Video Editor",
        }
        
        if extra_headers:
            headers.update(extra_headers)
        
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        if extra_body:
            payload.update(extra_body)
        
        data = json.dumps(payload).encode("utf-8")
        
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise Exception(f"OpenRouter API Error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network Error: {e.reason}")
    
    def chat(
        self,
        messages: List[Message],
        model: str = Model.CLAUDE_SONNET.value,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> OpenRouterResponse:
        """
        Send chat completion request
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            OpenRouterResponse object
        """
        response_data = self._make_request(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return OpenRouterResponse(
            content=response_data["choices"][0]["message"]["content"],
            model=response_data["model"],
            usage={
                "prompt_tokens": response_data["usage"]["prompt_tokens"],
                "completion_tokens": response_data["usage"]["completion_tokens"],
                "total_tokens": response_data["usage"]["total_tokens"],
            },
            finish_reason=response_data["choices"][0]["finish_reason"],
            raw_response=response_data,
        )
    
    def generate_recap_script(
        self,
        transcript: str,
        duration_minutes: float,
        style: str = "engaging",
        target_audience: str = "general",
    ) -> str:
        """
        Generate a video recap script from transcript
        
        Args:
            transcript: Video transcript text
            duration_minutes: Target video duration in minutes
            style: Script style (engaging, formal, casual, technical)
            target_audience: Target audience description
            
        Returns:
            Generated recap script
        """
        system_prompt = f"""You are a professional video script writer specializing in creating 
engaging recap videos. Create a compelling script that:
- Captures the key points and highlights
- Maintains viewer engagement throughout
- Is suitable for a {duration_minutes} minute video
- Targets {target_audience} audience
- Uses {style} tone

Format the script with clear sections and timing cues."""

        user_prompt = f"""Based on the following transcript, create a video recap script:

---
{transcript}
---

Please create a well-structured script with:
1. An attention-grabbing introduction
2. Main highlights organized logically
3. Key takeaways
4. A memorable conclusion with call-to-action

Keep it engaging and concise for a {duration_minutes} minute video."""

        response = self.chat(
            messages=[
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt),
            ],
            model=Model.CLAUDE_SONNET.value,
            temperature=0.7,
        )
        
        return response.content
    
    def summarize_content(
        self,
        text: str,
        max_sentences: int = 5,
    ) -> str:
        """
        Summarize long content
        
        Args:
            text: Text to summarize
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Summary text
        """
        response = self.chat(
            messages=[
                Message(
                    role="system",
                    content="You are a helpful summarization assistant. Create concise, accurate summaries."
                ),
                Message(
                    role="user",
                    content=f"Summarize the following text in approximately {max_sentences} sentences:\n\n{text}"
                ),
            ],
            model=Model.GPT4_O_MINI.value,
            temperature=0.3,
        )
        
        return response.content
    
    def generate_thumbnail_caption(
        self,
        video_topic: str,
        style: str = "bold",
    ) -> str:
        """
        Generate catchy caption for video thumbnail
        
        Args:
            video_topic: Main topic/theme of the video
            style: Caption style (bold, mysterious, exciting, question)
            
        Returns:
            Generated caption
        """
        response = self.chat(
            messages=[
                Message(
                    role="system",
                    content="You are a creative copywriter specializing in viral thumbnails. Create attention-grabbing, concise captions."
                ),
                Message(
                    role="user",
                    content=f"Generate a {style} thumbnail caption for a video about: {video_topic}\n\nKeep it short (5-10 words max), impactful, and suitable for a thumbnail."
                ),
            ],
            model=Model.CLAUDE_HAIKU.value,
            temperature=0.9,
        )
        
        return response.content
    
    def extract_key_topics(
        self,
        text: str,
        num_topics: int = 5,
    ) -> List[str]:
        """
        Extract key topics from text
        
        Args:
            text: Text to analyze
            num_topics: Number of topics to extract
            
        Returns:
            List of key topics
        """
        response = self.chat(
            messages=[
                Message(
                    role="system",
                    content="You are an expert at analyzing content and identifying key topics. Return only a JSON array of topics."
                ),
                Message(
                    role="user",
                    content=f"Extract {num_topics} key topics from the following text. Return ONLY a JSON array of topic strings, nothing else:\n\n{text}"
                ),
            ],
            model=Model.GPT4_O_MINI.value,
            temperature=0.3,
        )
        
        # Try to extract JSON array from response
        content = response.content.strip()
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: split by newlines or commas
        topics = re.split(r'[\n,]+', content)
        return [t.strip().strip('"-') for t in topics if t.strip()][:num_topics]
    
    def generate_hashtags(
        self,
        content: str,
        num_hashtags: int = 10,
    ) -> List[str]:
        """
        Generate relevant hashtags for video
        
        Args:
            content: Video content/topic description
            num_hashtags: Number of hashtags to generate
            
        Returns:
            List of hashtags
        """
        response = self.chat(
            messages=[
                Message(
                    role="system",
                    content="You are a social media expert. Generate relevant, popular hashtags."
                ),
                Message(
                    role="user",
                    content=f"Generate {num_hashtags} relevant hashtags for this video content. Return ONLY a JSON array of hashtags (with # symbol):\n\n{content}"
                ),
            ],
            model=Model.GPT4_O_MINI.value,
            temperature=0.7,
        )
        
        content = response.content.strip()
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback
        hashtags = re.findall(r'#\w+', content)
        return hashtags[:num_hashtags]


# Vercel Serverless Function Handler
def handler(request):
    """
    Vercel serverless function handler
    
    Environment Variables Required:
    - OPENROUTER_API_KEY: Your OpenRouter API key
    - VERCEL_URL: Your deployment URL (auto-set by Vercel)
    
    API Endpoints:
    - POST /api/openrouter - General chat
    - POST /api/openrouter/recap - Generate recap script
    - POST /api/openrouter/summarize - Summarize content
    - POST /api/openrouter/thumbnail - Generate thumbnail caption
    - POST /api/openrouter/topics - Extract key topics
    - POST /api/openrouter/hashtags - Generate hashtags
    """
    from urllib.parse import urlparse
    
    # Parse request
    parsed_path = urlparse(request.url.path)
    path = parsed_path.path.replace("/api/openrouter", "").strip("/")
    
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json",
    }
    
    # Handle preflight
    if request.method == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}
    
    # Initialize client
    try:
        client = OpenRouterClient()
    except ValueError as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }
    
    try:
        # Parse body
        if request.method in ["POST", "PUT"]:
            body = json.loads(request.body or "{}")
        else:
            body = {}
        
        # Route to appropriate handler
        if path == "recap":
            result = handle_recap(client, body)
        elif path == "summarize":
            result = handle_summarize(client, body)
        elif path == "thumbnail":
            result = handle_thumbnail(client, body)
        elif path == "topics":
            result = handle_topics(client, body)
        elif path == "hashtags":
            result = handle_hashtags(client, body)
        elif path == "" or path == "chat":
            result = handle_chat(client, body)
        else:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({"error": "Endpoint not found"}),
            }
        
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(result),
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}),
        }


def handle_recap(client: OpenRouterClient, body: dict) -> dict:
    """Handle recap script generation"""
    transcript = body.get("transcript", "")
    duration = body.get("duration_minutes", 5)
    style = body.get("style", "engaging")
    audience = body.get("target_audience", "general")
    
    if not transcript:
        raise ValueError("transcript is required")
    
    script = client.generate_recap_script(
        transcript=transcript,
        duration_minutes=duration,
        style=style,
        target_audience=audience,
    )
    
    return {"success": True, "script": script}


def handle_summarize(client: OpenRouterClient, body: dict) -> dict:
    """Handle content summarization"""
    text = body.get("text", "")
    max_sentences = body.get("max_sentences", 5)
    
    if not text:
        raise ValueError("text is required")
    
    summary = client.summarize_content(text, max_sentences)
    
    return {"success": True, "summary": summary}


def handle_thumbnail(client: OpenRouterClient, body: dict) -> dict:
    """Handle thumbnail caption generation"""
    topic = body.get("topic", "")
    style = body.get("style", "bold")
    
    if not topic:
        raise ValueError("topic is required")
    
    caption = client.generate_thumbnail_caption(topic, style)
    
    return {"success": True, "caption": caption}


def handle_topics(client: OpenRouterClient, body: dict) -> dict:
    """Handle key topics extraction"""
    text = body.get("text", "")
    num_topics = body.get("num_topics", 5)
    
    if not text:
        raise ValueError("text is required")
    
    topics = client.extract_key_topics(text, num_topics)
    
    return {"success": True, "topics": topics}


def handle_hashtags(client: OpenRouterClient, body: dict) -> dict:
    """Handle hashtag generation"""
    content = body.get("content", "")
    num_hashtags = body.get("num_hashtags", 10)
    
    if not content:
        raise ValueError("content is required")
    
    hashtags = client.generate_hashtags(content, num_hashtags)
    
    return {"success": True, "hashtags": hashtags}


def handle_chat(client: OpenRouterClient, body: dict) -> dict:
    """Handle general chat"""
    messages_data = body.get("messages", [])
    model = body.get("model", Model.CLAUDE_SONNET.value)
    temperature = body.get("temperature", 0.7)
    max_tokens = body.get("max_tokens")
    
    if not messages_data:
        raise ValueError("messages array is required")
    
    messages = [Message(**m) for m in messages_data]
    
    response = client.chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return {
        "success": True,
        "content": response.content,
        "model": response.model,
        "usage": response.usage,
        "finish_reason": response.finish_reason,
    }


# For local testing
if __name__ == "__main__":
    import sys
    
    api_key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        print("Please provide OpenRouter API key")
        sys.exit(1)
    
    client = OpenRouterClient(api_key)
    
    # Test chat
    response = client.chat([
        Message(role="user", content="Say hello in 3 words!")
    ])
    print(f"Chat Response: {response.content}")
    print(f"Usage: {response.usage}")
