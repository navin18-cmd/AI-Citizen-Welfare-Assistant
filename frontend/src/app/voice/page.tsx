'use client'
import { useSearchParams, useRouter } from 'next/navigation'
import { useState } from 'react'
import { Suspense } from 'react'
import VoiceRecorder from '@/components/VoiceRecorder'
import ProcessingOverlay from '@/components/ProcessingOverlay'
import Link from 'next/link'

function VoicePageInner() {
  const params = useSearchParams()
  const lang = params.get('lang') || 'en'
  const router = useRouter()
  const [isProcessing, setIsProcessing] = useState(false)
  const [step, setStep] = useState(0)

  const handleResult = (data: any) => {
    sessionStorage.setItem('welfare_result', JSON.stringify(data))
    setIsProcessing(true)
    setStep(0)
    setTimeout(() => setStep(1), 500)
    setTimeout(() => setStep(2), 1000)
    setTimeout(() => {
      router.push(`/results?lang=${lang}`)
    }, 1700)
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-red-50 to-white px-4 py-10">
      {isProcessing && (
        <ProcessingOverlay currentStep={step} />
      )}
      <div className="max-w-xl mx-auto">
        <Link href="/" className="text-blue-600 text-sm mb-6 inline-block">← Back</Link>
        <h1 className="text-3xl font-extrabold text-center text-gray-800 mb-2">🎤 Voice Input</h1>
        <p className="text-center text-gray-500 mb-8">
          Speak your details — name, occupation, income, state
        </p>
        <VoiceRecorder language={lang} onResult={handleResult} />

        {/* Demo hint */}
        <div className="mt-6 card bg-yellow-50 border-yellow-200">
          <p className="text-sm text-yellow-800 font-medium mb-2">💡 Demo tip — try saying:</p>
          <p className="text-sm text-yellow-700 italic">
            "I am a construction worker earning 10000 rupees per month. I live in Tamil Nadu."
          </p>
        </div>
      </div>
    </main>
  )
}

export default function VoicePage() {
  return (
    <Suspense>
      <VoicePageInner />
    </Suspense>
  )
}
