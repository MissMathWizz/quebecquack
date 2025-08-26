import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Polaroid Family Album',
  description: 'AI-powered interactive family photo album with vintage Polaroid aesthetic',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-polaroid-cream to-polaroid-vintage">
        {children}
      </body>
    </html>
  )
}