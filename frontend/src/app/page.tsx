'use client'
import Link from 'next/link'
import { useState } from 'react'
import LanguageSelector from '@/components/LanguageSelector'
import ChatAssistant from '@/components/ChatAssistant'
import ImpactCalculator from '@/components/ImpactCalculator'

const LANG_TEXT: Record<string, any> = {
  en: {
    title: 'AI Citizen Welfare Assistant',
    subtitle: 'Discover government schemes you qualify for — instantly',
    aiLabel: 'Powered by AI: Speech Recognition • OCR • Eligibility Engine',
    impact: 'Helping 500M+ informal workers discover government welfare schemes instantly.',
    speak: '🎤 Speak Your Details',
    upload: '📄 Upload Aadhaar',
    find: '🔍 Find Eligible Schemes',
    dashboard: '📊  NGO Dashboard',
    how: 'How it works',
    step1: 'Speak or type your details',
    step2: 'Upload your Aadhaar card',
    step3: 'Get your eligible schemes',
    schemes: 'Schemes Available',
    citizens: 'Citizens Served',
    benefits: 'Benefits Unlocked',
    demoNote: 'Demo Mode — using simulated welfare scheme data.',
  },
  hi: {
    title: 'AI नागरिक कल्याण सहायक',
    subtitle: 'तुरंत जानें — किन सरकारी योजनाओं के आप पात्र हैं',
    aiLabel: 'AI संचालित: स्पीच रिकग्निशन • OCR • एलिजिबिलिटी इंजन',
    impact: '500M+ असंगठित श्रमिकों को सरकारी योजनाएं तुरंत खोजने में मदद।',
    speak: '🎤  बोलें',
    upload: '📄  दस्तावेज़ अपलोड करें',
    find: '🔍  योजनाएं खोजें',
    dashboard: '📊  NGO डैशबोर्ड',
    how: 'यह कैसे काम करता है',
    step1: 'अपनी जानकारी बोलें या टाइप करें',
    step2: 'अपना आधार कार्ड अपलोड करें',
    step3: 'अपनी पात्र योजनाएं पाएं',
    schemes: 'उपलब्ध योजनाएं',
    citizens: 'सेवित नागरिक',
    benefits: 'लाभ अनलॉक',
    demoNote: 'डेमो मोड — सिम्युलेटेड योजना डेटा का उपयोग।',
  },
  ta: {
    title: 'AI குடிமக்கள் நல உதவியாளர்',
    subtitle: 'நீங்கள் தகுதிபெறும் அரசு திட்டங்களை உடனே கண்டறியுங்கள்',
    aiLabel: 'AI மூலம் இயங்குகிறது: பேச்சு அடையாளம் • OCR • தகுதி இயந்திரம்',
    impact: '500M+ ஒழுங்கற்ற தொழிலாளர்கள் அரசு நலத் திட்டங்களை உடனே கண்டறிய உதவுகிறது.',
    speak: '🎤  பேசுங்கள்',
    upload: '📄  ஆவணம் பதிவேற்றவும்',
    find: '🔍  திட்டங்களை கண்டறியவும்',
    dashboard: '📊  NGO டாஷ்போர்டு',
    how: 'எப்படி வேலை செய்கிறது',
    step1: 'உங்கள் விவரங்களை பேசுங்கள் அல்லது தட்டச்சு செய்யுங்கள்',
    step2: 'உங்கள் ஆதார் அட்டையை பதிவேற்றவும்',
    step3: 'தகுதி திட்டங்களை பெறுங்கள்',
    schemes: 'திட்டங்கள் கிடைக்கின்றன',
    citizens: 'சேவை செய்யப்பட்ட குடிமக்கள்',
    benefits: 'நலன்கள் திறக்கப்பட்டது',
    demoNote: 'டெமோ மோடு — சிமுலேட்டட் நலத் திட்ட தரவு பயன்படுத்தப்படுகிறது.',
  },
}

export default function Home() {
  const [lang, setLang] = useState('en')
  const t = LANG_TEXT[lang] || LANG_TEXT['en']

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🇮🇳</span>
            <div>
              <div className="font-bold text-blue-800 text-sm leading-tight">AI Welfare Assistant</div>
              <div className="text-xs text-gray-500">Government of India Demo</div>
            </div>
          </div>
          <LanguageSelector value={lang} onChange={setLang} />
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-4 py-12 text-center">
        <div className="text-5xl mb-4">🏛️</div>
        <h1 className="text-3xl md:text-4xl font-extrabold text-blue-900 mb-3">{t.title}</h1>
        <p className="text-sm md:text-base font-medium text-blue-700 mb-2">{t.aiLabel}</p>
        <p className="text-base md:text-lg text-gray-700 mb-2 max-w-3xl mx-auto">{t.impact}</p>
        <p className="text-lg text-gray-600 mb-10 max-w-xl mx-auto">{t.subtitle}</p>

        {/* Big action buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-10">
          <Link href={`/voice?lang=${lang}`} className="btn-primary text-xl py-5 px-10 bg-red-500 hover:bg-red-600 min-w-[200px]">
            {t.speak}
          </Link>
          <Link href={`/upload?lang=${lang}`} className="btn-primary text-xl py-5 px-10 bg-green-600 hover:bg-green-700 min-w-[200px]">
            {t.upload}
          </Link>
          <Link href={`/results?demo=true&lang=${lang}`} className="btn-primary text-xl py-5 px-10 min-w-[200px]">
            {t.find}
          </Link>
        </div>

        <Link href="/dashboard" className="inline-block btn-secondary text-base py-3 px-6 mb-12">
          {t.dashboard}
        </Link>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6 mb-16 max-w-2xl mx-auto">
          {[
            { label: t.schemes, value: '7+', color: 'text-blue-600' },
            { label: t.citizens, value: '3', color: 'text-green-600' },
            { label: t.benefits, value: '₹23L+', color: 'text-orange-600' },
          ].map(stat => (
            <div key={stat.label} className="card text-center">
              <div className={`text-3xl font-extrabold ${stat.color}`}>{stat.value}</div>
              <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Impact Projection */}
        <ImpactCalculator language={lang} />

        {/* How it works */}
        <div className="max-w-3xl mx-auto">
          <h2 className="text-xl font-bold text-gray-700 mb-6">{t.how}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { icon: '🎤', step: '1', text: t.step1 },
              { icon: '📷', step: '2', text: t.step2 },
              { icon: '✅', step: '3', text: t.step3 },
            ].map(item => (
              <div key={item.step} className="card flex flex-col items-center text-center gap-3">
                <div className="text-4xl">{item.icon}</div>
                <div className="w-7 h-7 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">{item.step}</div>
                <p className="text-gray-700 font-medium">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Chat Assistant */}
      <ChatAssistant language={lang} />

      <footer className="text-center text-xs text-gray-400 pb-6">
        {t.demoNote}
      </footer>
    </main>
  )
}
