'use client'

import { useState } from 'react'
import { Button } from './Button'
import { Label } from './Label'
import { Textarea } from './Textarea'
import { Select } from './Select'
import { Checkbox } from './Checkbox'
import { LoadingSpinner } from './LoadingSpinner'

interface ComplianceFormProps {
  onSubmit: (data: {
    brief: string
    platforms: string[]
    imageCount: number
    tone: string
  }) => void
  isGenerating: boolean
}

export default function ComplianceForm({ onSubmit, isGenerating }: ComplianceFormProps) {
  const [brief, setBrief] = useState('')
  const [platforms, setPlatforms] = useState<string[]>(['linkedin', 'twitter'])
  const [imageCount, setImageCount] = useState(2)
  const [tone, setTone] = useState('professional')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!brief.trim()) {
      alert('Veuillez saisir un brief')
      return
    }

    if (platforms.length === 0) {
      alert('Veuillez sélectionner au moins une plateforme')
      return
    }

    onSubmit({
      brief,
      platforms,
      imageCount,
      tone,
    })
  }

  const handlePlatformChange = (platform: string, checked: boolean) => {
    if (checked) {
      setPlatforms([...platforms, platform])
    } else {
      setPlatforms(platforms.filter(p => p !== platform))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Brief Input */}
      <div>
        <Label htmlFor="brief">Sujet du post</Label>
        <Textarea
          id="brief"
          placeholder="Ex: Nouvelle obligation RGPD pour IA générative"
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          rows={4}
          disabled={isGenerating}
        />
        <p className="mt-2 text-sm text-gray-600">
          Décrivez le sujet de votre post en quelques mots
        </p>
      </div>

      {/* Platforms */}
      <div>
        <Label>Plateformes</Label>
        <div className="space-y-2 mt-2">
          <Checkbox
            id="platform-linkedin"
            label="LinkedIn"
            checked={platforms.includes('linkedin')}
            onChange={(e) => handlePlatformChange('linkedin', e.target.checked)}
            disabled={isGenerating}
          />
          <Checkbox
            id="platform-twitter"
            label="Twitter / X"
            checked={platforms.includes('twitter')}
            onChange={(e) => handlePlatformChange('twitter', e.target.checked)}
            disabled={isGenerating}
          />
        </div>
      </div>

      {/* Image Count */}
      <div>
        <Label htmlFor="image-count">Nombre d'images</Label>
        <Select
          id="image-count"
          value={imageCount.toString()}
          onChange={(e) => setImageCount(parseInt(e.target.value))}
          disabled={isGenerating}
        >
          <option value="1">1 image</option>
          <option value="2">2 images</option>
          <option value="3">3 images</option>
          <option value="4">4 images</option>
        </Select>
      </div>

      {/* Tone */}
      <div>
        <Label htmlFor="tone">Ton du post</Label>
        <Select
          id="tone"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          disabled={isGenerating}
        >
          <option value="professional">Professionnel</option>
          <option value="accessible">Accessible</option>
          <option value="urgent">Urgent</option>
          <option value="educational">Éducatif</option>
        </Select>
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <Button
          type="submit"
          className="w-full"
          disabled={isGenerating}
        >
          {isGenerating ? (
            <span className="flex items-center justify-center space-x-2">
              <LoadingSpinner size="small" />
              <span>Génération en cours...</span>
            </span>
          ) : (
            'Générer le post'
          )}
        </Button>
      </div>
    </form>
  )
}
