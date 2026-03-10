'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import CitizenTable from '@/components/CitizenTable'

const DEMO_DASHBOARD = {
  summary: {
    total_citizens: 3,
    total_schemes_available: 7,
    total_applications: 7,
    approved_applications: 5,
    total_benefits_unlocked: 2396600
  },
  citizens: [
    { id:1, name:"Ravi Kumar", age:34, occupation:"construction worker", income:10000, state:"Tamil Nadu", eligibility_score:87, total_benefits:822000, status:"active", registered_schemes:["e-Shram","Ayushman Bharat"] },
    { id:2, name:"Lakshmi Devi", age:29, occupation:"domestic worker", income:9000, state:"Karnataka", eligibility_score:92, total_benefits:823600, status:"active", registered_schemes:["Ayushman Bharat"] },
    { id:3, name:"Ramesh Patel", age:45, occupation:"farmer", income:12000, state:"Andhra Pradesh", eligibility_score:75, total_benefits:751000, status:"active", registered_schemes:["PM Kisan","Ayushman Bharat"] },
  ]
}

export default function DashboardPage() {
  const [data, setData] = useState<any>(DEMO_DASHBOARD)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch('http://localhost:8000/citizens/ngo-dashboard')
      .then(r => r.json())
      .then(d => setData(d))
      .catch(() => setData(DEMO_DASHBOARD))
      .finally(() => setLoading(false))
  }, [])

  const s = data?.summary || DEMO_DASHBOARD.summary

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-10">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link href="/" className="text-blue-600 text-sm mb-1 inline-block">← Home</Link>
            <h1 className="text-2xl font-extrabold text-gray-800">📊 NGO Welfare Dashboard</h1>
            <p className="text-sm text-gray-500">Monitor citizen welfare registrations</p>
          </div>
          <div className="hidden sm:block text-right">
            <div className="text-xs text-gray-400">Last updated</div>
            <div className="text-sm font-semibold text-gray-600">{new Date().toLocaleDateString('en-IN')}</div>
          </div>
        </div>

        {/* Summary stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {[
            { label: 'Total Citizens', value: s.total_citizens, icon: '👥', color: 'text-blue-600' },
            { label: 'Schemes Available', value: s.total_schemes_available, icon: '📋', color: 'text-purple-600' },
            { label: 'Applications', value: s.total_applications, icon: '📝', color: 'text-orange-600' },
            { label: 'Approved', value: s.approved_applications, icon: '✅', color: 'text-green-600' },
            { label: 'Benefits Unlocked', value: `₹${(s.total_benefits_unlocked/100000).toFixed(1)}L`, icon: '💰', color: 'text-red-600' },
          ].map(stat => (
            <div key={stat.label} className="card text-center">
              <div className="text-2xl mb-1">{stat.icon}</div>
              <div className={`text-2xl font-extrabold ${stat.color}`}>{stat.value}</div>
              <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Citizens table */}
        <CitizenTable citizens={data?.citizens || DEMO_DASHBOARD.citizens} />

        {/* Add citizen button */}
        <div className="mt-6 flex gap-4">
          <Link href="/voice" className="btn-primary text-base py-3 px-6">
            🎤 Register New Citizen
          </Link>
        </div>
      </div>
    </main>
  )
}
