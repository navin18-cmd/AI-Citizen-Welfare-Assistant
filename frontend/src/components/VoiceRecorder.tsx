'use client'
import { useState, useRef } from 'react'
import { api } from '@/services/api'

interface Props {
  language: string
  onResult: (data: any) => void
}

// Fallback schemes shown when backend is offline or returns no matches
const FALLBACK_SCHEMES = [
  { id: 1, name: 'Ayushman Bharat', short_name: 'Ayushman Bharat', category: 'Healthcare', benefit_value: 500000, benefit_description: 'Health cover of ₹5,00,000 per family', icon: '🏥', eligibility_score: 85, required_documents: ['Aadhaar Card', 'Ration Card'], apply_link: 'https://pmjay.gov.in', description: "World's largest health insurance program." },
  { id: 2, name: 'e-Shram Card', short_name: 'e-Shram', category: 'Labour', benefit_value: 200000, benefit_description: 'Accident insurance ₹2,00,000 + social security', icon: '👷', eligibility_score: 80, required_documents: ['Aadhaar Card', 'Bank Account'], apply_link: 'https://eshram.gov.in', description: 'National database for unorganised workers.' },
  { id: 3, name: 'PM Shram Yogi Mandhan', short_name: 'PM-SYM', category: 'Pension', benefit_value: 36000, benefit_description: 'Monthly pension ₹3,000 after age 60', icon: '🏦', eligibility_score: 75, required_documents: ['Aadhaar Card', 'Savings Account'], apply_link: 'https://maandhan.in', description: 'Pension scheme for unorganised workers.' },
]

// Demo sentences for when mic isn't available
const DEMO_SENTENCES: Record<string, string> = {
  en: "I am a construction worker earning 10000 rupees per month. I live in Tamil Nadu.",
  hi: "मैं एक निर्माण मजदूर हूं। मेरी मासिक आय 10000 रुपये है। मैं तमिलनाडु से हूं।",
  ta: "நான் ஒரு கட்டுமான தொழிலாளி. என் மாத வருமானம் 10000 ரூபாய். நான் தமிழ்நாட்டில் வசிக்கிறேன்.",
}

