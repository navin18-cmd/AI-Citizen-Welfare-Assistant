import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Citizen Welfare Assistant',
  description: 'Discover government welfare schemes you qualify for',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* India flag stripe top */}
        <div className="h-1.5 w-full" style={{background:'linear-gradient(to right,#FF9933 33%,#fff 33%,#fff 66%,#138808 66%)'}} />
        {children}
      </body>
    </html>
  )
}
