import { useState } from 'react'
import { generateRecap, summarizeContent, generateHashtags, type RecapRequest } from './api/client'

function App() {
  const [transcript, setTranscript] = useState('')
  const [duration, setDuration] = useState(5)
  const [style, setStyle] = useState('engaging')
  const [script, setScript] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerateRecap = async () => {
    if (!transcript) {
      setError('Please enter a transcript')
      return
    }

    setLoading(true)
    setError('')
    setScript('')

    try {
      const request: RecapRequest = {
        transcript,
        duration_minutes: duration,
        style,
        target_audience: 'general',
      }
      const result = await generateRecap(request)
      setScript(result.script)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recap')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
            Recap AI
          </h1>
          <p className="text-gray-400">AI-Powered Video Recap Generator</p>
        </header>

        <div className="grid gap-8">
          {/* Input Section */}
          <section className="bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Video Transcript</h2>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste your video transcript here..."
              className="w-full h-48 bg-gray-700 rounded-lg p-4 text-white placeholder-gray-400 resize-none focus:ring-2 focus:ring-purple-500 focus:outline-none"
            />

            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Duration (minutes)</label>
                <input
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  min={1}
                  max={60}
                  className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Style</label>
                <select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  className="w-full bg-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 focus:outline-none"
                >
                  <option value="engaging">Engaging</option>
                  <option value="formal">Formal</option>
                  <option value="casual">Casual</option>
                  <option value="technical">Technical</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerateRecap}
              disabled={loading}
              className="w-full mt-6 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all"
            >
              {loading ? 'Generating...' : 'Generate Recap Script'}
            </button>

            {error && (
              <div className="mt-4 p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200">
                {error}
              </div>
            )}
          </section>

          {/* Output Section */}
          {script && (
            <section className="bg-gray-800 rounded-xl p-6 shadow-lg">
              <h2 className="text-xl font-semibold mb-4">Generated Script</h2>
              <pre className="whitespace-pre-wrap text-gray-300 bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto">
                {script}
              </pre>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
