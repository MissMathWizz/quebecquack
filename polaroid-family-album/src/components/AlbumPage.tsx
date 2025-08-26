'use client'

import { useState, useEffect } from 'react'
import { Camera, Sparkles, Users, Settings } from 'lucide-react'
import PolaroidPhoto from './PolaroidPhoto'
import CameraInterface from './CameraInterface'
import { Photo, Album } from '@/types'

export default function AlbumPage() {
  const [photos, setPhotos] = useState<Photo[]>([])
  const [showCamera, setShowCamera] = useState(false)
  const [showAIGenerator, setShowAIGenerator] = useState(false)
  const [loading, setLoading] = useState(true)
  
  const mockAlbum: Album = {
    id: '1',
    title: 'Ferwanda & Ferwando Family Album',
    description: 'Our beautiful family memories enhanced with AI magic',
    created_at: new Date().toISOString(),
    user_id: 'user1',
    is_public: false
  }

  // Mock photos for demonstration
  useEffect(() => {
    const mockPhotos: Photo[] = [
      {
        id: '1',
        url: '/api/placeholder/400/300',
        caption: 'Ferwanda and Ferwando at the beach',
        created_at: new Date('2024-01-15').toISOString(),
        is_generated: false,
        user_id: 'user1',
        album_id: '1'
      },
      {
        id: '2',
        url: '/api/placeholder/400/300',
        caption: 'AI-generated: Family picnic in the park',
        created_at: new Date('2024-02-01').toISOString(),
        is_generated: true,
        user_id: 'user1',
        album_id: '1',
        metadata: {
          prompt: 'Ferwanda and Ferwando having a picnic in a sunny park, polaroid style, vintage aesthetic',
          model: 'SDXL with Ferwanda-Ferwando LoRA',
          lora_strength: 0.8
        }
      }
    ]
    
    setTimeout(() => {
      setPhotos(mockPhotos)
      setLoading(false)
    }, 1000)
  }, [])

  const handlePhotoCapture = async (photoData: string) => {
    const newPhoto: Photo = {
      id: Date.now().toString(),
      url: photoData,
      caption: 'New family moment',
      created_at: new Date().toISOString(),
      is_generated: false,
      user_id: 'user1',
      album_id: '1'
    }
    
    setPhotos(prev => [newPhoto, ...prev])
    setShowCamera(false)
  }

  const handleAIGeneration = async (photoUrl: string, prompt: string) => {
    const newPhoto: Photo = {
      id: Date.now().toString(),
      url: photoUrl,
      caption: `AI Generated: ${prompt}`,
      created_at: new Date().toISOString(),
      is_generated: true,
      user_id: 'user1',
      album_id: '1',
      metadata: {
        prompt,
        model: 'SDXL with Ferwanda-Ferwando LoRA',
        lora_strength: 0.8
      }
    }
    
    setPhotos(prev => [newPhoto, ...prev])
    setShowAIGenerator(false)
  }

  const handleLike = (photoId: string) => {
    console.log('Liked photo:', photoId)
    // TODO: Implement like functionality with Supabase
  }

  const handleComment = (photoId: string, comment: string) => {
    console.log('Comment on photo:', photoId, comment)
    // TODO: Implement comment functionality with Supabase
  }

  const handleShare = (photoId: string) => {
    console.log('Share photo:', photoId)
    // TODO: Implement share functionality
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-polaroid-border border-t-purple-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg font-polaroid text-gray-600">Loading your family memories...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-6">
      {/* Header */}
      <header className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2 font-polaroid">
          {mockAlbum.title}
        </h1>
        <p className="text-lg text-gray-600 font-polaroid">
          {mockAlbum.description}
        </p>
        
        {/* Action buttons */}
        <div className="flex justify-center space-x-4 mt-6">
          <button
            onClick={() => setShowCamera(true)}
            className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors shadow-lg"
          >
            <Camera size={20} />
            <span>Take Photo</span>
          </button>
          
          <button
            onClick={() => setShowAIGenerator(true)}
            className="flex items-center space-x-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-colors shadow-lg"
          >
            <Sparkles size={20} />
            <span>Generate AI Photo</span>
          </button>
          
          <button className="flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors shadow-lg">
            <Users size={20} />
            <span>Invite Friends</span>
          </button>
          
          <button className="flex items-center space-x-2 bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors shadow-lg">
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </div>
      </header>

      {/* Photo Grid */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 place-items-center">
          {photos.map((photo) => (
            <PolaroidPhoto
              key={photo.id}
              photo={photo}
              onLike={handleLike}
              onComment={handleComment}
              onShare={handleShare}
            />
          ))}
        </div>

        {photos.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📷</div>
            <h3 className="text-xl font-polaroid text-gray-600 mb-2">No photos yet!</h3>
            <p className="text-gray-500 font-polaroid">
              Start by taking your first photo or generating one with AI
            </p>
          </div>
        )}
      </div>

      {/* Camera Interface Modal */}
      {showCamera && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <CameraInterface
              onCapture={handlePhotoCapture}
              onClose={() => setShowCamera(false)}
              onAIGenerate={handleAIGeneration}
            />
          </div>
        </div>
      )}

      {/* AI Generator Modal */}
      {showAIGenerator && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <CameraInterface
              onCapture={handlePhotoCapture}
              onClose={() => setShowAIGenerator(false)}
              onAIGenerate={handleAIGeneration}
              aiMode={true}
            />
          </div>
        </div>
      )}
    </div>
  )
}