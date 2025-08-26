import Replicate from 'replicate'

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN!,
})

export interface FriendIntegrationOptions {
  originalImageUrl: string
  friendImageUrl: string
  friendDescription: string
  placement: 'left' | 'right' | 'center' | 'background'
  integrationStyle: 'natural' | 'polaroid' | 'vintage'
  lightingMatch: boolean
  preserveOriginalSubjects: boolean
}

export interface IntegrationResult {
  success: boolean
  integratedImageUrl?: string
  maskUrl?: string
  error?: string
  metadata?: {
    originalImage: string
    friendImage: string
    placement: string
    processingTime: number
    model: string
    prompt: string
    maskGenerated: boolean
  }
}

export class FriendInpaintingPipeline {
  private inpaintModel = 'stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf'
  private segmentationModel = 'facebook/sam-vit-huge:9bf4c6ee7a25e5a8b5a85e8c0dc07e4e9e5e7b4d3c9b9b9b9b9b9b9b9b9b9'

  async processImages(options: FriendIntegrationOptions): Promise<IntegrationResult> {
    const startTime = Date.now()
    
    try {
      console.log('🔄 Starting friend integration pipeline...')
      
      // Step 1: Analyze original image for optimal placement
      const placementAnalysis = await this.analyzePlacement(options.originalImageUrl, options.placement)
      
      // Step 2: Extract friend from their photo
      const friendExtraction = await this.extractFriend(options.friendImageUrl, options.friendDescription)
      
      if (!friendExtraction.success) {
        throw new Error(`Friend extraction failed: ${friendExtraction.error}`)
      }
      
      // Step 3: Generate integration mask
      const maskGeneration = await this.generateIntegrationMask(
        options.originalImageUrl,
        placementAnalysis.suggestedRegion,
        friendExtraction.dimensions
      )
      
      // Step 4: Perform inpainting integration
      const integration = await this.performInpainting({
        originalImage: options.originalImageUrl,
        mask: maskGeneration.maskUrl!,
        friendDescription: this.buildIntegrationPrompt(options),
        style: options.integrationStyle,
        lightingMatch: options.lightingMatch
      })
      
      const processingTime = Date.now() - startTime
      
      return {
        success: true,
        integratedImageUrl: integration.imageUrl,
        maskUrl: maskGeneration.maskUrl,
        metadata: {
          originalImage: options.originalImageUrl,
          friendImage: options.friendImageUrl,
          placement: options.placement,
          processingTime,
          model: this.inpaintModel,
          prompt: this.buildIntegrationPrompt(options),
          maskGenerated: true
        }
      }
      
    } catch (error) {
      console.error('❌ Friend integration failed:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        metadata: {
          originalImage: options.originalImageUrl,
          friendImage: options.friendImageUrl,
          placement: options.placement,
          processingTime: Date.now() - startTime,
          model: this.inpaintModel,
          prompt: '',
          maskGenerated: false
        }
      }
    }
  }

  private async analyzePlacement(imageUrl: string, preferredPlacement: string) {
    // Analyze image composition to suggest optimal placement
    // In a full implementation, this would use computer vision to detect:
    // - Empty spaces, lighting conditions, perspective, etc.
    
    const placementStrategies = {
      left: { region: 'left third', priority: 'background integration' },
      right: { region: 'right third', priority: 'natural positioning' },
      center: { region: 'center background', priority: 'group dynamics' },
      background: { region: 'background area', priority: 'depth layering' }
    }
    
    return {
      suggestedRegion: placementStrategies[preferredPlacement as keyof typeof placementStrategies] || placementStrategies.right,
      lightingAnalysis: {
        dominantLighting: 'natural',
        shadowDirection: 'bottom-right',
        colorTemperature: 'warm'
      },
      compositionTips: [
        'Consider perspective matching',
        'Maintain consistent lighting',
        'Preserve original subjects prominence'
      ]
    }
  }

  private async extractFriend(friendImageUrl: string, description: string) {
    try {
      // Use segmentation model to extract the friend
      console.log('👤 Extracting friend from photo...')
      
      // In production, this would use SAM or similar for precise segmentation
      // For now, we'll simulate the extraction process
      return {
        success: true,
        extractedImageUrl: friendImageUrl, // Would be the segmented version
        dimensions: { width: 400, height: 600 },
        boundingBox: { x: 100, y: 50, width: 300, height: 500 },
        confidence: 0.92
      }
      
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Extraction failed'
      }
    }
  }

  private async generateIntegrationMask(
    originalImageUrl: string, 
    placementRegion: any, 
    friendDimensions: any
  ) {
    try {
      console.log('🎭 Generating integration mask...')
      
      // Generate mask for inpainting based on placement strategy
      // This would use image processing to create precise masks
      
      // For demo, return a simulated mask URL
      return {
        success: true,
        maskUrl: `data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==`,
        region: placementRegion,
        dimensions: friendDimensions
      }
      
    } catch (error) {
      throw new Error(`Mask generation failed: ${error}`)
    }
  }

  private async performInpainting(params: {
    originalImage: string
    mask: string
    friendDescription: string
    style: string
    lightingMatch: boolean
  }) {
    try {
      console.log('🎨 Performing inpainting integration...')
      
      const prompt = this.buildDetailedInpaintingPrompt(params)
      
      const output = await replicate.run(this.inpaintModel, {
        input: {
          image: params.originalImage,
          mask: params.mask,
          prompt: prompt,
          negative_prompt: this.buildNegativePrompt(),
          num_inference_steps: 30,
          guidance_scale: 7.5,
          num_outputs: 1
        }
      })

      if (Array.isArray(output) && output.length > 0) {
        return {
          success: true,
          imageUrl: output[0]
        }
      } else {
        throw new Error('No output from inpainting model')
      }
      
    } catch (error) {
      throw new Error(`Inpainting failed: ${error}`)
    }
  }

  private buildIntegrationPrompt(options: FriendIntegrationOptions): string {
    let prompt = `Add ${options.friendDescription} to the photo`
    
    // Placement specifications
    const placementPrompts = {
      left: 'positioned naturally on the left side of the group',
      right: 'positioned naturally on the right side of the group', 
      center: 'positioned naturally in the center background',
      background: 'positioned naturally in the background of the scene'
    }
    
    prompt += `, ${placementPrompts[options.placement]}`
    
    // Style specifications
    if (options.integrationStyle === 'polaroid') {
      prompt += ', polaroid photo style, vintage aesthetic, soft lighting'
    } else if (options.integrationStyle === 'vintage') {
      prompt += ', vintage photography, retro aesthetic, film grain'
    } else {
      prompt += ', natural photography, realistic integration'
    }
    
    // Lighting and preservation
    if (options.lightingMatch) {
      prompt += ', matching lighting conditions and shadows'
    }
    
    if (options.preserveOriginalSubjects) {
      prompt += ', preserving all original people in the photo without modification'
    }
    
    prompt += ', seamless integration, natural positioning, photorealistic'
    
    return prompt
  }

  private buildDetailedInpaintingPrompt(params: {
    originalImage: string
    mask: string
    friendDescription: string
    style: string
    lightingMatch: boolean
  }): string {
    let prompt = `Seamlessly integrate ${params.friendDescription} into this family photo. `
    
    prompt += 'The person should appear naturally positioned as if they were in the original photo. '
    
    if (params.lightingMatch) {
      prompt += 'Match the lighting, shadows, and color temperature of the original photo precisely. '
    }
    
    if (params.style === 'polaroid') {
      prompt += 'Maintain the polaroid aesthetic with vintage colors and soft lighting. '
    }
    
    prompt += 'Ensure realistic perspective, natural body positioning, and consistent image quality. '
    prompt += 'The integration should be undetectable and photorealistic.'
    
    return prompt
  }

  private buildNegativePrompt(): string {
    return [
      'blurry', 'low quality', 'distorted', 'unnatural positioning',
      'inconsistent lighting', 'obvious manipulation', 'artificial shadows',
      'mismatched perspective', 'floating person', 'duplicated people',
      'cut off limbs', 'weird anatomy', 'inconsistent style'
    ].join(', ')
  }

  // Method for testing different lighting conditions
  async testLightingIntegration(
    originalImageUrl: string,
    friendImageUrl: string,
    lightingConditions: string[]
  ) {
    const results = []
    
    for (const lighting of lightingConditions) {
      console.log(`🔆 Testing ${lighting} lighting integration...`)
      
      const result = await this.processImages({
        originalImageUrl,
        friendImageUrl,
        friendDescription: `a friend, ${lighting} lighting`,
        placement: 'right',
        integrationStyle: 'natural',
        lightingMatch: true,
        preserveOriginalSubjects: true
      })
      
      results.push({
        lightingCondition: lighting,
        result
      })
    }
    
    return results
  }

  // Method for composition testing
  async testCompositionIntegration(
    originalImageUrl: string,
    friendImageUrl: string,
    compositions: Array<{ placement: string, description: string }>
  ) {
    const results = []
    
    for (const comp of compositions) {
      console.log(`📐 Testing ${comp.placement} composition integration...`)
      
      const result = await this.processImages({
        originalImageUrl,
        friendImageUrl,
        friendDescription: comp.description,
        placement: comp.placement as any,
        integrationStyle: 'polaroid',
        lightingMatch: true,
        preserveOriginalSubjects: true
      })
      
      results.push({
        composition: comp,
        result
      })
    }
    
    return results
  }
}

// Helper function for quick friend addition
export async function addFriendToPhoto(
  originalImageUrl: string,
  friendImageUrl: string,
  friendDescription: string,
  placement: 'left' | 'right' | 'center' | 'background' = 'right'
): Promise<IntegrationResult> {
  const pipeline = new FriendInpaintingPipeline()
  
  return pipeline.processImages({
    originalImageUrl,
    friendImageUrl,
    friendDescription,
    placement,
    integrationStyle: 'polaroid',
    lightingMatch: true,
    preserveOriginalSubjects: true
  })
}