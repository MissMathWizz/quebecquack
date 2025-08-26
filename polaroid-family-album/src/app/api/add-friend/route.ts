import { NextRequest, NextResponse } from 'next/server'
import { FriendInpaintingPipeline } from '@/lib/inpainting'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      originalImageUrl,
      friendImageUrl,
      friendDescription,
      placement = 'right',
      integrationStyle = 'polaroid',
      lightingMatch = true,
      preserveOriginalSubjects = true
    } = body

    // Validate required fields
    if (!originalImageUrl || !friendImageUrl || !friendDescription) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required fields: originalImageUrl, friendImageUrl, friendDescription' 
        },
        { status: 400 }
      )
    }

    // Validate placement
    const validPlacements = ['left', 'right', 'center', 'background']
    if (!validPlacements.includes(placement)) {
      return NextResponse.json(
        { 
          success: false, 
          error: `Invalid placement. Must be one of: ${validPlacements.join(', ')}` 
        },
        { status: 400 }
      )
    }

    // Validate integration style
    const validStyles = ['natural', 'polaroid', 'vintage']
    if (!validStyles.includes(integrationStyle)) {
      return NextResponse.json(
        { 
          success: false, 
          error: `Invalid integration style. Must be one of: ${validStyles.join(', ')}` 
        },
        { status: 400 }
      )
    }

    console.log('🤝 Starting friend integration process...')
    console.log(`   Original: ${originalImageUrl.substring(0, 50)}...`)
    console.log(`   Friend: ${friendImageUrl.substring(0, 50)}...`)
    console.log(`   Description: ${friendDescription}`)
    console.log(`   Placement: ${placement}`)

    // Initialize inpainting pipeline
    const pipeline = new FriendInpaintingPipeline()

    // Process the friend integration
    const result = await pipeline.processImages({
      originalImageUrl,
      friendImageUrl,
      friendDescription,
      placement,
      integrationStyle,
      lightingMatch,
      preserveOriginalSubjects
    })

    if (result.success) {
      console.log('✅ Friend integration successful')
      return NextResponse.json({
        success: true,
        integratedImageUrl: result.integratedImageUrl,
        maskUrl: result.maskUrl,
        metadata: result.metadata
      })
    } else {
      console.error('❌ Friend integration failed:', result.error)
      return NextResponse.json(
        { 
          success: false, 
          error: result.error,
          metadata: result.metadata
        },
        { status: 500 }
      )
    }

  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Return information about the friend integration service
  return NextResponse.json({
    service: 'Friend Integration API',
    version: '1.0.0',
    description: 'Add friends to existing family photos using AI inpainting',
    endpoints: {
      POST: {
        description: 'Integrate a friend into an existing family photo',
        requiredFields: [
          'originalImageUrl',
          'friendImageUrl', 
          'friendDescription'
        ],
        optionalFields: [
          'placement (left|right|center|background)',
          'integrationStyle (natural|polaroid|vintage)',
          'lightingMatch (boolean)',
          'preserveOriginalSubjects (boolean)'
        ]
      }
    },
    supportedPlacements: ['left', 'right', 'center', 'background'],
    supportedStyles: ['natural', 'polaroid', 'vintage'],
    processingCapabilities: [
      'Face detection and extraction',
      'Lighting condition matching',
      'Polaroid aesthetic preservation',
      'Seamless background integration',
      'Multi-person composition handling'
    ]
  })
}