/**
 * API service - all calls to the FastAPI backend.
 * Base URL proxied through Next.js config to http://localhost:8000
 */

const BASE = 'http://localhost:8000'

async function safeFetch(url: string, options?: RequestInit) {
  const res = await fetch(url, options)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export const api = {
  // Voice / text input
  sendText: (text: string, language = 'en') =>
    safeFetch(`${BASE}/voice-input/text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
    }),

  sendAudio: (audioBlob: Blob, language = 'en') => {
    const form = new FormData()
    form.append('audio', audioBlob, 'recording.webm')
    form.append('language', language)
    return safeFetch(`${BASE}/voice-input`, { method: 'POST', body: form })
  },

  // Document upload
  uploadDocument: (file: File, docType = 'aadhaar', language = 'en') => {
    const form = new FormData()
    form.append('file', file)
    form.append('document_type', docType)
    form.append('language', language)
    return safeFetch(`${BASE}/upload-document`, { method: 'POST', body: form })
  },

  // Schemes
  getSchemes: (category?: string) =>
    safeFetch(`${BASE}/schemes${category ? `?category=${category}` : ''}`),

  checkEligibility: (profile: Record<string, any>) =>
    safeFetch(`${BASE}/schemes/check-eligibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    }),

  // Citizens / Dashboard
  getCitizens: () => safeFetch(`${BASE}/citizens`),

  getNgoDashboard: () => safeFetch(`${BASE}/citizens/ngo-dashboard`),

  getCitizen: (id: number) => safeFetch(`${BASE}/citizens/${id}`),

  createCitizen: (data: Record<string, any>) =>
    safeFetch(`${BASE}/citizens`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }),
}
