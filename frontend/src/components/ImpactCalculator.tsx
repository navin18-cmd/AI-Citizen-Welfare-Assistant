'use client'

const PROJECTIONS = [
  {
    icon: '👤',
    label: '1 Citizen',
    workers: 1,
    benefit: 856000,
    display: '₹8,56,000',
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
  },
  {
    icon: '👥',
    label: '1,000 Citizens',
    workers: 1000,
    benefit: 856000000,
    display: '₹85,60,00,000',
    color: 'text-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
  },
  {
    icon: '🌍',
    label: '10 Lakh Citizens',
    workers: 1000000,
    benefit: 856000000000,
    display: '₹8,560 Crore',
    color: 'text-orange-600',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
  },
]

interface Props {
  language?: string
}

export default function ImpactCalculator({ language = 'en' }: Props) {
  const title =
    language === 'hi'
      ? 'प्रभाव अनुमान'
      : language === 'ta'
      ? 'தாக்க கணிப்பு'
      : 'Impact Projection'

  const subtitle =
    language === 'hi'
      ? 'यदि यह AI प्लेटफॉर्म लाखों नागरिकों को कल्याण योजनाओं तक पहुँचने में मदद करे, तो सामाजिक प्रभाव अपार हो सकता है।'
      : language === 'ta'
      ? 'இந்த AI தளம் மில்லியன் கணக்கான குடிமக்களுக்கு நலத் திட்டங்களை அணுக உதவினால், சமூக தாக்கம் மிகப்பெரியதாக இருக்கும்.'
      : 'If this AI platform helps millions of citizens access welfare schemes, the social impact can be enormous.'

  const benefitLabel =
    language === 'hi' ? 'लाभ राशि' : language === 'ta' ? 'நலன் மதிப்பு' : 'Benefits Unlocked'

  return (
    <div className="max-w-3xl mx-auto mt-16 mb-6">
      {/* Section header */}
      <div className="text-center mb-8">
        <div className="text-3xl mb-2">📈</div>
        <h2 className="text-2xl font-extrabold text-gray-800 mb-2">{title}</h2>
        <p className="text-sm text-gray-500 max-w-xl mx-auto">{subtitle}</p>
      </div>

      {/* Projection cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {PROJECTIONS.map((p) => (
          <div
            key={p.label}
            className={`card border ${p.border} ${p.bg} flex flex-col items-center text-center gap-2 py-6`}
          >
            <span className="text-4xl">{p.icon}</span>
            <div className="text-base font-bold text-gray-700">{p.label}</div>
            <div className="text-xs text-gray-400 uppercase tracking-wide">{benefitLabel}</div>
            <div className={`text-xl font-extrabold ${p.color}`}>{p.display}</div>
          </div>
        ))}
      </div>

      {/* Bottom note */}
      <p className="text-center text-xs text-gray-400 mt-4">
        * Based on average ₹8,56,000 benefit per citizen across 7 government schemes.
      </p>
    </div>
  )
}
