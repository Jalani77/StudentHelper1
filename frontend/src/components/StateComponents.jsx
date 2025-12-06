import { AlertCircle, RefreshCw, Home } from 'lucide-react'
import { Button } from './ui'

export function ErrorState({ title, message, onRetry, onHome }) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center max-w-md px-4">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
          <AlertCircle className="h-8 w-8 text-red-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {title || 'Something went wrong'}
        </h2>
        <p className="text-gray-600 mb-6">
          {message || 'An unexpected error occurred. Please try again.'}
        </p>
        <div className="flex items-center justify-center space-x-3">
          {onRetry && (
            <Button variant="primary" onClick={onRetry}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          )}
          {onHome && (
            <Button variant="outline" onClick={onHome}>
              <Home className="h-4 w-4 mr-2" />
              Go Home
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export function EmptyState({ icon: Icon, title, message, action }) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center max-w-md px-4">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
          {Icon && <Icon className="h-8 w-8 text-gray-400" />}
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {title}
        </h2>
        <p className="text-gray-600 mb-6">
          {message}
        </p>
        {action}
      </div>
    </div>
  )
}

export function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <div className="spinner mb-4 mx-auto" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  )
}
