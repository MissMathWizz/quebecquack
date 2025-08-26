import Replicate from 'replicate'
import { GenerationRequest } from '@/types'

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN!,
})

export interface PolaroidGenerationOptions extends GenerationRequest {
  polaroid_style?: boolean
  vintage_filter?: boolean
  soft_lighting?: boolean
}

export async function generatePolaroidPhoto(options: PolaroidGenerationOptions) {
  const {
    prompt,
    model = 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b',
    lora_model,
    lora_strength = 0.8,
    negative_prompt = 'blurry, low quality, distorted, modern, digital, oversaturated',
    num_inference_steps = 30,
    guidance_scale = 7.5,
    polaroid_style = true,
    vintage_filter = true,
    soft_lighting = true
  } = options

  // Enhance prompt with Polaroid aesthetic
  let enhancedPrompt = prompt
  
  if (polaroid_style) {
    enhancedPrompt += ', polaroid photo, vintage aesthetic'
  }
  
  if (soft_lighting) {
    enhancedPrompt += ', soft lighting, natural lighting'
  }
  
  if (vintage_filter) {
    enhancedPrompt += ', slightly faded colors, film grain, nostalgic mood'
  }

  const input: any = {
    prompt: enhancedPrompt,
    negative_prompt,
    width: 1024,
    height: 1024,
    num_inference_steps,
    guidance_scale,
    scheduler: 'K_EULER',
    num_outputs: 1,
    high_noise_frac: 0.8,
    apply_watermark: false
  }

  // Add LoRA support if specified
  if (lora_model && lora_strength) {
    // For SDXL with LoRA, we need to use a different model or approach
    // This would typically involve a custom fine-tuned model
    input.lora_scale = lora_strength
  }

  try {
    const output = await replicate.run(model, { input })
    
    if (Array.isArray(output) && output.length > 0) {
      return {
        success: true,
        imageUrl: output[0],
        metadata: {
          model,
          prompt: enhancedPrompt,
          lora_model,
          lora_strength,
          generation_time: new Date().toISOString()
        }
      }
    } else {
      throw new Error('No image generated')
    }
  } catch (error) {
    console.error('Replicate generation error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    }
  }
}

export async function generateFamilyPhoto(
  prompt: string, 
  includeLoRA: boolean = true
): Promise<{ success: boolean; imageUrl?: string; error?: string }> {
  const familyPrompt = `Ferwanda and Ferwando, ${prompt}`
  
  return generatePolaroidPhoto({
    prompt: familyPrompt,
    model: 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b',
    lora_model: includeLoRA ? 'ferwanda-ferwando-lora' : undefined,
    lora_strength: includeLoRA ? 0.8 : undefined,
    negative_prompt: 'blurry, low quality, distorted, modern, digital, multiple people not Ferwanda and Ferwando',
    num_inference_steps: 30,
    guidance_scale: 7.5
  })
}

export async function enhancePhotoWithFriend(
  originalImageUrl: string,
  friendDescription: string,
  placement: 'left' | 'right' | 'center' = 'right'
): Promise<{ success: boolean; imageUrl?: string; error?: string }> {
  try {
    // For inpainting, we'd use a different model
    const inpaintModel = 'stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf'
    
    const output = await replicate.run(inpaintModel, {
      input: {
        image: originalImageUrl,
        prompt: `Add ${friendDescription} to the ${placement} side of the photo, polaroid style, vintage aesthetic, natural integration`,
        negative_prompt: 'blurry, unnatural, poorly integrated, low quality',
        num_inference_steps: 30,
        guidance_scale: 7.5
      }
    })

    if (Array.isArray(output) && output.length > 0) {
      return {
        success: true,
        imageUrl: output[0]
      }
    } else {
      throw new Error('No image generated')
    }
  } catch (error) {
    console.error('Friend integration error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    }
  }
}

// Utility function to save generated images
export async function saveGeneratedImage(
  imageUrl: string, 
  filename?: string
): Promise<string> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const savedFilename = filename || `generated_${timestamp}.png`
  
  try {
    // In a real implementation, you'd save to your storage service
    // For now, we'll return the original URL
    console.log(`Image would be saved as: public/generated/${savedFilename}`)
    return imageUrl
  } catch (error) {
    console.error('Error saving image:', error)
    throw error
  }
}