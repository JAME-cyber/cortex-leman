'use client'

import { useState } from 'react'
import ComplianceForm from '@/components/ComplianceForm'
import ResultDisplay from '@/components/ResultDisplay'
import { ComplianceResult } from '@/types/compliance'
import { Shield, Zap, Lock, FileText } from 'lucide-react'

export default function Home() {
  const [result, setResult] = useState<ComplianceResult | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const handleGenerate = async (data: {
    brief: string
    platforms: string[]
    imageCount: number
    tone: string
  }) => {
    setIsGenerating(true)
    setResult(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      const responseData = await response.json()

      if (response.ok) {
        setResult(responseData)
      } else {
        console.error('Error:', responseData.error)
        alert('Erreur lors de la génération: ' + (responseData.error || 'Erreur inconnue'))
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Erreur de connexion à l\'API')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Cortex Leman</h1>
                <p className="text-sm text-gray-600">Compliance Generator</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 text-green-600">
                <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                <span className="text-sm font-medium">API Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Générez vos posts de conformité
            <span className="gradient-text"> en 60 secondes</span>
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Créez du contenu professionnel RGPD/IA pour vos réseaux sociaux sans expertise juridique ou marketing
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-xl p-6 card-shadow">
            <div className="flex items-center space-x-3 mb-3">
              <div className="bg-blue-100 p-2 rounded-lg">
                <Zap className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Rapide</h3>
            </div>
            <p className="text-gray-600">
              Générez des posts professionnels en moins de 60 secondes
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 card-shadow">
            <div className="flex items-center space-x-3 mb-3">
              <div className="bg-green-100 p-2 rounded-lg">
                <Shield className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Conforme</h3>
            </div>
            <p className="text-gray-600">
              Validé par Le Gardien des Normes pour garantir la conformité RGPD
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 card-shadow">
            <div className="flex items-center space-x-3 mb-3">
              <div className="bg-purple-100 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Professionnel</h3>
            </div>
            <p className="text-gray-600">
              Contenu de qualité généré par Le Narrateur Augmenté
            </p>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-xl p-6 card-shadow">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">
              Créez votre post
            </h3>
            <ComplianceForm
              onSubmit={handleGenerate}
              isGenerating={isGenerating}
            />
          </div>

          <div className="bg-white rounded-xl p-6 card-shadow">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">
              Résultat
            </h3>
            <ResultDisplay result={result} isGenerating={isGenerating} />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              © 2026 Cortex Leman - Audit RGPD-IA PME FR-CH
            </p>
            <div className="flex items-center space-x-2">
              <Lock className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">Données sécurisées</span>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
