import { createClient } from '@supabase/supabase-js'
import { Database } from '@/types/supabase'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey)

// Server-side client with service role key for admin operations
export const supabaseAdmin = createClient<Database>(
  supabaseUrl,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

// Types for database operations
export type Tables<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Row']
export type TablesInsert<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Insert']
export type TablesUpdate<T extends keyof Database['public']['Tables']> = Database['public']['Tables'][T]['Update']

// Photo operations
export const photoOperations = {
  async getPhotos(albumId: string) {
    const { data, error } = await supabase
      .from('photos')
      .select(`
        *,
        user_interactions (
          id,
          interaction_type,
          content,
          user_id,
          created_at
        )
      `)
      .eq('album_id', albumId)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data
  },

  async createPhoto(photo: TablesInsert<'photos'>) {
    const { data, error } = await supabase
      .from('photos')
      .insert([photo])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async updatePhoto(id: string, updates: TablesUpdate<'photos'>) {
    const { data, error } = await supabase
      .from('photos')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  async deletePhoto(id: string) {
    const { error } = await supabase
      .from('photos')
      .delete()
      .eq('id', id)

    if (error) throw error
  }
}

// Album operations
export const albumOperations = {
  async getAlbums(userId: string) {
    const { data, error } = await supabase
      .from('albums')
      .select(`
        *,
        album_collaborators!inner (
          role
        ),
        photos (
          id,
          url,
          created_at
        )
      `)
      .or(`user_id.eq.${userId},album_collaborators.user_id.eq.${userId}`)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data
  },

  async createAlbum(album: TablesInsert<'albums'>) {
    const { data, error } = await supabase
      .from('albums')
      .insert([album])
      .select()
      .single()

    if (error) throw error
    
    // Add creator as owner
    if (data) {
      await supabase
        .from('album_collaborators')
        .insert([{
          album_id: data.id,
          user_id: data.user_id,
          role: 'owner'
        }])
    }

    return data
  },

  async updateAlbum(id: string, updates: TablesUpdate<'albums'>) {
    const { data, error } = await supabase
      .from('albums')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  async deleteAlbum(id: string) {
    const { error } = await supabase
      .from('albums')
      .delete()
      .eq('id', id)

    if (error) throw error
  }
}

// Interaction operations
export const interactionOperations = {
  async addInteraction(interaction: TablesInsert<'user_interactions'>) {
    const { data, error } = await supabase
      .from('user_interactions')
      .insert([interaction])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async getPhotoInteractions(photoId: string) {
    const { data, error } = await supabase
      .from('user_interactions')
      .select(`
        *,
        profiles (
          full_name,
          avatar_url
        )
      `)
      .eq('photo_id', photoId)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data
  },

  async removeInteraction(id: string) {
    const { error } = await supabase
      .from('user_interactions')
      .delete()
      .eq('id', id)

    if (error) throw error
  }
}

// Invitation operations
export const invitationOperations = {
  async createInvitation(albumId: string, createdBy: string, maxUses = 1, expiresAt?: string) {
    const code = await generateInvitationCode()
    
    const { data, error } = await supabase
      .from('invitation_codes')
      .insert([{
        code,
        album_id: albumId,
        created_by: createdBy,
        max_uses: maxUses,
        expires_at: expiresAt
      }])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async useInvitation(code: string, userId: string) {
    // Get invitation details
    const { data: invitation, error: inviteError } = await supabase
      .from('invitation_codes')
      .select('*')
      .eq('code', code)
      .eq('is_active', true)
      .single()

    if (inviteError || !invitation) {
      throw new Error('Invalid or expired invitation code')
    }

    // Check if invitation is still valid
    if (invitation.expires_at && new Date(invitation.expires_at) < new Date()) {
      throw new Error('Invitation code has expired')
    }

    if (invitation.current_uses >= invitation.max_uses) {
      throw new Error('Invitation code has reached maximum uses')
    }

    // Add user as collaborator
    const { error: collaboratorError } = await supabase
      .from('album_collaborators')
      .insert([{
        album_id: invitation.album_id,
        user_id: userId,
        role: 'viewer',
        invited_by: invitation.created_by
      }])

    if (collaboratorError) throw collaboratorError

    // Update invitation usage count
    const { error: updateError } = await supabase
      .from('invitation_codes')
      .update({ 
        current_uses: invitation.current_uses + 1,
        is_active: invitation.current_uses + 1 < invitation.max_uses
      })
      .eq('id', invitation.id)

    if (updateError) throw updateError

    return invitation.album_id
  }
}

// LoRA model operations
export const loraOperations = {
  async getUserModels(userId: string) {
    const { data, error } = await supabase
      .from('lora_models')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data
  },

  async createModel(model: TablesInsert<'lora_models'>) {
    const { data, error } = await supabase
      .from('lora_models')
      .insert([model])
      .select()
      .single()

    if (error) throw error
    return data
  },

  async updateModel(id: string, updates: TablesUpdate<'lora_models'>) {
    const { data, error } = await supabase
      .from('lora_models')
      .update(updates)
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  }
}

// Helper functions
async function generateInvitationCode(): Promise<string> {
  const { data, error } = await supabase.rpc('generate_invitation_code')
  if (error) throw error
  return data
}