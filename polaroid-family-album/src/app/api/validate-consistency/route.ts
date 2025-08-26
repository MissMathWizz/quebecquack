import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'
import path from 'path'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { 
      generateNew = true, 
      referenceDir, 
      resultsFile 
    } = body

    // Validate inputs
    if (!generateNew && !resultsFile) {
      return NextResponse.json(
        { success: false, error: 'Results file required for validation-only mode' },
        { status: 400 }
      )
    }

    // Construct command
    const scriptPath = path.join(process.cwd(), 'scripts', 'run_consistency_test.py')
    let command = `python3 "${scriptPath}"`

    if (referenceDir) {
      command += ` --reference-dir "${referenceDir}"`
    }

    if (!generateNew) {
      command += ` --validate-only --results-file "${resultsFile}"`
    }

    console.log(`Executing: ${command}`)

    // Execute the consistency test pipeline
    const { stdout, stderr } = await execAsync(command, {
      cwd: process.cwd(),
      timeout: 1800000, // 30 minutes timeout
      env: {
        ...process.env,
        REPLICATE_API_TOKEN: process.env.REPLICATE_API_TOKEN
      }
    })

    // Parse results from stdout
    const results = {
      success: true,
      output: stdout,
      errors: stderr || null,
      timestamp: new Date().toISOString()
    }

    return NextResponse.json(results)

  } catch (error) {
    console.error('Consistency validation error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        details: error instanceof Error ? error.stack : null
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Return validation system status and available reports
  try {
    const validationDir = path.join(process.cwd(), 'validation')
    const reportsDir = path.join(validationDir, 'analysis_results')
    
    // Check if directories exist and list recent reports
    const { stdout } = await execAsync(`find "${reportsDir}" -name "*.md" -type f | head -5`, {
      cwd: process.cwd()
    }).catch(() => ({ stdout: '' }))

    const recentReports = stdout.split('\n').filter(Boolean)

    return NextResponse.json({
      success: true,
      validationSystemActive: true,
      recentReports,
      availableFeatures: [
        'Face detection and analysis',
        'Character consistency scoring',
        'Location-based performance metrics',
        'Age variation analysis',
        'Automated report generation',
        'Visualization charts'
      ]
    })

  } catch (error) {
    return NextResponse.json({
      success: false,
      validationSystemActive: false,
      error: error instanceof Error ? error.message : 'System check failed'
    })
  }
}