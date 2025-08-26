export interface Photo {
  id: string
  url: string
  caption: string
  created_at: string
  is_generated: boolean
  user_id: string
  album_id: string
  metadata?: {
    prompt?: string
    model?: string
    lora_strength?: number
  }
}

export interface Album {
  id: string
  title: string
  description: string
  created_at: string
  user_id: string
  invitation_code?: string
  is_public: boolean
}

export interface UserInteraction {
  id: string
  user_id: string
  photo_id: string
  interaction_type: 'like' | 'comment' | 'share'
  content?: string
  created_at: string
}

export interface GenerationRequest {
  prompt: string
  model: string
  lora_model?: string
  lora_strength?: number
  negative_prompt?: string
  num_inference_steps?: number
  guidance_scale?: number
}