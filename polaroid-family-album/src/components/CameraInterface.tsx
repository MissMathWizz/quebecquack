'use client'

import { useState, useRef, useEffect } from 'react'
import { Camera, X, Sparkles, Upload, Loader2 } from 'lucide-react'

interface CameraInterfaceProps {
  onCapture: (photoData: string) => void
  onClose: () => void
  onAIGenerate: (photoUrl: string, prompt: string) => void
  aiMode?: boolean
}

export default function CameraInterface({ onCapture, onClose, onAIGenerate, aiMode = false }: CameraInterfaceProps) {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [aiPrompt, setAiPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [mode, setMode] = useState<'camera' | 'ai' | 'upload'>(aiMode ? 'ai' : 'camera')
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (mode === 'camera') {
      startCamera()
    }
    
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [mode])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      const context = canvas.getContext('2d')
      
      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)
        
        const photoData = canvas.toDataURL('image/jpeg', 0.8)
        onCapture(photoData)
      }
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const photoData = e.target?.result as string
        onCapture(photoData)
      }
      reader.readAsDataURL(file)
    }
  }

  const generateAIPhoto = async () => {
    if (!aiPrompt.trim()) return
    
    setIsGenerating(true)
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: `${aiPrompt}, polaroid photo, vintage aesthetic, soft lighting, slightly faded colors`,
          model: 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b',
          lora_model: 'ferwanda-ferwando-lora',
          lora_strength: 0.8,
          negative_prompt: 'blurry, low quality, distorted, modern, digital',
          num_inference_steps: 30,
          guidance_scale: 7.5
        }),
      })
      
      const data = await response.json()
      
      if (data.success && data.imageUrl) {
        onAIGenerate(data.imageUrl, aiPrompt)
      } else {
        console.error('Failed to generate image:', data.error)
      }
    } catch (error) {
      console.error('Error generating AI photo:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold font-polaroid text-gray-800">
          {mode === 'ai' ? 'AI Photo Generator' : mode === 'upload' ? 'Upload Photo' : 'Camera'}
        </h2>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-200 rounded-full transition-colors"
        >
          <X size={24} />
        </button>
      </div>

      {/* Mode selector */}
      <div className="flex space-x-2">
        <button
          onClick={() => setMode('camera')}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
            mode === 'camera' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <Camera size={16} />
          <span>Camera</span>
        </button>
        
        <button
          onClick={() => setMode('ai')}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
            mode === 'ai' 
              ? 'bg-purple-500 text-white' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <Sparkles size={16} />
          <span>AI Generate</span>
        </button>
        
        <button
          onClick={() => setMode('upload')}
          className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
            mode === 'upload' 
              ? 'bg-green-500 text-white' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          <Upload size={16} />
          <span>Upload</span>
        </button>
      </div>

      {/* Camera Mode */}
      {mode === 'camera' && (
        <div className="space-y-4">
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-80 object-cover"
            />
            <canvas ref={canvasRef} className="hidden" />
          </div>
          
          <div className="flex justify-center">
            <button
              onClick={capturePhoto}
              className="bg-blue-500 text-white px-6 py-3 rounded-full hover:bg-blue-600 transition-colors flex items-center space-x-2"
            >
              <Camera size={20} />
              <span>Capture Photo</span>
            </button>
          </div>
        </div>
      )}

      {/* AI Generation Mode */}
      {mode === 'ai' && (
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 font-polaroid text-gray-800">
              Generate AI Photo with Ferwanda & Ferwando
            </h3>
            
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Describe the photo you want to generate... (e.g., 'Ferwanda and Ferwando having dinner at a fancy restaurant')"
              className="w-full p-3 border border-gray-300 rounded-lg resize-none h-24 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            
            <div className="mt-4 text-sm text-gray-600">
              <p><strong>Tip:</strong> The AI will automatically add Polaroid styling and use the trained Ferwanda-Ferwando LoRA model.</p>
            </div>
          </div>
          
          <div className="flex justify-center">
            <button
              onClick={generateAIPhoto}
              disabled={!aiPrompt.trim() || isGenerating}
              className="bg-purple-500 text-white px-6 py-3 rounded-full hover:bg-purple-600 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  <span>Generate AI Photo</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Upload Mode */}
      {mode === 'upload' && (
        <div className="space-y-4">
          <div 
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-500 transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 font-polaroid">
              Click to upload a photo from your device
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supports JPG, PNG, and GIF files
            </p>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>
      )}
    </div>
  )
}