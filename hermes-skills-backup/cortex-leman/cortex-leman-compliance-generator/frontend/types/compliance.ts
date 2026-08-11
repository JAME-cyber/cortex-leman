export interface ComplianceResult {
  success: boolean
  posts: {
    [platform: string]: string
  }
  images: Array<{
    url: string
    type: string
    index: number
  }>
  validation: {
    [platform: string]: {
      is_valid: boolean
      confidence: number
      issues: Array<{
        rule: string
        severity: string
        description: string
        issue: string
        correction?: string
      }>
      corrected_text?: string
    }
  }
  metadata: {
    brief: string
    platforms: string[]
    image_count: number
    tone: string
  }
  timestamp: string
  error?: string
}

export interface GenerateRequest {
  brief: string
  platforms: string[]
  image_count: number
  tone: string
  enable_validation?: boolean
}
