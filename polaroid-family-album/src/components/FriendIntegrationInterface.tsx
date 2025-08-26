'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { Upload, Camera, Users, Sparkles, Download, RotateCw, Zap, Settings } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import Image from 'next/image'

interface PolaroidDevelopingAnimationProps {
  isVisible: boolean
  progress: number
  stage: 'uploading' | 'processing' | 'developing' | 'complete'
}

interface FriendIntegrationData {
  originalPhoto: string | null
  friendPhoto: string | null
  friendDescription: string
  placement: 'left' | 'right' | 'center' | 'background'
  integrationStyle: 'natural' | 'polaroid' | 'vintage'
  lightingMatch: boolean
  result: string | null
}

const PolaroidDevelopingAnimation = ({ isVisible, progress, stage }: PolaroidDevelopingAnimationProps) => {
  const [developmentPhase, setDevelopmentPhase] = useState(0)
  
  useEffect(() => {
    if (stage === 'developing') {
      const interval = setInterval(() => {
        setDevelopmentPhase(prev => (prev + 1) % 4)
      }, 500)
      
      return () => clearInterval(interval)
    }
  }, [stage])

  if (!isVisible) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-amber-50 to-orange-100 p-8 rounded-xl shadow-2xl max-w-md w-full mx-4">
        {/* Polaroid Camera Icon */}
        <div className="text-center mb-6">
          <div className="inline-block p-4 bg-gradient-to-br from-amber-200 to-orange-300 rounded-lg">
            <Camera size={48} className="text-amber-800" />
          </div>
        </div>

        {/* Stage Display */}
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold text-amber-800 font-polaroid mb-2">
            {stage === 'uploading' && '📤 Uploading Photos...'}
            {stage === 'processing' && '🔄 Processing Images...'}
            {stage === 'developing' && '🎞️ Developing Polaroid...'}
            {stage === 'complete' && '✅ Integration Complete!'}
          </h3>
          
          <p className="text-sm text-amber-700">
            {stage === 'uploading' && 'Preparing your photos for integration'}
            {stage === 'processing' && 'Analyzing composition and lighting'}
            {stage === 'developing' && 'Creating the perfect blend'}
            {stage === 'complete' && 'Your friend has been added to the photo'}
          </p>
        </div>

        {/* Polaroid Development Simulation */}
        {stage === 'developing' && (
          <div className="mb-6">
            <div className="bg-white p-4 rounded-lg shadow-inner">
              <div className="aspect-square bg-gradient-to-br from-gray-100 via-gray-50 to-white rounded border-2 border-gray-200 relative overflow-hidden">
                {/* Development phases */}
                <div className={`absolute inset-0 transition-all duration-500 ${
                  developmentPhase >= 1 ? 'bg-gradient-to-t from-blue-100 to-transparent' : 'bg-gray-300'
                }`} />
                <div className={`absolute inset-0 transition-all duration-500 ${
                  developmentPhase >= 2 ? 'bg-gradient-to-br from-purple-50 to-pink-50 opacity-70' : 'opacity-0'
                }`} />
                <div className={`absolute inset-0 transition-all duration-500 ${
                  developmentPhase >= 3 ? 'bg-gradient-to-tl from-amber-50 to-orange-50 opacity-80' : 'opacity-0'
                }`} />
                
                {/* Developing image placeholder */}
                <div className="absolute inset-4 bg-gradient-to-br from-gray-200 to-gray-400 rounded opacity-20" />
                <div className="absolute inset-6 bg-gradient-to-br from-blue-100 to-purple-100 rounded opacity-30" />
                
                {/* Chemical wash effect */}
                <div className={`absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-40 transition-transform duration-1000 ${
                  stage === 'developing' ? 'animate-pulse' : ''
                }`} />
              </div>
              
              <div className="text-center mt-2 text-xs text-gray-600 font-polaroid">
                Developing... {Math.round(progress)}%
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="bg-amber-200 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-amber-400 to-orange-500 transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            >
              <div className="h-full bg-gradient-to-r from-white/20 to-transparent" />
            </div>
          </div>
          <div className="text-center mt-2 text-sm text-amber-700 font-polaroid">
            {progress}% Complete
          </div>
        </div>

        {/* Processing Steps */}
        <div className="space-y-2 text-sm text-amber-700">
          <div className={`flex items-center space-x-2 ${progress > 20 ? 'text-green-700' : ''}`}>
            <div className={`w-2 h-2 rounded-full ${progress > 20 ? 'bg-green-500' : 'bg-amber-300'}`} />
            <span>Analyzing original photo composition</span>
          </div>
          <div className={`flex items-center space-x-2 ${progress > 40 ? 'text-green-700' : ''}`}>
            <div className={`w-2 h-2 rounded-full ${progress > 40 ? 'bg-green-500' : 'bg-amber-300'}`} />
            <span>Extracting friend from uploaded photo</span>
          </div>
          <div className={`flex items-center space-x-2 ${progress > 60 ? 'text-green-700' : ''}`}>
            <div className={`w-2 h-2 rounded-full ${progress > 60 ? 'bg-green-500' : 'bg-amber-300'}`} />
            <span>Matching lighting and perspective</span>
          </div>
          <div className={`flex items-center space-x-2 ${progress > 80 ? 'text-green-700' : ''}`}>
            <div className={`w-2 h-2 rounded-full ${progress > 80 ? 'bg-green-500' : 'bg-amber-300'}`} />
            <span>Integrating with Polaroid aesthetic</span>
          </div>
          <div className={`flex items-center space-x-2 ${progress >= 100 ? 'text-green-700' : ''}`}>
            <div className={`w-2 h-2 rounded-full ${progress >= 100 ? 'bg-green-500' : 'bg-amber-300'}`} />
            <span>Finalizing integrated photo</span>
          </div>
        </div>

        {/* Vintage development sounds text */}
        {stage === 'developing' && (
          <div className="text-center mt-4 text-xs text-amber-600 italic">
            *whirr* *click* *buzz* 
          </div>
        )}
      </div>
    </div>
  )
}

export default function FriendIntegrationInterface() {
  const [integrationData, setIntegrationData] = useState<FriendIntegrationData>({
    originalPhoto: null,
    friendPhoto: null,
    friendDescription: '',
    placement: 'right',
    integrationStyle: 'polaroid',
    lightingMatch: true,
    result: null
  })

  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [stage, setStage] = useState<'uploading' | 'processing' | 'developing' | 'complete'>('uploading')
  const [showAdvanced, setShowAdvanced] = useState(false)

  const originalPhotoRef = useRef<HTMLInputElement>(null)
  const friendPhotoRef = useRef<HTMLInputElement>(null)

  // Dropzone for original photo
  const originalDropzone = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    },
    maxFiles: 1,
    onDrop: useCallback((acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        const reader = new FileReader()
        reader.onload = (e) => {
          setIntegrationData(prev => ({
            ...prev,
            originalPhoto: e.target?.result as string
          }))
        }
        reader.readAsDataURL(file)
      }
    }, [])
  })

  // Dropzone for friend photo
  const friendDropzone = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp']
    },
    maxFiles: 1,
    onDrop: useCallback((acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        const reader = new FileReader()
        reader.onload = (e) => {
          setIntegrationData(prev => ({
            ...prev,
            friendPhoto: e.target?.result as string
          }))
        }
        reader.readAsDataURL(file)
      }
    }, [])
  })

  const simulateIntegrationProcess = async () => {
    setIsProcessing(true)
    setProgress(0)
    setStage('uploading')

    // Simulate upload phase
    for (let i = 0; i <= 25; i += 5) {
      setProgress(i)
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    setStage('processing')
    // Simulate processing phase
    for (let i = 25; i <= 70; i += 5) {
      setProgress(i)
      await new Promise(resolve => setTimeout(resolve, 150))
    }

    setStage('developing')
    // Simulate developing phase (slower, more dramatic)
    for (let i = 70; i <= 95; i += 2) {
      setProgress(i)
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    // Final completion
    setProgress(100)
    setStage('complete')
    
    // Simulate result generation
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock result - in production this would be the API response
    setIntegrationData(prev => ({
      ...prev,
      result: '/api/placeholder/800/600?text=Integrated+Family+Photo'
    }))

    setTimeout(() => {
      setIsProcessing(false)
    }, 1500)
  }

  const handleIntegrateFriend = async () => {
    if (!integrationData.originalPhoto || !integrationData.friendPhoto) {
      alert('Please upload both photos first')
      return
    }

    if (!integrationData.friendDescription.trim()) {
      alert('Please describe your friend')
      return
    }

    try {
      await simulateIntegrationProcess()
      
      // In production, this would call the actual API
      /*
      const response = await fetch('/api/add-friend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          originalImageUrl: integrationData.originalPhoto,
          friendImageUrl: integrationData.friendPhoto,
          friendDescription: integrationData.friendDescription,
          placement: integrationData.placement,
          integrationStyle: integrationData.integrationStyle,
          lightingMatch: integrationData.lightingMatch,
          preserveOriginalSubjects: true
        })
      })

      const result = await response.json()
      
      if (result.success) {
        setIntegrationData(prev => ({
          ...prev,
          result: result.integratedImageUrl
        }))
      }
      */
    } catch (error) {
      console.error('Integration failed:', error)
      alert('Failed to integrate friend. Please try again.')
    }
  }

  const resetInterface = () => {
    setIntegrationData({
      originalPhoto: null,
      friendPhoto: null,
      friendDescription: '',
      placement: 'right',
      integrationStyle: 'polaroid',
      lightingMatch: true,
      result: null
    })
    setProgress(0)
    setStage('uploading')
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <Users size={32} className="text-purple-600" />
          <h1 className="text-4xl font-bold text-gray-800 font-polaroid">Add Friend to Photo</h1>
          <Sparkles size={32} className="text-yellow-500" />
        </div>
        <p className="text-lg text-gray-600 font-polaroid">
          Seamlessly integrate your friend into existing family photos with AI-powered inpainting
        </p>
      </div>

      {/* Main Interface */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column - Photo Uploads */}
        <div className="space-y-6">
          {/* Original Photo Upload */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 font-polaroid flex items-center space-x-2">
              <Camera size={24} />
              <span>Original Family Photo</span>
            </h3>
            
            <div 
              {...originalDropzone.getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
                originalDropzone.isDragActive 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 hover:border-blue-400'
              }`}
            >
              <input {...originalDropzone.getInputProps()} />
              
              {integrationData.originalPhoto ? (
                <div className="relative">
                  <Image
                    src={integrationData.originalPhoto}
                    alt="Original photo"
                    width={400}
                    height={300}
                    className="mx-auto rounded-lg shadow-md object-cover"
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setIntegrationData(prev => ({ ...prev, originalPhoto: null }))
                    }}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div>
                  <Upload size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 font-polaroid">
                    Drop your family photo here or click to browse
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    PNG, JPG, GIF up to 10MB
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Friend Photo Upload */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 font-polaroid flex items-center space-x-2">
              <Users size={24} />
              <span>Friend's Photo</span>
            </h3>
            
            <div 
              {...friendDropzone.getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${
                friendDropzone.isDragActive 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-gray-300 hover:border-green-400'
              }`}
            >
              <input {...friendDropzone.getInputProps()} />
              
              {integrationData.friendPhoto ? (
                <div className="relative">
                  <Image
                    src={integrationData.friendPhoto}
                    alt="Friend photo"
                    width={400}
                    height={300}
                    className="mx-auto rounded-lg shadow-md object-cover"
                  />
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setIntegrationData(prev => ({ ...prev, friendPhoto: null }))
                    }}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div>
                  <Users size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 font-polaroid">
                    Drop your friend's photo here or click to browse
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    PNG, JPG, GIF up to 10MB
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Configuration & Results */}
        <div className="space-y-6">
          {/* Configuration Panel */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold font-polaroid">Integration Settings</h3>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 transition-colors"
              >
                <Settings size={16} />
                <span className="text-sm">Advanced</span>
              </button>
            </div>

            {/* Friend Description */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Describe your friend
              </label>
              <textarea
                value={integrationData.friendDescription}
                onChange={(e) => setIntegrationData(prev => ({ ...prev, friendDescription: e.target.value }))}
                placeholder="e.g., a tall woman with curly hair wearing a blue dress"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none h-20"
              />
              <p className="text-xs text-gray-500 mt-1">
                Be specific about appearance, clothing, and pose for best results
              </p>
            </div>

            {/* Placement */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Placement
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: 'left', label: '← Left Side', icon: '👈' },
                  { value: 'right', label: 'Right Side →', icon: '👉' },
                  { value: 'center', label: '⬆ Center Back', icon: '🎯' },
                  { value: 'background', label: '🔙 Background', icon: '🌄' }
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => setIntegrationData(prev => ({ ...prev, placement: option.value as any }))}
                    className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                      integrationData.placement === option.value
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-gray-200 hover:border-purple-300 text-gray-700'
                    }`}
                  >
                    <div className="text-lg mb-1">{option.icon}</div>
                    {option.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Advanced Settings */}
            {showAdvanced && (
              <div className="space-y-4 pt-4 border-t border-gray-200">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Integration Style
                  </label>
                  <select
                    value={integrationData.integrationStyle}
                    onChange={(e) => setIntegrationData(prev => ({ ...prev, integrationStyle: e.target.value as any }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="polaroid">Polaroid Aesthetic</option>
                    <option value="vintage">Vintage Film</option>
                    <option value="natural">Natural/Modern</option>
                  </select>
                </div>

                <div>
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={integrationData.lightingMatch}
                      onChange={(e) => setIntegrationData(prev => ({ ...prev, lightingMatch: e.target.checked }))}
                      className="w-4 h-4 text-purple-600"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Match lighting conditions
                    </span>
                  </label>
                  <p className="text-xs text-gray-500 ml-7 mt-1">
                    Automatically adjust shadows and color temperature
                  </p>
                </div>
              </div>
            )}

            {/* Integration Button */}
            <button
              onClick={handleIntegrateFriend}
              disabled={!integrationData.originalPhoto || !integrationData.friendPhoto || !integrationData.friendDescription.trim() || isProcessing}
              className="w-full mt-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed font-polaroid font-semibold flex items-center justify-center space-x-2 transition-all"
            >
              {isProcessing ? (
                <>
                  <RotateCw size={20} className="animate-spin" />
                  <span>Integrating Friend...</span>
                </>
              ) : (
                <>
                  <Zap size={20} />
                  <span>Add Friend to Photo</span>
                </>
              )}
            </button>
          </div>

          {/* Results Panel */}
          {integrationData.result && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 font-polaroid flex items-center space-x-2">
                <Sparkles size={24} />
                <span>Integration Result</span>
              </h3>

              <div className="relative">
                <Image
                  src={integrationData.result}
                  alt="Integrated photo"
                  width={500}
                  height={400}
                  className="w-full rounded-lg shadow-md object-cover"
                />
              </div>

              <div className="flex space-x-3 mt-4">
                <button className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center space-x-2">
                  <Download size={16} />
                  <span>Download</span>
                </button>
                <button 
                  onClick={resetInterface}
                  className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Start Over
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Polaroid Developing Animation */}
      <PolaroidDevelopingAnimation
        isVisible={isProcessing}
        progress={progress}
        stage={stage}
      />

      {/* Tips Section */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 font-polaroid text-gray-800">
          💡 Tips for Best Results
        </h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
          <div>
            <h4 className="font-semibold mb-2">Photo Quality:</h4>
            <ul className="space-y-1 text-xs">
              <li>• Use high-resolution images (1024px+)</li>
              <li>• Ensure good lighting in both photos</li>
              <li>• Avoid heavily shadowed or blurry images</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">Description Tips:</h4>
            <ul className="space-y-1 text-xs">
              <li>• Include clothing colors and styles</li>
              <li>• Mention hair color and style</li>
              <li>• Note any distinctive features</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}