'use client'

import { Download } from 'lucide-react'
import { Button } from './Button'

interface DownloadButtonProps {
  url: string
  filename: string
}

export default function DownloadButton({ url, filename }: DownloadButtonProps) {
  const handleDownload = async () => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('Failed to download:', error)
    }
  }

  return (
    <div className="absolute top-2 right-2">
      <Button
        variant="secondary"
        size="small"
        onClick={handleDownload}
        className="p-2 bg-white/90"
      >
        <Download className="w-4 h-4" />
      </Button>
    </div>
  )
}
