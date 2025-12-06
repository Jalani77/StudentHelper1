import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button, Spinner } from '../components/ui'
import toast from 'react-hot-toast'
import { apiClient } from '../api/client'
import { useEvalStore } from '../store'

export default function UploadEval() {
  const navigate = useNavigate()
  const { setEvalData } = useEvalStore()
  const [file, setFile] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [parsedData, setParsedData] = useState(null)
  
  const onDrop = useCallback((acceptedFiles) => {
    const uploadedFile = acceptedFiles[0]
    if (uploadedFile) {
      setFile(uploadedFile)
      setParsedData(null)
    }
  }, [])
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/html': ['.html', '.htm'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1,
    multiple: false
  })
  
  const removeFile = () => {
    setFile(null)
    setParsedData(null)
  }
  
  const handleProcess = async () => {
    if (!file) return
    
    setIsProcessing(true)
    
    try {
      const response = await apiClient.uploadEval(file)
      const data = response.data
      
      setParsedData(data)
      
      toast.success('Degree evaluation parsed successfully!')
    } catch (error) {
      console.error('Upload error:', error)
      // Fallback to mock data for development
      const mockData = {
        remainingCredits: 45,
        courses: [
          { code: 'CSC 1301', title: 'Principles of Computer Science I', credits: 3 },
          { code: 'MATH 2211', title: 'Calculus I', credits: 4 },
          { code: 'ENGL 1102', title: 'English Composition II', credits: 3 },
          { code: 'HIST 2110', title: 'Survey of United States History I', credits: 3 },
        ]
      }
      setParsedData(mockData)
      toast.success('Using mock data for development')
    } finally {
      setIsProcessing(false)
    }
  }
  
  const handleContinue = () => {
    if (!parsedData) return
    setEvalData(parsedData)
    navigate('/preferences')
  }
  
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Upload Your Degree Evaluation
          </h1>
          <p className="text-lg text-gray-600">
            We'll extract your remaining course requirements automatically
          </p>
        </div>
        
        {/* Upload Area */}
        {!file && (
          <div
            {...getRootProps()}
            className={`card-hover cursor-pointer border-2 border-dashed transition-all duration-200 ${
              isDragActive
                ? 'border-primary-600 bg-primary-50 scale-[1.02]'
                : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getInputProps()} />
            
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-100 rounded-full mb-6">
                <Upload className="h-10 w-10 text-primary-600" />
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {isDragActive ? 'Drop your file here' : 'Drag & drop your evaluation'}
              </h3>
              <p className="text-gray-600 mb-6">
                or click to browse from your computer
              </p>
              
              <Button variant="outline" type="button">
                Choose File
              </Button>
              
              <p className="text-sm text-gray-500 mt-4">
                Supported formats: PDF, HTML, Image (PNG, JPG)
              </p>
            </div>
          </div>
        )}
        
        {/* File Preview */}
        {file && !parsedData && (
          <div className="card animate-scale-in">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-start space-x-4 flex-1">
                <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FileText className="h-6 w-6 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              
              <button
                onClick={removeFile}
                className="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-150 flex-shrink-0"
                disabled={isProcessing}
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1 text-sm text-blue-800">
                  <p className="font-medium mb-1">How to get your degree evaluation:</p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>Log in to PAWS</li>
                    <li>Go to Student Services → Degree Evaluation</li>
                    <li>Run your evaluation and save as PDF or HTML</li>
                  </ol>
                </div>
              </div>
            </div>
            
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={handleProcess}
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Process Evaluation
                </>
              )}
            </Button>
          </div>
        )}
        
        {/* Parsed Results */}
        {parsedData && (
          <div className="space-y-6 animate-slide-up">
            <div className="card">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Evaluation Processed
                  </h3>
                  <p className="text-sm text-gray-600">
                    Found {parsedData.courses.length} remaining courses
                  </p>
                </div>
              </div>
              
              <div className="bg-primary-50 rounded-xl p-6 mb-6">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-2">Remaining Credits</p>
                  <p className="text-4xl font-bold text-primary-600">
                    {parsedData.remainingCredits}
                  </p>
                </div>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Required Courses:</h4>
                {parsedData.courses.map((course, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{course.code}</p>
                      <p className="text-sm text-gray-600">{course.title}</p>
                    </div>
                    <span className="badge-primary">
                      {course.credits} credits
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="lg"
                className="flex-1"
                onClick={removeFile}
              >
                Upload Different File
              </Button>
              <Button
                variant="primary"
                size="lg"
                className="flex-1"
                onClick={handleContinue}
              >
                Continue to Preferences →
              </Button>
            </div>
          </div>
        )}
        
        {/* Help Section */}
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-600">
            Need help?{' '}
            <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
              View tutorial
            </a>
            {' '}or{' '}
            <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
              watch demo
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
