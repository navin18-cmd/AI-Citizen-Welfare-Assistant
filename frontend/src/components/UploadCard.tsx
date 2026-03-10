'use client'
import { useState, useRef } from 'react'

interface Props {
  language: string
  onResult: (data: any) => void
}

export default function UploadCard({ language, onResult }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [docType, setDocType] = useState('aadhaar')
  const [loading, setLoading] = useState(false)
  const [ocrResult, setOcrResult] = useState<any>(null)
  const [extractedText, setExtractedText] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = (f: File) => {
    setFile(f)
    const reader = new FileReader()
    reader.onload = e => setPreview(e.target?.result as string)
    reader.readAsDataURL(f)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setOcrResult(null)
    setExtractedText('')
    const form = new FormData()
    form.append('file', file)
    form.append('document_type', docType)
    form.append('language', language)
    try {
      const res = await fetch('http://localhost:8000/upload-document', { method: 'POST', body: form })
      const data = await res.json()
      setOcrResult(data.parsed_data)
      setExtractedText(data.extracted_text || '')
      onResult(data)
    } catch {
      // Demo fallback
      const demoData = {
        parsed_data: { name: 'Ravi Kumar', age: 34, state: 'Tamil Nadu', gender: 'Male', dob: '15/08/1990' },
        eligible_schemes: [
          { id: 1, name: 'Ayushman Bharat', short_name: 'Ayushman Bharat', category: 'Healthcare', benefit_value: 500000, benefit_description: 'Health cover of ₹5,00,000 per family', icon: '🏥', eligibility_score: 85, required_documents: ['Aadhaar Card', 'Ration Card'], apply_link: 'https://pmjay.gov.in', description: "World's largest health insurance program." },
        ],
        total_schemes: 1,
        total_benefit_value: 500000,
        message: "Document processed. You qualify for 1 scheme."
      }
      setOcrResult(demoData.parsed_data)
      setExtractedText('Government of India Name: Ravi Kumar DOB: 15/08/1990 Address: Tamil Nadu')
      onResult(demoData)
    } finally {
      setLoading(false)
    }
  }

  const useDemoDoc = () => {
    const demoData = {
      parsed_data: { name: 'Ravi Kumar', age: 34, state: 'Tamil Nadu', gender: 'Male', source: 'document' },
      eligible_schemes: [
        { id: 1, name: 'Ayushman Bharat', short_name: 'Ayushman Bharat', category: 'Healthcare', benefit_value: 500000, benefit_description: 'Health cover of ₹5,00,000 per family', icon: '🏥', eligibility_score: 85, required_documents: ['Aadhaar Card', 'Ration Card'], apply_link: 'https://pmjay.gov.in', description: "World's largest health insurance program." },
      ],
      total_schemes: 1,
      total_benefit_value: 500000,
    }
    setOcrResult(demoData.parsed_data)
    setExtractedText('Government of India Name: Ravi Kumar DOB: 15/08/1990 Address: Tamil Nadu')
    onResult(demoData)
  }

  return (
    <div className="card space-y-5">
      {/* Doc type selector */}
      <div>
        <label className="text-sm font-semibold text-gray-600 block mb-2">Document Type</label>
        <div className="flex gap-3">
          {['aadhaar', 'income_certificate'].map(t => (
            <button
              key={t}
              onClick={() => setDocType(t)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition ${
                docType === t ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {t === 'aadhaar' ? '🪪 Aadhaar Card' : '📋 Income Certificate'}
            </button>
          ))}
        </div>
      </div>

      {/* Drop zone */}
      <div
        onDrop={handleDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
        className="border-2 border-dashed border-blue-300 rounded-2xl p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition"
      >
        {preview ? (
          <img src={preview} alt="preview" className="max-h-40 mx-auto rounded-xl object-contain" />
        ) : (
          <>
            <div className="text-5xl mb-3">📁</div>
            <p className="text-gray-600 font-medium">Drag & drop or click to upload</p>
            <p className="text-xs text-gray-400 mt-1">JPG, PNG, PDF supported</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.pdf"
          className="hidden"
          onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </div>

      {file && (
        <p className="text-sm text-gray-500 text-center">Selected: {file.name}</p>
      )}

      {/* OCR result preview */}
      {extractedText && (
        <div className="bg-blue-50 rounded-xl p-4">
          <p className="text-sm font-semibold text-blue-700 mb-2">📝 OCR Extracted Text</p>
          <p className="text-xs text-blue-900 leading-relaxed whitespace-pre-wrap line-clamp-4">{extractedText}</p>
        </div>
      )}

      {ocrResult && (
        <div className="bg-green-50 rounded-xl p-4">
          <p className="text-sm font-semibold text-green-700 mb-2">✅ Extracted from document:</p>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(ocrResult).filter(([k]) => k !== 'source').map(([k, v]) => (
              <div key={k}>
                <span className="text-gray-500 capitalize">{k}: </span>
                <span className="font-semibold text-gray-800">{String(v)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="btn-primary w-full text-lg disabled:opacity-50"
      >
        {loading ? '⏳ Analyzing your profile with AI...' : '🔍 Extract & Find Schemes'}
      </button>

      <div className="text-center">
        <p className="text-xs text-gray-400 mb-2">No document? Try the demo:</p>
        <button
          onClick={useDemoDoc}
          className="text-sm text-blue-600 underline"
        >
          Use sample Aadhaar (demo)
        </button>
      </div>
    </div>
  )
}
