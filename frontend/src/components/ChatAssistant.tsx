'use client'
import { useState } from 'react'

interface Message {
  role: 'user' | 'assistant'
  text: string
}

interface Props {
  language?: string
}

// Offline FAQ answers for demo
const FAQ: Array<{ q: RegExp; a: string }> = [
  { q: /ayushman|health|hospital|medical/i, a: "Ayushman Bharat provides health insurance of ₹5,00,000 per family per year. It covers secondary and tertiary hospitalisation. Eligible families with income under ₹1,00,000 can apply at pmjay.gov.in." },
  { q: /eshram|e-shram|labour|unorganised/i, a: "e-Shram is a national database for unorganised workers. It provides a UAN card, accidental insurance of ₹2,00,000, and access to social security schemes. Register at eshram.gov.in." },
  { q: /pension|old age|mandhan|sym/i, a: "PM Shram Yogi Mandhan gives ₹3,000/month pension after age 60. Workers aged 18-40 with income under ₹15,000/month can enrol at maandhan.in." },
  { q: /house|home|awas|housing/i, a: "PM Awas Yojana (Gramin) provides ₹1,20,000 financial assistance for rural families to build a pucca house. Apply at pmayg.nic.in." },
  { q: /farmer|kisan|agriculture|crop/i, a: "PM Kisan Samman Nidhi gives ₹6,000/year to small and marginal farmers in 3 instalments of ₹2,000 directly to their bank account. Apply at pmkisan.gov.in." },
  { q: /lpg|gas|ujjwala|cooking/i, a: "PM Ujjwala Yojana gives free LPG connection to women from BPL households with ₹1,600 assistance. Apply at your nearest LPG dealer." },
  { q: /nrega|mgnrega|employment|100 days/i, a: "MGNREGS guarantees 100 days of wage employment per year to rural households at minimum wage (₹202-330/day). Apply at your Gram Panchayat." },
  { q: /document|aadhaar|required|apply/i, a: "For most schemes you need: Aadhaar Card, Bank Account linked to Aadhaar, and Ration Card (if BPL). Some schemes need land records or income certificate." },
  { q: /eligible|qualify|who can/i, a: "Eligibility depends on your income, age, occupation and state. Most schemes target workers earning under ₹1,50,000/year. Use the 'Find Schemes' button to check your exact eligibility." },
  { q: /hi|hello|help|namaste/i, a: "Hello! I am your AI welfare assistant. Ask me about government schemes like Ayushman Bharat, e-Shram, PM Kisan, PMAY, or eligibility criteria. How can I help?" },
]

function getAnswer(q: string): string {
  for (const faq of FAQ) {
    if (faq.q.test(q)) return faq.a
  }
  return "I can answer questions about Ayushman Bharat, e-Shram, PM Kisan, PM Awas Yojana, PM-SYM, Ujjwala, and MGNREGS. Please ask about any of these schemes or your eligibility."
}

export default function ChatAssistant({ language = 'en' }: Props) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', text: '👋 Hi! I am your welfare scheme assistant. Ask me anything about government schemes.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async () => {
    if (!input.trim()) return
    const userMsg: Message = { role: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    // Try backend first, fallback to local FAQ
    try {
      const res = await fetch('http://localhost:8000/schemes', { signal: AbortSignal.timeout(3000) })
      // Simple offline answer
      throw new Error('use offline')
    } catch {
      await new Promise(r => setTimeout(r, 600)) // simulate thinking
      const answer = getAnswer(userMsg.text)
      setMessages(prev => [...prev, { role: 'assistant', text: answer }])
    }
    setLoading(false)
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-2xl flex items-center justify-center text-2xl z-50 transition-all"
        title="Ask about schemes"
      >
        {open ? '✕' : '💬'}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-24 right-6 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col z-50 max-h-[500px]">
          {/* Header */}
          <div className="bg-blue-700 text-white px-4 py-3 rounded-t-2xl flex items-center gap-2">
            <span className="text-xl">🤖</span>
            <div>
              <div className="font-bold text-sm">Welfare Scheme Assistant</div>
              <div className="text-xs text-blue-200">Ask about any government scheme</div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 min-h-[200px]">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
                  m.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-sm'
                    : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                }`}>
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-3 py-2 text-sm text-gray-500">
                  Thinking...
                </div>
              </div>
            )}
          </div>

          {/* Suggested questions */}
          <div className="px-3 pb-2">
            <div className="flex gap-2 overflow-x-auto pb-1">
              {['Ayushman Bharat', 'e-Shram', 'PM Kisan', 'Who is eligible?'].map(q => (
                <button
                  key={q}
                  onClick={() => { setInput(q); }}
                  className="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full whitespace-nowrap hover:bg-blue-100 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="px-3 pb-3 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask about a scheme..."
              className="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              onClick={send}
              disabled={!input.trim() || loading}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-3 py-2 text-sm font-bold disabled:opacity-50 transition"
            >
              ↑
            </button>
          </div>
        </div>
      )}
    </>
  )
}
