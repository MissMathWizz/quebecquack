'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Heart, MessageCircle, Share2 } from 'lucide-react'
import { Photo } from '@/types'

interface PolaroidPhotoProps {
  photo: Photo
  onLike?: (photoId: string) => void
  onComment?: (photoId: string, comment: string) => void
  onShare?: (photoId: string) => void
}

export default function PolaroidPhoto({ photo, onLike, onComment, onShare }: PolaroidPhotoProps) {
  const [isFlipped, setIsFlipped] = useState(false)
  const [comment, setComment] = useState('')
  const [showComments, setShowComments] = useState(false)

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
  }

  const handleComment = () => {
    if (comment.trim() && onComment) {
      onComment(photo.id, comment)
      setComment('')
    }
  }

  return (
    <div 
      className="relative group cursor-pointer transform transition-all duration-300 hover:scale-105 hover:z-10"
      style={{ perspective: '1000px' }}
    >
      <div 
        className={`relative w-64 h-80 transition-transform duration-500 transform-style-preserve-3d ${
          isFlipped ? 'rotate-y-180' : ''
        }`}
        onClick={handleFlip}
      >
        {/* Front of Polaroid */}
        <div className="absolute inset-0 backface-hidden">
          <div className="bg-white p-3 shadow-polaroid group-hover:shadow-polaroid-hover rounded-sm polaroid-texture">
            <div className="relative w-full h-52 bg-gray-100 mb-3 overflow-hidden">
              <Image
                src={photo.url}
                alt={photo.caption}
                fill
                className="object-cover filter brightness-95 contrast-110 saturate-90"
              />
              {photo.is_generated && (
                <div className="absolute top-2 right-2 bg-purple-500 text-white text-xs px-2 py-1 rounded">
                  AI Generated
                </div>
              )}
            </div>
            
            <div className="text-center">
              <p className="font-polaroid text-sm text-gray-800 mb-2 h-12 overflow-hidden">
                {photo.caption}
              </p>
              <p className="text-xs text-gray-500 font-polaroid">
                {new Date(photo.created_at).toLocaleDateString()}
              </p>
            </div>

            {/* Interaction buttons */}
            <div className="absolute -bottom-2 -right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onLike?.(photo.id)
                }}
                className="bg-red-500 text-white p-2 rounded-full shadow-lg hover:bg-red-600 transition-colors"
              >
                <Heart size={14} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setShowComments(!showComments)
                }}
                className="bg-blue-500 text-white p-2 rounded-full shadow-lg hover:bg-blue-600 transition-colors"
              >
                <MessageCircle size={14} />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onShare?.(photo.id)
                }}
                className="bg-green-500 text-white p-2 rounded-full shadow-lg hover:bg-green-600 transition-colors"
              >
                <Share2 size={14} />
              </button>
            </div>
          </div>
        </div>

        {/* Back of Polaroid */}
        <div className="absolute inset-0 backface-hidden rotate-y-180">
          <div className="bg-white p-4 shadow-polaroid h-full rounded-sm flex flex-col justify-center items-center polaroid-texture">
            <div className="text-center space-y-4">
              <h3 className="font-polaroid text-lg font-bold text-gray-800">Photo Details</h3>
              
              {photo.metadata?.prompt && (
                <div>
                  <p className="text-xs text-gray-600 font-semibold mb-1">AI Prompt:</p>
                  <p className="text-xs text-gray-700 italic">"{photo.metadata.prompt}"</p>
                </div>
              )}
              
              {photo.metadata?.model && (
                <div>
                  <p className="text-xs text-gray-600 font-semibold mb-1">Model:</p>
                  <p className="text-xs text-gray-700">{photo.metadata.model}</p>
                </div>
              )}
              
              <div className="border-t pt-3 mt-3">
                <p className="text-xs text-gray-500">
                  Created: {new Date(photo.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Comment popup */}
      {showComments && (
        <div 
          className="absolute top-full left-0 mt-2 w-full bg-white rounded-lg shadow-lg p-3 z-20"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex space-x-2">
            <input
              type="text"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Add a comment..."
              className="flex-1 text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && handleComment()}
            />
            <button
              onClick={handleComment}
              className="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
            >
              Post
            </button>
          </div>
        </div>
      )}
    </div>
  )
}