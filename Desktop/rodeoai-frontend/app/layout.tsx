import type { Metadata } from 'next'
import './globals.css'
import { AuthProvider } from './lib/AuthContext'

export const metadata: Metadata = {
  title: 'RodeoAI - Powered by DataSpur',
  description: 'Expert rodeo insights, powered by AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
