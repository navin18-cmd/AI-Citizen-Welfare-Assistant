'use client'

interface Props {
  value: string
  onChange: (lang: string) => void
}

const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'hi', label: 'हिंदी', flag: '🇮🇳' },
  { code: 'ta', label: 'தமிழ்', flag: '🌟' },
]

export default function LanguageSelector({ value, onChange }: Props) {
  return (
    <div className="flex gap-1 bg-gray-100 rounded-xl p-1">
      {LANGUAGES.map(lang => (
        <button
          key={lang.code}
          onClick={() => onChange(lang.code)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
            value === lang.code
              ? 'bg-white shadow text-blue-700 font-bold'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          {lang.flag} {lang.label}
        </button>
      ))}
    </div>
  )
}
