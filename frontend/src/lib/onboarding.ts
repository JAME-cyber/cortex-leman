/**
 * Cortex Leman v5 — Onboarding API
 */
import { apiFetch } from './api'

export const onboarding = {
  listVerticals: () =>
    apiFetch<{ verticals: VerticalPreview[] }>('/api/v1/onboarding/verticals'),

  previewVertical: (vertical: string) =>
    apiFetch<VerticalPreview>(`/api/v1/onboarding/verticals/${vertical}`),

  setup: (data: OnboardingSetupData) =>
    apiFetch<OnboardingResult>('/api/v1/onboarding/setup', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  status: () =>
    apiFetch('/api/v1/onboarding/status'),
}

export interface VerticalPreview {
  vertical: string
  mode: 'standard' | 'haute_protection'
  ai_act_risk: string
  agents: { id: string; role: string; autonomy: string; guardrails: number }[]
  rules_count: number
  data_residency_default: string
  encryption: string
  workflows: number
  special_notes: string
  allowed_llm_modes: string[]
}

export interface OnboardingSetupData {
  identity: {
    full_name: string
    email: string
    organization: string
    size: '1-5' | '6-20' | '21-50' | '50+'
  }
  vertical: string
  compliance: {
    data_residency: 'EU' | 'CH' | 'EU_CH'
    encryption: 'AES-256' | 'ChaCha20'
    llm_mode: 'cloud' | 'local' | 'hybrid'
  }
  security: {
    admin_password: string
    two_factor?: 'totp' | 'sms'
    invites?: { email: string; role: string }[]
  }
}

export interface OnboardingResult {
  status: string
  tenant_id: string
  admin_user_id: string
  vertical: string
  mode: string
  rules_loaded: number
  agents_created: number
  workflows_installed: number
  vault_created: boolean
  journal_initialized: boolean
  regulatory_seeded: number
  errors: string[]
  first_message: string
}
