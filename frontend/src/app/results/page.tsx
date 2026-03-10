'use client'
import { useEffect, useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import SchemeCard from '@/components/SchemeCard'
import EligibilityScore from '@/components/EligibilityScore'
import { api } from '@/services/api'

// Demo fallback data when no session / backend
const DEMO_RESULT = {
  transcript: "I am a construction worker earning 10000 rupees per month. I live in Tamil Nadu.",
  extracted_profile: { name: "Ravi Kumar", age: 34, occupation: "construction worker", income: 10000, state: "Tamil Nadu" },
  eligible_schemes: [
    { id:1, name:"Ayushman Bharat", short_name:"Ayushman Bharat", category:"Healthcare", benefit_value:500000, benefit_description:"Health cover of ₹5,00,000 per family", icon:"🏥", eligibility_score:90, required_documents:["Aadhaar Card","Ration Card"], apply_link:"https://pmjay.gov.in", description:"World's largest health insurance program." },
    { id:2, name:"e-Shram Card", short_name:"e-Shram", category:"Labour", benefit_value:200000, benefit_description:"Accident insurance ₹2,00,000 + social security", icon:"👷", eligibility_score:85, required_documents:["Aadhaar Card","Bank Account"], apply_link:"https://eshram.gov.in", description:"National database for unorganised workers." },
    { id:3, name:"PM Shram Yogi Mandhan", short_name:"PM-SYM", category:"Pension", benefit_value:36000, benefit_description:"Monthly pension ₹3,000 after age 60", icon:"🏦", eligibility_score:80, required_documents:["Aadhaar Card","Savings Account"], apply_link:"https://maandhan.in", description:"Pension scheme for unorganised workers." },
    { id:4, name:"PM Awas Yojana", short_name:"PMAY-G", category:"Housing", benefit_value:120000, benefit_description:"₹1,20,000 for pucca house construction", icon:"🏠", eligibility_score:75, required_documents:["Aadhaar Card","BPL Certificate"], apply_link:"https://pmayg.nic.in", description:"Housing for all rural poor." },
  ],
  total_schemes: 4,
  total_benefit_value: 856000,
  message: "You qualify for 4 government welfare schemes worth ₹8,56,000"
}

function ResultsInner() {
  const params = useSearchParams()
  const lang = params.get('lang') || 'en'
  const isDemo = params.get('demo') === 'true'

  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isDemo) {
      setResult(DEMO_RESULT)
      setLoading(false)
      return
    }
    try {
      const saved = sessionStorage.getItem('welfare_result')
      if (saved) {
        setResult(JSON.parse(saved))
      } else {
        setResult(DEMO_RESULT)
      }
    } catch {
      setResult(DEMO_RESULT)
    }
    setLoading(false)
  }, [isDemo])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center text-gray-500 text-xl">
      Calculating your eligible schemes...
    </div>
  )

  const r = result || DEMO_RESULT
  const schemes = r.eligible_schemes || []
  const total = r.total_benefit_value || 0
  const occupation = (r.extracted_profile?.occupation || '').toLowerCase()
  const transcriptText = (r.transcript || '').toLowerCase()

  // Demo score mapping for the three sample profiles.
  const demoScoreByOccupation: Record<string, number> = {
    'construction worker': 80,
    'domestic worker': 86,
    farmer: 91,
  }

  const detectedDemoOccupation =
    occupation.includes('farmer') || transcriptText.includes('farmer')
      ? 'farmer'
      : occupation.includes('domestic') || transcriptText.includes('domestic') || transcriptText.includes('maid')
      ? 'domestic worker'
      : occupation.includes('construction') || transcriptText.includes('construction')
      ? 'construction worker'
      : occupation

  const averageSchemeScore = schemes.length
    ? Math.round(schemes.reduce((sum: number, s: any) => sum + (s.eligibility_score || 0), 0) / schemes.length)
    : 80

  const aiScore = demoScoreByOccupation[detectedDemoOccupation] ?? averageSchemeScore
  const confidence = aiScore >= 85 ? 'High' : aiScore >= 70 ? 'Medium' : 'Low'

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white px-4 py-10">
      <div className="max-w-4xl mx-auto">
        <Link href="/" className="text-blue-600 text-sm mb-6 inline-block">← Back to Home</Link>

        {/* Big result banner */}
        <div className="card bg-gradient-to-r from-blue-700 to-blue-900 text-white text-center mb-8 py-10">
          <div className="text-5xl mb-4">✅</div>
          <h1 className="text-2xl md:text-3xl font-extrabold mb-2">
            You qualify for <span className="text-yellow-300">{schemes.length} government welfare schemes</span>
          </h1>
          <p className="text-xl mt-3 text-blue-100">
            Total benefits worth{' '}
            <span className="text-green-300 font-extrabold text-2xl">
              ₹{total.toLocaleString('en-IN')}
            </span>
          </p>
          {r.extracted_profile?.occupation && (
            <p className="mt-4 text-sm text-blue-200">
              Profile: {r.extracted_profile.occupation} · ₹{r.extracted_profile.income?.toLocaleString('en-IN')}/mo · {r.extracted_profile.state}
            </p>
          )}
        </div>

        {/* AI Eligibility Score */}
        <EligibilityScore score={aiScore} confidence={confidence} />

        {/* Transcript if from voice */}
        {r.transcript && !isDemo && (
          <div className="card bg-gray-50 mb-6">
            <p className="text-xs text-gray-500 mb-1">What you said:</p>
            <p className="text-gray-700 italic">"{r.transcript}"</p>
          </div>
        )}

        {/* Scheme cards */}
        <h2 className="text-xl font-bold text-gray-800 mb-4">Your Eligible Schemes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {schemes.map((scheme: any) => (
            <SchemeCard key={scheme.id} scheme={scheme} language={lang} />
          ))}
        </div>

        <div className="mt-8 text-center flex flex-col sm:flex-row gap-4 justify-center">
          <Link href={`/upload?lang=${lang}`} className="btn-secondary text-base py-3 px-6">
            📄 Upload Aadhaar to refine
          </Link>
          <Link href="/dashboard" className="btn-primary text-base py-3 px-6">
            📊 NGO Dashboard
          </Link>
        </div>
      </div>
    </main>
  )
}

export default function ResultsPage() {
  return (
    <Suspense>
      <ResultsInner />
    </Suspense>
  )
}