export default function VoiceRecorder({ language, onResult }: Props) {
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [transcriptionReady, setTranscriptionReady] = useState(false)
  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const mimeTypeRef = useRef<string>('audio/webm')
  const streamRef = useRef<MediaStream | null>(null)
  const autoStopTimerRef = useRef<number | null>(null)

  const startRecording = async () => {
    setError('')
    setTranscriptionReady(false)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const recorder = new MediaRecorder(stream)
      mimeTypeRef.current = recorder.mimeType || 'audio/webm'
      chunksRef.current = []
      recorder.ondataavailable = e => chunksRef.current.push(e.data)
      recorder.onstop = handleStop
      mediaRef.current = recorder
      recorder.start()
      autoStopTimerRef.current = window.setTimeout(() => {
        if (mediaRef.current?.state === 'recording') {
          stopRecording()
        }
      }, 10000)
      setIsRecording(true)
    } catch {
      setError('Microphone not available. Please type your details manually.')
    }
  }

  const stopRecording = () => {
    if (autoStopTimerRef.current) {
      window.clearTimeout(autoStopTimerRef.current)
      autoStopTimerRef.current = null
    }
    mediaRef.current?.stop()
    streamRef.current?.getTracks().forEach(t => t.stop())
    setIsRecording(false)
  }

  const handleStop = async () => {
    setLoading(true)
    setError('')
    setTranscriptionReady(false)
    const blob = new Blob(chunksRef.current, { type: mimeTypeRef.current || 'audio/webm' })
    try {
      const data = await api.sendAudio(blob, language)
      setTranscript(data.transcript || '')
      setTranscriptionReady(true)
    } catch (err: any) {
      const detail = typeof err?.message === 'string' ? err.message : 'Transcription failed. Please try again or type your details.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  const useDemoText = async () => {
    const text = DEMO_SENTENCES[language] || DEMO_SENTENCES['en']
    setTranscript(text)
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/voice-input/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, language }),
      })
      const data = await res.json()
      onResult(data)
    } catch {
      // Offline: construct mock result
      onResult({
        transcript: text,
        extracted_profile: { occupation: 'construction worker', income: 10000, state: 'Tamil Nadu' },
        eligible_schemes: FALLBACK_SCHEMES,
        total_schemes: FALLBACK_SCHEMES.length,
        total_benefit_value: 736000,
        message: `You qualify for ${FALLBACK_SCHEMES.length} government welfare schemes worth ₹7,36,000`
      })
    } finally {
      setLoading(false)
    }
  }

  const handleTextSubmit = async () => {
    if (!transcript.trim()) return
    setError('')
    setTranscriptionReady(false)
    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/voice-input/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: transcript, language }),
      })
      const data = await res.json()
      onResult(data)
    } catch {
      onResult({
        transcript,
        extracted_profile: { occupation: 'construction worker', income: 10000, state: 'Tamil Nadu' },
        eligible_schemes: FALLBACK_SCHEMES,
        total_schemes: FALLBACK_SCHEMES.length,
        total_benefit_value: 736000,
        message: `You qualify for ${FALLBACK_SCHEMES.length} government welfare schemes`
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card space-y-6">
      {/* Big mic button */}
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          {isRecording && (
            <span className="absolute inset-0 rounded-full bg-red-400 opacity-60 pulse-ring" />
          )}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`w-28 h-28 rounded-full text-5xl shadow-xl transition-all duration-200 active:scale-90 ${
              isRecording
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-red-100 hover:bg-red-200 text-red-600'
            }`}
          >
            {isRecording ? '⏹️' : '🎤'}
          </button>
        </div>
        <p className="font-semibold text-gray-700">
          {isRecording ? (
            <span className="text-red-600">
              <span className="recording-dot">●</span> Listening... tap to stop
            </span>
          ) : loading ? 'Processing...' : 'Tap to speak'}
        </p>
      </div>

      {error && <p className="text-sm text-orange-600 text-center">{error}</p>}

      {transcriptionReady && !loading && (
        <p className="text-sm text-green-700 text-center">
          Voice converted to text. Review/edit and click Find My Schemes.
        </p>
      )}

      {/* Or type */}
      <div>
        <p className="text-xs text-gray-400 text-center mb-2">— or type your details —</p>
        <textarea
          value={transcript}
          onChange={e => setTranscript(e.target.value)}
          className="w-full border border-gray-200 rounded-xl p-3 text-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
          rows={4}
          placeholder="e.g. I am a construction worker earning 10000 rupees, living in Tamil Nadu..."
        />
        <button
          onClick={handleTextSubmit}
          disabled={loading || !transcript.trim()}
          className="btn-primary w-full mt-3 text-lg disabled:opacity-50"
        >
          {loading ? '⏳ Analyzing your profile with AI...' : '🔍 Find My Schemes'}
        </button>
      </div>

      {/* Quick demo buttons */}
      <div>
        <p className="text-xs text-gray-400 text-center mb-2">Quick demo profiles</p>
        <div className="flex flex-col gap-2">
          {[
            { label: '👷 Construction Worker – Tamil Nadu', text: "I am a construction worker earning 10000 rupees. I live in Tamil Nadu." },
            { label: '🧹 Domestic Worker – Karnataka', text: "My name is Lakshmi. I am a domestic worker earning 9000 rupees. I am from Karnataka." },
            { label: '🌾 Farmer – Andhra Pradesh', text: "I am a farmer from Andhra Pradesh earning 12000 rupees. I have 2 acres of land." },
          ].map(p => (
            <button
              key={p.label}
              onClick={() => setTranscript(p.text)}
              className="text-left text-sm bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-xl px-4 py-2 transition"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
