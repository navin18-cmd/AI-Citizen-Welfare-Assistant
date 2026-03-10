'use client'

interface Props {
  currentStep: number
}

const STEPS = [
  'Analyzing your profile with AI...',
  'Extracting document details...',
  'Matching government welfare schemes...',
]

export default function ProcessingOverlay({ currentStep }: Props) {
  const safeStep = Math.max(0, Math.min(currentStep, STEPS.length - 1))
  const progress = ((safeStep + 1) / STEPS.length) * 100

  return (
    <div className="fixed inset-0 z-50 bg-white/70 backdrop-blur-sm flex items-center justify-center px-4">
      <div className="card max-w-md w-full">
        <div className="text-center mb-4">
          <div className="text-3xl mb-2">🤖</div>
          <p className="font-semibold text-gray-800">{STEPS[safeStep]}</p>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="space-y-2">
          {STEPS.map((step, index) => {
            const active = index <= safeStep
            return (
              <div key={step} className="flex items-center gap-2 text-sm">
                <span
                  className={`w-2.5 h-2.5 rounded-full ${
                    active ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                />
                <span className={active ? 'text-gray-800 font-medium' : 'text-gray-500'}>{step}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
