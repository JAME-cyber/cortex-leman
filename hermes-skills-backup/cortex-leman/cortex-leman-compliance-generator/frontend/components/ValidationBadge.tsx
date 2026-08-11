'use client'

import { CheckCircle, AlertCircle } from 'lucide-react'

interface ValidationBadgeProps {
  isValid: boolean
  confidence: number
}

export default function ValidationBadge({ isValid, confidence }: ValidationBadgeProps) {
  if (isValid) {
    return (
      <div className="flex items-center space-x-1 bg-green-100 px-2 py-1 rounded-full">
        <CheckCircle className="w-4 h-4 text-green-600" />
        <span className="text-xs font-medium text-green-800">
          {(confidence * 100).toFixed(0)}%
        </span>
      </div>
    )
  }

  return (
    <div className="flex items-center space-x-1 bg-yellow-100 px-2 py-1 rounded-full">
      <AlertCircle className="w-4 h-4 text-yellow-600" />
      <span className="text-xs font-medium text-yellow-800">
        {(confidence * 100).toFixed(0)}%
      </span>
    </div>
  )
}
