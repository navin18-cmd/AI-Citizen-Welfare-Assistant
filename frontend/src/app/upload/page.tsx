'use client'
import { useSearchParams, useRouter } from 'next/navigation'
import { useState } from 'react'
import { Suspense } from 'react'
import UploadCard from '@/components/UploadCard'
import ProcessingOverlay from '@/components/ProcessingOverlay'
import Link from 'next/link'

function UploadPageInner() {
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
    <main className="min-h-screen bg-gradient-to-b from-green-50 to-white px-4 py-10">
      {isProcessing && (
        <ProcessingOverlay currentStep={step} />
      )}
      <div className="max-w-xl mx-auto">
        <Link href="/" className="text-blue-600 text-sm mb-6 inline-block">← Back</Link>
        <h1 className="text-3xl font-extrabold text-center text-gray-800 mb-2">📄 Upload Document</h1>
        <p className="text-center text-gray-500 mb-8">
          Upload your Aadhaar card or income certificate
        </p>
        <UploadCard language={lang} onResult={handleResult} />
      </div>
    </main>
  )
}

export default function UploadPage() {
  return (
    <Suspense>
      <UploadPageInner />
    </Suspense>
  )
}
