'use client'

import { ComplianceResult } from '@/types/compliance'
import { CopyButton } from './CopyButton'
import { DownloadButton } from './DownloadButton'
import { ValidationBadge } from './ValidationBadge'
import { LoadingSpinner } from './LoadingSpinner'
import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react'

interface ResultDisplayProps {
  result: ComplianceResult | null
  isGenerating: boolean
}

export default function ResultDisplay({ result, isGenerating }: ResultDisplayProps) {
  if (isGenerating) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <LoadingSpinner size="large" />
        <div className="text-center">
          <p className="text-lg font-medium text-gray-900">Génération en cours...</p>
          <p className="text-sm text-gray-600 mt-1">
            Cela peut prendre jusqu'à 60 secondes
          </p>
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="bg-gray-100 rounded-full p-4 mb-4">
          <Clock className="w-8 h-8 text-gray-400" />
        </div>
        <p className="text-gray-600">
          Remplissez le formulaire et cliquez sur "Générer le post"
        </p>
      </div>
    )
  }

  if (!result.success) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="bg-red-100 rounded-full p-4 mb-4">
          <XCircle className="w-8 h-8 text-red-600" />
        </div>
        <p className="text-gray-900 font-medium">Erreur de génération</p>
        <p className="text-sm text-red-600 mt-1">
          {result.error || 'Une erreur est survenue'}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Success Message */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3">
        <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
        <div>
          <p className="text-sm font-medium text-green-900">
            Génération terminée avec succès
          </p>
          <p className="text-xs text-green-700 mt-1">
            {new Date(result.timestamp).toLocaleString('fr-FR')}
          </p>
        </div>
      </div>

      {/* Posts */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Posts générés</h4>
        {Object.entries(result.posts).map(([platform, text]) => (
          <div key={platform} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h5 className="font-medium text-gray-900 capitalize">{platform}</h5>
              <div className="flex items-center space-x-2">
                <ValidationBadge
                  isValid={result.validation[platform]?.is_valid || false}
                  confidence={result.validation[platform]?.confidence || 0}
                />
                <CopyButton text={text} />
              </div>
            </div>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{text}</p>
          </div>
        ))}
      </div>

      {/* Images */}
      {result.images && result.images.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-900">Images générées</h4>
          <div className="grid grid-cols-2 gap-4">
            {result.images.map((image) => (
              <div key={image.index} className="relative">
                <img
                  src={image.url}
                  alt={`Image ${image.index} (${image.type})`}
                  className="w-full h-48 object-cover rounded-lg border border-gray-200"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent rounded-b-lg p-2">
                  <p className="text-xs text-white font-medium capitalize">
                    {image.type}
                  </p>
                </div>
                <DownloadButton url={image.url} filename={`compliance-image-${image.index}.png`} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Validation Details */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Validation</h4>
        {Object.entries(result.validation).map(([platform, validation]) => (
          <div key={platform} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              {validation.is_valid ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-600" />
              )}
              <div>
                <p className="font-medium text-gray-900 capitalize">{platform}</p>
                <p className="text-xs text-gray-600">
                  Confiance: {(validation.confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {validation.issues && validation.issues.length > 0 && (
              <div className="space-y-2 mt-3">
                {validation.issues.map((issue, index) => (
                  <div
                    key={index}
                    className={`border-l-2 pl-3 ${
                      issue.severity === 'critical' || issue.severity === 'error'
                        ? 'border-red-500'
                        : issue.severity === 'warning'
                        ? 'border-yellow-500'
                        : 'border-blue-500'
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-900">
                      {issue.rule}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {issue.issue}
                    </p>
                    {issue.correction && (
                      <p className="text-xs text-green-700 mt-1">
                        Correction: {issue.correction}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
