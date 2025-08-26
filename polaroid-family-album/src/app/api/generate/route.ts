import { NextRequest, NextResponse } from 'next/server'
import { generatePolaroidPhoto, saveGeneratedImage } from '@/lib/replicate'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      prompt,
      model,
      lora_model,
      lora_strength,
      negative_prompt,
      num_inference_steps,
      guidance_scale
    } = body

    if (!prompt) {
      return NextResponse.json(
        { success: false, error: 'Prompt is required' },
        { status: 400 }
      )
    }

    // Generate the image using Replicate
    const result = await generatePolaroidPhoto({
      prompt,
      model,
      lora_model,
      lora_strength,
      negative_prompt,
      num_inference_steps,
      guidance_scale
    })

    if (!result.success) {
      return NextResponse.json(
        { success: false, error: result.error },
        { status: 500 }
      )
    }

    // Save the generated image (in a real app, you'd save to cloud storage)
    const savedImageUrl = await saveGeneratedImage(result.imageUrl!)

    return NextResponse.json({
      success: true,
      imageUrl: savedImageUrl,
      metadata: result.metadata
    })

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

// Handle preflight requests for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}