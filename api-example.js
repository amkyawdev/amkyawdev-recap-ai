/**
 * Frontend Integration Examples for OpenRouter API
 * These functions can be used in React, Next.js, or any JavaScript frontend
 */

// ============================================
// Configuration
// ============================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

// ============================================
// API Response Types
// ============================================

/**
 * @typedef {Object} OpenRouterResponse
 * @property {boolean} success
 * @property {string} [error]
 * @property {string} [content]
 * @property {object} [usage]
 */

// ============================================
// Generic API Caller
// ============================================

async function callOpenRouter(endpoint, payload) {
  const response = await fetch(`${API_BASE}/api/openrouter/${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();

  if (!response.ok || !data.success) {
    throw new Error(data.error || 'API request failed');
  }

  return data;
}

// ============================================
// AI Recap Functions
// ============================================

/**
 * Generate a video recap script from transcript
 * 
 * @param {Object} params
 * @param {string} params.transcript - Video transcript text
 * @param {number} [params.durationMinutes=5] - Target duration in minutes
 * @param {string} [params.style='engaging'] - Script style (engaging, formal, casual, technical)
 * @param {string} [params.targetAudience='general'] - Target audience
 * @returns {Promise<{script: string}>}
 */
async function generateRecapScript({ transcript, durationMinutes = 5, style = 'engaging', targetAudience = 'general' }) {
  return callOpenRouter('recap', {
    transcript,
    duration_minutes: durationMinutes,
    style,
    target_audience: targetAudience,
  });
}

/**
 * Summarize long content
 * 
 * @param {Object} params
 * @param {string} params.text - Text to summarize
 * @param {number} [params.maxSentences=5] - Max sentences in summary
 * @returns {Promise<{summary: string}>}
 */
async function summarizeContent({ text, maxSentences = 5 }) {
  return callOpenRouter('summarize', {
    text,
    max_sentences: maxSentences,
  });
}

/**
 * Generate thumbnail caption
 * 
 * @param {Object} params
 * @param {string} params.topic - Video topic
 * @param {string} [params.style='bold'] - Caption style (bold, mysterious, exciting, question)
 * @returns {Promise<{caption: string}>}
 */
async function generateThumbnailCaption({ topic, style = 'bold' }) {
  return callOpenRouter('thumbnail', {
    topic,
    style,
  });
}

/**
 * Extract key topics from text
 * 
 * @param {Object} params
 * @param {string} params.text - Text to analyze
 * @param {number} [params.numTopics=5] - Number of topics to extract
 * @returns {Promise<{topics: string[]}>}
 */
async function extractKeyTopics({ text, numTopics = 5 }) {
  return callOpenRouter('topics', {
    text,
    num_topics: numTopics,
  });
}

/**
 * Generate hashtags for video
 * 
 * @param {Object} params
 * @param {string} params.content - Video content/topic
 * @param {number} [params.numHashtags=10] - Number of hashtags
 * @returns {Promise<{hashtags: string[]}>}
 */
async function generateHashtags({ content, numHashtags = 10 }) {
  return callOpenRouter('hashtags', {
    content,
    num_hashtags: numHashtags,
  });
}

/**
 * General chat with AI model
 * 
 * @param {Object} params
 * @param {Array<{role: string, content: string}>} params.messages - Chat messages
 * @param {string} [params.model='anthropic/claude-3.5-sonnet'] - Model to use
 * @param {number} [params.temperature=0.7] - Sampling temperature
 * @param {number} [params.maxTokens] - Max tokens to generate
 * @returns {Promise<OpenRouterResponse>}
 */
async function chatWithAI({ messages, model = 'anthropic/claude-3.5-sonnet', temperature = 0.7, maxTokens }) {
  return callOpenRouter('chat', {
    messages,
    model,
    temperature,
    max_tokens: maxTokens,
  });
}

// ============================================
// React Hook Example
// ============================================

/**
 * React Hook for AI Recap Generation
 * 
 * Usage:
 * ```jsx
 * import { useAIRecap } from './api-client';
 * 
 * function RecapGenerator() {
 *   const { generate, loading, error, script } = useAIRecap();
 * 
 *   const handleGenerate = async () => {
 *     const result = await generate({
 *       transcript: "...",
 *       durationMinutes: 5,
 *       style: "engaging"
 *     });
 *     console.log(result.script);
 *   };
 * 
 *   return <button onClick={handleGenerate}>Generate Recap</button>;
 * }
 * ```
 */
function useAIRecap() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [script, setScript] = React.useState(null);

  const generate = async (params) => {
    setLoading(true);
    setError(null);
    try {
      const result = await generateRecapScript(params);
      setScript(result.script);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { generate, loading, error, script };
}

// ============================================
// Export all functions
// ============================================

export {
  generateRecapScript,
  summarizeContent,
  generateThumbnailCaption,
  extractKeyTopics,
  generateHashtags,
  chatWithAI,
  useAIRecap,
};
