'use client'

interface Scheme {
  id: number
  name: string
  short_name?: string
  category?: string
  benefit_value?: number
  benefit_description?: string
  icon?: string
  eligibility_score?: number
  required_documents?: string[]
  apply_link?: string
  description?: string
  hindi_name?: string
  tamil_name?: string
}

interface Props {
  scheme: Scheme
  language?: string
}

const CATEGORY_COLORS: Record<string, string> = {
  Healthcare: 'bg-red-100 text-red-700',
  Labour: 'bg-blue-100 text-blue-700',
  Pension: 'bg-purple-100 text-purple-700',
  Housing: 'bg-orange-100 text-orange-700',
  Agriculture: 'bg-green-100 text-green-700',
  Fuel: 'bg-yellow-100 text-yellow-700',
  Employment: 'bg-cyan-100 text-cyan-700',
}

export default function SchemeCard({ scheme, language = 'en' }: Props) {
  const score = scheme.eligibility_score || 0
  const scoreColor = score >= 80 ? 'text-green-600' : score >= 60 ? 'text-orange-500' : 'text-red-500'
  const barColor = score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-orange-400' : 'bg-red-400'
  const catColor = CATEGORY_COLORS[scheme.category || ''] || 'bg-gray-100 text-gray-600'

  const displayName = language === 'hi' && scheme.hindi_name
    ? scheme.hindi_name
    : language === 'ta' && scheme.tamil_name
    ? scheme.tamil_name
    : scheme.name

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200 flex flex-col gap-3">
      {/* Header row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-3xl">{scheme.icon || '📋'}</span>
          <div>
            <h3 className="font-bold text-gray-800 leading-tight">{displayName}</h3>
            {scheme.category && (
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${catColor}`}>
                {scheme.category}
              </span>
            )}
          </div>
        </div>
        {score > 0 && (
          <div className="text-right shrink-0">
            <div className={`text-lg font-extrabold ${scoreColor}`}>{score}%</div>
            <div className="text-xs text-gray-400">match</div>
          </div>
        )}
      </div>

      {/* Score bar */}
      {score > 0 && (
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div className={`${barColor} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
        </div>
      )}

      {/* Benefit */}
      {scheme.benefit_value && (
        <div className="bg-green-50 rounded-xl px-4 py-2">
          <div className="text-xs text-gray-500">Benefit</div>
          <div className="text-lg font-extrabold text-green-700">
            ₹{scheme.benefit_value.toLocaleString('en-IN')}
          </div>
          <div className="text-xs text-gray-600">{scheme.benefit_description}</div>
        </div>
      )}

      {/* Description */}
      {scheme.description && (
        <p className="text-sm text-gray-600">{scheme.description}</p>
      )}

      {/* Documents */}
      {scheme.required_documents && scheme.required_documents.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 mb-1">Documents Required:</p>
          <div className="flex flex-wrap gap-1">
            {scheme.required_documents.map(doc => (
              <span key={doc} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                📎 {doc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Apply button */}
      <a
        href={scheme.apply_link || '#'}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-auto btn-primary text-sm py-2.5 px-4 bg-blue-600 hover:bg-blue-700 w-full"
      >
        Apply Now →
      </a>
    </div>
  )
}
