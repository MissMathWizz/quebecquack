import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: { width: string; height: string } }
) {
  const width = parseInt(params.width)
  const height = parseInt(params.height)

  // Validate dimensions
  if (width <= 0 || height <= 0 || width > 2000 || height > 2000) {
    return NextResponse.json(
      { error: 'Invalid dimensions' },
      { status: 400 }
    )
  }

  // Create a simple SVG placeholder
  const svg = `
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" stroke-width="1"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="#f8f8f8"/>
      <rect width="100%" height="100%" fill="url(#grid)"/>
      <rect x="10" y="10" width="${width - 20}" height="${height - 20}" fill="none" stroke="#ddd" stroke-width="2" rx="8"/>
      <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#999">
        Polaroid Photo
      </text>
      <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#ccc">
        ${width} × ${height}
      </text>
    </svg>
  `

  return new NextResponse(svg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'public, max-age=86400', // Cache for 1 day
    },
  })
}