'use client'

interface Props {
  score?: number
  confidence?: 'High' | 'Medium' | 'Low'
}

export default function EligibilityScore({ score = 87, confidence = 'High' }: Props) {
  const ring = score > 90 ? 'text-green-500' : score >= 70 ? 'text-orange-500' : 'text-red-500'
  const confColor =
    confidence === 'High'
      ? 'bg-green-100 text-green-700'
      : confidence === 'Medium'
      ? 'bg-yellow-100 text-yellow-700'
      : 'bg-red-100 text-red-700'

  const radius = 40
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="card mb-8">
      <div className="flex flex-col sm:flex-row items-center gap-6">
        {/* Circular score ring */}
        <div className="relative w-28 h-28 shrink-0">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="8" />
            <circle
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className={ring}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-2xl font-extrabold ${ring}`}>{score}%</span>
          </div>
        </div>

        {/* Text section */}
        <div className="flex-1 text-center sm:text-left">
          <h3 className="text-lg font-extrabold text-gray-800">AI Eligibility Score</h3>
          <div className="flex items-center gap-2 mt-1 justify-center sm:justify-start">
            <span className="text-sm text-gray-500">Confidence Level:</span>
            <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${confColor}`}>
              {confidence}
            </span>
          </div>

          {/* Explanation box */}
          <div className="mt-3 bg-blue-50 border border-blue-200 rounded-xl px-4 py-2.5 text-xs text-blue-700 leading-relaxed">
            Score calculated using occupation match, income eligibility, age requirement, and state availability.
          </div>
        </div>
      </div>
    </div>
  )
}
