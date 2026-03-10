'use client'

interface Citizen {
  id: number
  name: string
  age?: number
  occupation?: string
  income?: number
  state?: string
  eligibility_score?: number
  total_benefits?: number
  status?: string
  registered_schemes?: string[]
}

interface Props {
  citizens: Citizen[]
}

const SCORE_COLOR = (score: number) =>
  score >= 80 ? 'text-green-600 bg-green-50' :
  score >= 60 ? 'text-orange-600 bg-orange-50' :
  'text-red-600 bg-red-50'

export default function CitizenTable({ citizens }: Props) {
  return (
    <div className="card overflow-hidden p-0">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="font-bold text-gray-800">Registered Citizens</h2>
        <span className="text-sm text-gray-500">{citizens.length} records</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              {['Citizen', 'Occupation', 'Income/mo', 'State', 'Eligibility', 'Est. Benefits', 'Status'].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {citizens.map(c => (
              <tr key={c.id} className="hover:bg-gray-50 transition">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                      {(c.name || 'U')[0]}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{c.name}</div>
                      <div className="text-xs text-gray-400">Age {c.age}</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600 capitalize">{c.occupation}</td>
                <td className="px-4 py-3 font-semibold text-gray-800">
                  ₹{(c.income || 0).toLocaleString('en-IN')}
                </td>
                <td className="px-4 py-3 text-gray-600">{c.state}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-lg font-bold text-xs ${SCORE_COLOR(c.eligibility_score || 0)}`}>
                    {c.eligibility_score || 0}%
                  </span>
                </td>
                <td className="px-4 py-3 font-semibold text-green-700">
                  ₹{((c.total_benefits || 0) / 100000).toFixed(1)}L
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    c.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}>
                    {c.status || 'active'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
