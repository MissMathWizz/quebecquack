'use client'

import { useState } from 'react'
import { CheckCircle, AlertCircle, BarChart3, Download, Play, Pause } from 'lucide-react'

interface ValidationResults {
  success: boolean
  output: string
  errors?: string
  timestamp: string
}

interface ValidationMetrics {
  totalImages: number
  detectionRate: number
  averageConfidence: number
  highConfidenceCount: number
  lowConfidenceCount: number
}

export default function ConsistencyValidation() {
  const [isRunning, setIsRunning] = useState(false)
  const [results, setResults] = useState<ValidationResults | null>(null)
  const [metrics, setMetrics] = useState<ValidationMetrics | null>(null)
  const [generateNew, setGenerateNew] = useState(true)
  const [referenceDir, setReferenceDir] = useState('')
  const [resultsFile, setResultsFile] = useState('')

  const runValidation = async () => {
    setIsRunning(true)
    setResults(null)
    setMetrics(null)

    try {
      const response = await fetch('/api/validate-consistency', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          generateNew,
          referenceDir: referenceDir || undefined,
          resultsFile: resultsFile || undefined
        })
      })

      const data = await response.json()
      setResults(data)

      // Extract metrics from output if available
      if (data.success && data.output) {
        const metricsMatch = data.output.match(/Total Images: (\d+).*Detection Rate: ([\d.]+)%.*Average Confidence: ([\d.]+)/s)
        if (metricsMatch) {
          setMetrics({
            totalImages: parseInt(metricsMatch[1]),
            detectionRate: parseFloat(metricsMatch[2]) / 100,
            averageConfidence: parseFloat(metricsMatch[3]),
            highConfidenceCount: 0, // Would need to parse from output
            lowConfidenceCount: 0
          })
        }
      }
    } catch (error) {
      setResults({
        success: false,
        output: '',
        errors: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      })
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-800 mb-2 font-polaroid">
          Character Consistency Validation
        </h2>
        <p className="text-lg text-gray-600 font-polaroid">
          Test Ferwanda & Ferwando face consistency across different scenarios
        </p>
      </div>

      {/* Configuration Panel */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold mb-4 font-polaroid">Test Configuration</h3>
        
        <div className="space-y-4">
          {/* Generation Mode */}
          <div>
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={generateNew}
                onChange={(e) => setGenerateNew(e.target.checked)}
                className="w-4 h-4 text-purple-600"
              />
              <span className="font-polaroid">Generate new test photos</span>
            </label>
            <p className="text-sm text-gray-500 ml-7 mt-1">
              Creates photos at QT office, Great Wall, Indonesian Embassy
            </p>
          </div>

          {/* Reference Directory */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Reference Images Directory (Optional)
            </label>
            <input
              type="text"
              value={referenceDir}
              onChange={(e) => setReferenceDir(e.target.value)}
              placeholder="/path/to/reference/images"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
            <p className="text-sm text-gray-500 mt-1">
              Directory containing reference photos for baseline comparison
            </p>
          </div>

          {/* Results File (for validation-only mode) */}
          {!generateNew && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Existing Results File
              </label>
              <input
                type="text"
                value={resultsFile}
                onChange={(e) => setResultsFile(e.target.value)}
                placeholder="/path/to/generation_results.json"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                required={!generateNew}
              />
            </div>
          )}
        </div>

        {/* Run Button */}
        <div className="mt-6">
          <button
            onClick={runValidation}
            disabled={isRunning || (!generateNew && !resultsFile)}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 font-polaroid"
          >
            {isRunning ? (
              <>
                <Pause className="animate-spin" size={20} />
                <span>Running Validation...</span>
              </>
            ) : (
              <>
                <Play size={20} />
                <span>Start Consistency Test</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Progress/Status */}
      {isRunning && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            <div>
              <p className="font-semibold text-blue-800">Running Character Consistency Test</p>
              <p className="text-sm text-blue-600">
                {generateNew ? 'Generating test photos and analyzing consistency...' : 'Analyzing existing photos...'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Results Summary */}
      {metrics && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4 font-polaroid flex items-center space-x-2">
            <BarChart3 size={24} />
            <span>Validation Results</span>
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{metrics.totalImages}</div>
              <div className="text-sm text-gray-600">Total Images</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {(metrics.detectionRate * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Detection Rate</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {metrics.averageConfidence.toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">Avg Confidence</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {metrics.highConfidenceCount}
              </div>
              <div className="text-sm text-gray-600">High Confidence</div>
            </div>
          </div>
        </div>
      )}

      {/* Results Output */}
      {results && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold font-polaroid">
              Test Results
            </h3>
            <div className={`flex items-center space-x-2 ${results.success ? 'text-green-600' : 'text-red-600'}`}>
              {results.success ? (
                <CheckCircle size={20} />
              ) : (
                <AlertCircle size={20} />
              )}
              <span className="font-semibold">
                {results.success ? 'Success' : 'Failed'}
              </span>
            </div>
          </div>

          {/* Output */}
          {results.output && (
            <div className="mb-4">
              <h4 className="font-semibold text-gray-700 mb-2">Output:</h4>
              <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">
                {results.output}
              </pre>
            </div>
          )}

          {/* Errors */}
          {results.errors && (
            <div className="mb-4">
              <h4 className="font-semibold text-red-700 mb-2">Errors:</h4>
              <pre className="bg-red-50 p-4 rounded-lg text-sm overflow-x-auto text-red-700 whitespace-pre-wrap">
                {results.errors}
              </pre>
            </div>
          )}

          {/* Download Reports */}
          {results.success && (
            <div className="border-t pt-4">
              <h4 className="font-semibold text-gray-700 mb-2">Generated Reports:</h4>
              <div className="flex flex-wrap gap-2">
                <button className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                  <Download size={16} />
                  <span>Validation Report</span>
                </button>
                <button className="flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
                  <Download size={16} />
                  <span>Visualization Charts</span>
                </button>
                <button className="flex items-center space-x-2 bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-colors">
                  <Download size={16} />
                  <span>Raw Data</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Test Scenarios Info */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4 font-polaroid">Test Scenarios</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">🏢 QT Office</h4>
            <p className="text-sm text-gray-600">
              Professional business environment with modern office setting and contemporary interior design.
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">🏯 Great Wall</h4>
            <p className="text-sm text-gray-600">
              Tourist photography at the Great Wall of China with ancient architecture and mountain landscapes.
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">🏛️ Indonesian Embassy</h4>
            <p className="text-sm text-gray-600">
              Formal diplomatic setting with official government atmosphere and Indonesian cultural elements.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}