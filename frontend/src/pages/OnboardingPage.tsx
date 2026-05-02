/**
 * Cortex Leman v5 — Onboarding Page
 * Design Owner: même palette, glass cards, glow orbs, dark navy
 * Architecture: 6-step wizard avec state machine (inspiré Danswer/Onyx)
 */
import { useState, useCallback, useMemo } from 'react'
import { onboarding, type OnboardingSetupData, type VerticalPreview } from '../lib/onboarding'

// ═══════════════════════════════════════════════════════════════
// DESIGN CONSTANTS (même palette que LandingPage)
// ═══════════════════════════════════════════════════════════════

const VERTICALS = [
  { id: 'comptable', icon: '📊', label: 'Expert-Comptable', color: '#22d3ee', desc: 'TVA, seuils AFC, plan comptable', risk: 'limited' },
  { id: 'avocat',    icon: '⚖️',  label: 'Avocat',          color: '#a78bfa', desc: 'Secret professionnel Art. 321 CP', risk: 'high' },
  { id: 'sante',     icon: '🏥',  label: 'Santé',           color: '#34d399', desc: 'LPM, HDS, consentement éclairé', risk: 'high' },
  { id: 'banque',    icon: '🏦',  label: 'Banque',          color: '#fbbf24', desc: 'Secret bancaire Art. 47 LB, KYC', risk: 'high' },
  { id: 'startup',   icon: '🚀',  label: 'Startup',         color: '#fb923c', desc: 'DPIA, AI Act, RGPD', risk: 'limited' },
  { id: 'rh',        icon: '👥',  label: 'Ressources Humaines', color: '#fb7185', desc: 'Anti-discrimination, Art. 22 RGPD', risk: 'high' },
] as const

const STEP_META = [
  { id: 'welcome',    title: 'Bienvenue',           pct: 5 },
  { id: 'identity',   title: 'Votre profil',        pct: 20 },
  { id: 'vertical',   title: 'Votre activité',      pct: 40 },
  { id: 'compliance', title: 'Conformité',           pct: 60 },
  { id: 'security',   title: 'Sécurité',             pct: 80 },
  { id: 'activation', title: 'Activation',           pct: 100 },
] as const

type StepId = typeof STEP_META[number]['id']

interface FormData {
  jurisdiction: 'FR' | 'CH' | 'FR_CH'
  fullName: string
  email: string
  organization: string
  orgSize: '1-5' | '6-20' | '21-50' | '50+'
  vertical: string
  dataResidency: 'EU' | 'CH' | 'EU_CH'
  encryption: 'AES-256' | 'ChaCha20'
  llmMode: 'cloud' | 'local' | 'hybrid'
  adminPassword: string
  confirmPassword: string
  twoFactor: '' | 'totp' | 'sms'
  invites: { email: string; role: string }[]
}

const INITIAL_DATA: FormData = {
  jurisdiction: 'FR_CH',
  fullName: '',
  email: '',
  organization: '',
  orgSize: '6-20',
  vertical: '',
  dataResidency: 'EU',
  encryption: 'AES-256',
  llmMode: 'cloud',
  adminPassword: '',
  confirmPassword: '',
  twoFactor: '',
  invites: [],
}

// ═══════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════

export function OnboardingPage({ onComplete }: { onComplete: (result: any) => void }) {
  const [step, setStep] = useState<StepId>('welcome')
  const [data, setData] = useState<FormData>(INITIAL_DATA)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<string[]>([])
  const [preview, setPreview] = useState<VerticalPreview | null>(null)
  const [result, setResult] = useState<any>(null)

  const stepIndex = STEP_META.findIndex(s => s.id === step)
  const isHighRisk = ['avocat', 'sante', 'banque'].includes(data.vertical)

  const update = useCallback(<K extends keyof FormData>(key: K, val: FormData[K]) => {
    setData(prev => ({ ...prev, [key]: val }))
    setErrors([])
  }, [])

  // Load vertical preview when selected
  const loadPreview = useCallback(async (vertical: string) => {
    try {
      const p = await onboarding.previewVertical(vertical)
      setPreview(p)
    } catch { setPreview(null) }
  }, [])

  const next = useCallback(() => {
    const idx = stepIndex
    if (idx < STEP_META.length - 1) setStep(STEP_META[idx + 1].id)
  }, [stepIndex])

  const prev = useCallback(() => {
    const idx = stepIndex
    if (idx > 0) setStep(STEP_META[idx - 1].id)
  }, [stepIndex])

  // Validate current step
  const canNext = useMemo(() => {
    switch (step) {
      case 'welcome': return true
      case 'identity': return !!data.fullName && !!data.email && !!data.organization
      case 'vertical': return !!data.vertical
      case 'compliance': {
        if (isHighRisk && data.llmMode === 'cloud') return false
        if (data.vertical === 'avocat' && data.dataResidency === 'EU') return false
        return true
      }
      case 'security': {
        return data.adminPassword.length >= 8 && data.adminPassword === data.confirmPassword
      }
      default: return false
    }
  }, [step, data, isHighRisk])

  // Submit onboarding
  const submit = useCallback(async () => {
    setLoading(true)
    setErrors([])
    try {
      const payload: OnboardingSetupData = {
        identity: {
          full_name: data.fullName,
          email: data.email,
          organization: data.organization,
          size: data.orgSize,
        },
        vertical: data.vertical,
        compliance: {
          data_residency: data.dataResidency,
          encryption: data.encryption,
          llm_mode: data.llmMode,
        },
        security: {
          admin_password: data.adminPassword,
          two_factor: data.twoFactor || undefined,
          invites: data.invites,
        },
      }
      const res = await onboarding.setup(payload)
      setResult(res)
      if (res.errors?.length) setErrors(res.errors)
    } catch (e: any) {
      const msg = e?.message || 'Erreur lors de l\'activation'
      try {
        const parsed = JSON.parse(msg)
        setErrors(Array.isArray(parsed.errors) ? parsed.errors : [msg])
      } catch { setErrors([msg]) }
    } finally { setLoading(false) }
  }, [data])

  // ═══════════════════════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════════════════════

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', position: 'relative', overflow: 'hidden' }}>
      {/* Grid background */}
      <div className="grid-bg" />

      {/* Glow orbs */}
      <div className="glow-orb cyan" style={{ top: '5%', right: '10%' }} />
      <div className="glow-orb violet" style={{ bottom: '10%', left: '5%' }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 680, margin: '0 auto', padding: '3rem 1.5rem', minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>

        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '0.5rem', background: 'linear-gradient(135deg, var(--cyan), var(--emerald))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 700, color: 'var(--bg)' }}>CL</div>
          <div>
            <div className="mono" style={{ fontSize: '0.9375rem', fontWeight: 700 }}>Cortex Leman</div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Configuration de votre infrastructure</div>
          </div>
        </div>

        {/* Progress bar */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            {STEP_META.map((s, i) => (
              <div key={s.id} style={{ flex: 1, textAlign: 'center' }}>
                <div style={{
                  width: 28, height: 28, borderRadius: '50%', margin: '0 auto 0.375rem',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.6875rem', fontWeight: 700,
                  background: i < stepIndex ? 'var(--emerald)' : i === stepIndex ? 'var(--cyan)' : 'rgba(30,41,59,0.8)',
                  color: i <= stepIndex ? 'var(--bg)' : 'var(--text-dim)',
                  border: i === stepIndex ? '2px solid var(--cyan)' : '2px solid transparent',
                  transition: 'all 0.3s ease',
                }}>
                  {i < stepIndex ? '✓' : i + 1}
                </div>
                <div style={{ fontSize: '0.5625rem', color: i <= stepIndex ? 'var(--text-muted)' : 'var(--text-dim)', fontWeight: 500 }}>
                  {s.title}
                </div>
              </div>
            ))}
          </div>
          <div style={{ height: 3, background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{
              height: '100%', borderRadius: 2, transition: 'width 0.5s ease',
              background: 'linear-gradient(90deg, var(--cyan), var(--emerald))',
              width: `${STEP_META[stepIndex].pct}%`,
            }} />
          </div>
        </div>

        {/* Step content */}
        <div className="glass" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
          {step === 'welcome' && <WelcomeStep data={data} update={update} />}
          {step === 'identity' && <IdentityStep data={data} update={update} />}
          {step === 'vertical' && <VerticalStep data={data} update={update} preview={preview} loadPreview={loadPreview} />}
          {step === 'compliance' && <ComplianceStep data={data} update={update} preview={preview} isHighRisk={isHighRisk} />}
          {step === 'security' && <SecurityStep data={data} update={update} />}
          {step === 'activation' && <ActivationStep data={data} result={result} loading={loading} errors={errors} submit={submit} onComplete={onComplete} />}
        </div>

        {/* Errors */}
        {errors.length > 0 && step !== 'activation' && (
          <div style={{ marginBottom: '1rem' }}>
            {errors.map((e, i) => (
              <div key={i} style={{ padding: '0.625rem 1rem', background: 'rgba(251,113,133,0.08)', border: '1px solid rgba(251,113,133,0.2)', borderRadius: '0.5rem', fontSize: '0.8125rem', color: 'var(--rose)', marginBottom: '0.375rem' }}>
                ❌ {e}
              </div>
            ))}
          </div>
        )}

        {/* Navigation */}
        {step !== 'activation' && (
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'space-between' }}>
            <button onClick={prev} className="btn btn-secondary" style={{ opacity: stepIndex === 0 ? 0.3 : 1, pointerEvents: stepIndex === 0 ? 'none' : 'auto' }}>
              ← Retour
            </button>
            <button onClick={next} disabled={!canNext} className="btn btn-primary" style={{ opacity: canNext ? 1 : 0.4 }}>
              {stepIndex === STEP_META.length - 2 ? 'Activer →' : 'Suivant →'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// STEP 0: WELCOME
// ═══════════════════════════════════════════════════════════════

function WelcomeStep({ data, update }: { data: FormData; update: (k: any, v: any) => void }) {
  return (
    <div>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.75rem' }}>
        Bienvenue dans Cortex Leman
      </h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '2rem', lineHeight: 1.7 }}>
        Votre infrastructure de confiance IA en 5 minutes.
        Choisissez d'abord votre juridiction — cela configure le data residency par défaut.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
        {([
          { value: 'FR' as const, flag: '🇫🇷', label: 'France', residency: 'EU' },
          { value: 'CH' as const, flag: '🇨🇭', label: 'Suisse', residency: 'CH' },
          { value: 'FR_CH' as const, flag: '🇫🇷🇨🇭', label: 'FR-CH', residency: 'EU_CH' },
        ]).map(j => (
          <button key={j.value} onClick={() => { update('jurisdiction', j.value); update('dataResidency', j.residency as any) }}
            className="glass" style={{
            padding: '1.25rem', cursor: 'pointer', textAlign: 'center',
            border: data.jurisdiction === j.value ? `2px solid var(--cyan)` : '1px solid var(--border)',
            background: data.jurisdiction === j.value ? 'rgba(34,211,238,0.06)' : 'transparent',
            transition: 'all 0.2s',
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{j.flag}</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{j.label}</div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>Residency: {j.residency}</div>
          </button>
        ))}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// STEP 1: IDENTITY
// ═══════════════════════════════════════════════════════════════

function IdentityStep({ data, update }: { data: FormData; update: (k: any, v: any) => void }) {
  return (
    <div>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>👤 Votre profil</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>
        Ces informations seront utilisées pour configurer votre espace et le journal d'audit.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Nom complet</label>
          <input value={data.fullName} onChange={e => update('fullName', e.target.value)} placeholder="Jean Dupont" style={inputStyle} />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Email professionnel</label>
          <input value={data.email} onChange={e => update('email', e.target.value)} placeholder="jean@dupont-comptable.fr" type="email" style={inputStyle} />
          {data.vertical === 'avocat' && (
            <div style={{ fontSize: '0.6875rem', color: 'var(--amber)', marginTop: '0.25rem' }}>
              ⚠️ Art. 321 CP: adresse professionnelle obligatoire (pas gmail, outlook, etc.)
            </div>
          )}
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Nom du cabinet / organisation</label>
          <input value={data.organization} onChange={e => update('organization', e.target.value)} placeholder="Dupont & Associés" style={inputStyle} />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.375rem' }}>Taille de l'organisation</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {(['1-5', '6-20', '21-50', '50+'] as const).map(s => (
              <button key={s} onClick={() => update('orgSize', s)} style={{
                flex: 1, padding: '0.5rem', borderRadius: '0.5rem', fontSize: '0.8125rem', fontWeight: 600,
                border: data.orgSize === s ? '2px solid var(--cyan)' : '1px solid var(--border)',
                background: data.orgSize === s ? 'rgba(34,211,238,0.06)' : 'transparent',
                color: data.orgSize === s ? 'var(--cyan)' : 'var(--text-muted)', cursor: 'pointer',
                transition: 'all 0.2s',
              }}>
                {s}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// STEP 2: VERTICAL
// ═══════════════════════════════════════════════════════════════

function VerticalStep({ data, update, preview, loadPreview }: {
  data: FormData; update: (k: any, v: any) => void; preview: VerticalPreview | null; loadPreview: (v: string) => void
}) {
  return (
    <div>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Choisissez votre domaine d'activité</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>
        Cela configure automatiquement les règles de conformité, le mode de protection et les agents.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {VERTICALS.map(v => {
          const selected = data.vertical === v.id
          const isHigh = v.risk === 'high'
          return (
            <button key={v.id} onClick={() => { update('vertical', v.id); loadPreview(v.id) }}
              className="glass" style={{
              padding: '1rem', cursor: 'pointer', textAlign: 'left',
              border: selected ? `2px solid ${v.color}` : '1px solid var(--border)',
              background: selected ? `${v.color}08` : 'transparent',
              transition: 'all 0.2s', position: 'relative',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '1.5rem' }}>{v.icon}</span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{v.label}</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{v.desc}</div>
                </div>
              </div>
              {isHigh && (
                <div style={{ position: 'absolute', top: '0.5rem', right: '0.5rem' }}>
                  <span style={{ fontSize: '0.5625rem', padding: '0.125rem 0.5rem', borderRadius: 999, background: 'rgba(251,113,133,0.1)', color: 'var(--rose)', border: '1px solid rgba(251,113,133,0.2)', fontWeight: 600 }}>
                    HAUTE PROTECTION
                  </span>
                </div>
              )}
            </button>
          )
        })}
      </div>

      {/* Preview panel */}
      {preview && (
        <div style={{ background: 'rgba(30,41,59,0.4)', borderRadius: '0.75rem', padding: '1rem', border: '1px solid var(--border)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--cyan)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            📋 Ce qui sera installé
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
            <div style={previewItemStyle}>
              <span style={{ color: 'var(--cyan)', fontWeight: 700 }}>{preview.rules_count}</span> règles JsonLogic
            </div>
            <div style={previewItemStyle}>
              <span style={{ color: 'var(--emerald)', fontWeight: 700 }}>{preview.agents.length}</span> agents spécialisés
            </div>
            <div style={previewItemStyle}>
              Mode: <span style={{ color: preview.mode === 'haute_protection' ? 'var(--rose)' : 'var(--cyan)', fontWeight: 600 }}>{preview.mode.replace('_', ' ')}</span>
            </div>
            <div style={previewItemStyle}>
              Risk: <span style={{ fontWeight: 600, color: preview.ai_act_risk === 'high' ? 'var(--amber)' : 'var(--emerald)' }}>{preview.ai_act_risk}</span>
            </div>
          </div>
          <div style={{ marginTop: '0.75rem', fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
            Agents: {preview.agents.map(a => a.role).join(' · ')}
          </div>
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// STEP 3: COMPLIANCE
// ═══════════════════════════════════════════════════════════════

function ComplianceStep({ data, update, preview, isHighRisk }: {
  data: FormData; update: (k: any, v: any) => void; preview: VerticalPreview | null; isHighRisk: boolean
}) {
  return (
    <div>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>🛡️ Conformité & Protection</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>
        Configuré automatiquement selon votre vertical. Modifiable par un expert ensuite.
      </p>

      {isHighRisk && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(251,191,36,0.06)', border: '1px solid rgba(251,191,36,0.2)', borderRadius: '0.5rem', fontSize: '0.8125rem', color: 'var(--amber)', marginBottom: '1.25rem', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
          <span>⚠️</span>
          <div>
            <strong>Mode Haute Protection activé</strong> — secret professionnel oblige.
            Certains réglages sont restreints pour garantir la conformité.
          </div>
        </div>
      )}

      {/* Data Residency */}
      <div style={{ marginBottom: '1.25rem' }}>
        <label style={labelStyle}>📍 Data Residency</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {(['EU', 'CH', 'EU_CH'] as const).map(r => {
            const disabled = isHighRisk && r === 'EU'
            return (
              <button key={r} onClick={() => !disabled && update('dataResidency', r)} disabled={disabled} style={{
                flex: 1, padding: '0.625rem', borderRadius: '0.5rem', fontSize: '0.8125rem', fontWeight: 600,
                border: data.dataResidency === r ? '2px solid var(--cyan)' : '1px solid var(--border)',
                background: data.dataResidency === r ? 'rgba(34,211,238,0.06)' : disabled ? 'rgba(30,41,59,0.3)' : 'transparent',
                color: data.dataResidency === r ? 'var(--cyan)' : disabled ? 'var(--text-dim)' : 'var(--text-muted)',
                cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.4 : 1,
                textDecoration: disabled ? 'line-through' : 'none', transition: 'all 0.2s',
              }}>
                {r === 'EU' ? '🇪🇺 EU' : r === 'CH' ? '🇨🇭 CH' : '🇪🇺🇨🇭 EU+CH'}
              </button>
            )
          })}
        </div>
      </div>

      {/* Encryption */}
      <div style={{ marginBottom: '1.25rem' }}>
        <label style={labelStyle}>🔐 Chiffrement au repos</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {(['AES-256', 'ChaCha20'] as const).map(e => (
            <button key={e} onClick={() => update('encryption', e)} style={{
              flex: 1, padding: '0.625rem', borderRadius: '0.5rem', fontSize: '0.8125rem', fontWeight: 600,
              border: data.encryption === e ? '2px solid var(--emerald)' : '1px solid var(--border)',
              background: data.encryption === e ? 'rgba(52,211,153,0.06)' : 'transparent',
              color: data.encryption === e ? 'var(--emerald)' : 'var(--text-muted)',
              cursor: 'pointer', transition: 'all 0.2s',
            }}>
              {e === 'AES-256' ? '✓ AES-256 (recommandé)' : e}
            </button>
          ))}
        </div>
      </div>

      {/* LLM Mode */}
      <div style={{ marginBottom: '1.25rem' }}>
        <label style={labelStyle}>🤖 Mode IA</label>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {([
            { value: 'cloud' as const, label: '☁️ Cloud', desc: 'OpenRouter' },
            { value: 'local' as const, label: '🏠 Local', desc: 'Ollama' },
            { value: 'hybrid' as const, label: '🔀 Hybride', desc: 'Cloud + Local' },
          ]).map(m => {
            const disabled = isHighRisk && m.value === 'cloud'
            return (
              <button key={m.value} onClick={() => !disabled && update('llmMode', m.value)} disabled={disabled} style={{
                flex: 1, padding: '0.625rem', borderRadius: '0.5rem',
                border: data.llmMode === m.value ? '2px solid var(--violet)' : '1px solid var(--border)',
                background: data.llmMode === m.value ? 'rgba(167,139,250,0.06)' : disabled ? 'rgba(30,41,59,0.3)' : 'transparent',
                color: data.llmMode === m.value ? 'var(--violet)' : disabled ? 'var(--text-dim)' : 'var(--text-muted)',
                cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.4 : 1,
                textDecoration: disabled ? 'line-through' : 'none', transition: 'all 0.2s',
              }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600 }}>{m.label}</div>
                <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{m.desc}</div>
              </button>
            )
          })}
        </div>
        {isHighRisk && (
          <div style={{ fontSize: '0.6875rem', color: 'var(--amber)', marginTop: '0.375rem' }}>
            ⚠️ Cloud interdit — secret professionnel exige local ou hybride
          </div>
        )}
      </div>

      {/* Rules loaded */}
      {preview && (
        <div style={{ background: 'rgba(52,211,153,0.04)', border: '1px solid rgba(52,211,153,0.15)', borderRadius: '0.5rem', padding: '0.75rem 1rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--emerald)', marginBottom: '0.5rem' }}>
            ✅ {preview.rules_count} règles JsonLogic chargées automatiquement
          </div>
          <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
            Journal WORM · Vault chiffré · Guardrails 3 couches · Audit trail
          </div>
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// STEP 4: SECURITY
// ═══════════════════════════════════════════════════════════════

function SecurityStep({ data, update }: { data: FormData; update: (k: any, v: any) => void }) {
  const strength = useMemo(() => {
    const p = data.adminPassword
    let s = 0
    if (p.length >= 8) s++
    if (p.length >= 12) s++
    if (/[A-Z]/.test(p)) s++
    if (/[0-9]/.test(p)) s++
    if (/[^A-Za-z0-9]/.test(p)) s++
    return s
  }, [data.adminPassword])

  const match = data.adminPassword === data.confirmPassword && data.confirmPassword.length > 0

  return (
    <div>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>🔑 Sécurité & Accès</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', marginBottom: '1.5rem' }}>
        Configurez l'accès administrateur à votre infrastructure.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div>
          <label style={labelStyle}>Mot de passe administrateur</label>
          <input type="password" value={data.adminPassword} onChange={e => update('adminPassword', e.target.value)} placeholder="Minimum 8 caractères" style={inputStyle} />
          <div style={{ display: 'flex', gap: '0.125rem', marginTop: '0.5rem' }}>
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} style={{
                flex: 1, height: 3, borderRadius: 2,
                background: i <= strength ? (strength <= 2 ? 'var(--rose)' : strength <= 3 ? 'var(--amber)' : 'var(--emerald)') : 'var(--border)',
                transition: 'all 0.2s',
              }} />
            ))}
          </div>
          <div style={{ fontSize: '0.6875rem', color: strength <= 2 ? 'var(--rose)' : strength <= 3 ? 'var(--amber)' : 'var(--emerald)', marginTop: '0.25rem' }}>
            {strength <= 2 ? 'Faible' : strength <= 3 ? 'Moyen' : 'Fort'}
          </div>
        </div>

        <div>
          <label style={labelStyle}>Confirmer le mot de passe</label>
          <input type="password" value={data.confirmPassword} onChange={e => update('confirmPassword', e.target.value)} placeholder="Confirmez" style={{
            ...inputStyle,
            border: data.confirmPassword.length > 0 ? (match ? '1px solid var(--emerald)' : '1px solid var(--rose)') : inputStyle.border,
          }} />
          {data.confirmPassword.length > 0 && !match && (
            <div style={{ fontSize: '0.6875rem', color: 'var(--rose)', marginTop: '0.25rem' }}>Les mots de passe ne correspondent pas</div>
          )}
        </div>

        <div>
          <label style={labelStyle}>🛡️ Double authentification (optionnel)</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {([
              { value: '' as const, label: 'Plus tard' },
              { value: 'totp' as const, label: '📱 TOTP (Google Auth)' },
              { value: 'sms' as const, label: '💬 SMS' },
            ]).map(o => (
              <button key={o.value} onClick={() => update('twoFactor', o.value)} style={{
                flex: 1, padding: '0.5rem', borderRadius: '0.5rem', fontSize: '0.8125rem', fontWeight: 600,
                border: data.twoFactor === o.value ? '2px solid var(--cyan)' : '1px solid var(--border)',
                background: data.twoFactor === o.value ? 'rgba(34,211,238,0.06)' : 'transparent',
                color: data.twoFactor === o.value ? 'var(--cyan)' : 'var(--text-muted)',
                cursor: 'pointer', transition: 'all 0.2s',
              }}>
                {o.label}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label style={labelStyle}>📧 Inviter des collègues (optionnel)</label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input placeholder="email@exemple.fr" style={{ ...inputStyle, flex: 1 }} id="invite-email" />
            <select style={{ ...inputStyle, width: 120 }} id="invite-role">
              <option value="expert">Expert</option>
              <option value="operator">Opérateur</option>
              <option value="viewer">Viewer</option>
            </select>
            <button onClick={() => {
              const emailEl = document.getElementById('invite-email') as HTMLInputElement
              const roleEl = document.getElementById('invite-role') as HTMLSelectElement
              if (emailEl?.value && emailEl.value.includes('@')) {
                update('invites', [...data.invites, { email: emailEl.value, role: roleEl.value }])
                emailEl.value = ''
              }
            }} className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
              + Ajouter
            </button>
          </div>
          {data.invites.length > 0 && (
            <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
              {data.invites.map((inv, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.375rem 0.75rem', background: 'rgba(30,41,59,0.4)', borderRadius: '0.375rem', fontSize: '0.8125rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{inv.email}</span>
                  <span className="badge badge-cyan" style={{ fontSize: '0.5625rem' }}>{inv.role}</span>
                  <button onClick={() => update('invites', data.invites.filter((_, j) => j !== i))} style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--text-dim)', cursor: 'pointer', fontSize: '0.75rem' }}>✕</button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// STEP 5: ACTIVATION
// ═══════════════════════════════════════════════════════════════

function ActivationStep({ data, result, loading, errors, submit, onComplete }: {
  data: FormData; result: any; loading: boolean; errors: string[]; submit: () => void; onComplete: (r: any) => void
}) {
  const v = VERTICALS.find(v => v.id === data.vertical)
  const isHigh = ['avocat', 'sante', 'banque'].includes(data.vertical)

  if (!result) {
    return (
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.5rem' }}>🚀 Prêt à activer</h2>

        {/* Récap */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <div style={recapStyle}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Organisation</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{data.organization}</div>
          </div>
          <div style={recapStyle}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Vertical</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{v?.icon} {v?.label}</div>
          </div>
          <div style={recapStyle}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Mode</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem', color: isHigh ? 'var(--rose)' : 'var(--cyan)' }}>
              {isHigh ? '🔒 Haute Protection' : '📊 Standard'}
            </div>
          </div>
          <div style={recapStyle}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Data Residency</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{data.dataResidency}</div>
          </div>
          <div style={recapStyle}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>IA</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{data.llmMode === 'cloud' ? '☁️ Cloud' : data.llmMode === 'local' ? '🏠 Local' : '🔀 Hybride'}</div>
          </div>
          <div style={recapStyle}>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Utilisateurs</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>1 admin + {data.invites.length} invités</div>
          </div>
        </div>

        {/* Activation checklist */}
        <div style={{ background: 'rgba(30,41,59,0.4)', borderRadius: '0.75rem', padding: '1rem', border: '1px solid var(--border)', marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--cyan)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Sera créé automatiquement :
          </div>
          {[
            'Journal WORM (SHA-256 hash-chain)',
            'Règles JsonLogic de votre vertical',
            'Textes réglementaires vectorisés (RAG)',
            'Vault client chiffré',
            `Data residency: ${data.dataResidency}`,
            `Modèle IA: ${data.llmMode}`,
            `Mode: ${isHigh ? 'Haute Protection' : 'Standard'}`,
            'Audit trail actif',
          ].map((item, i) => (
            <div key={i} style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', padding: '0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: 'var(--emerald)' }}>✅</span> {item}
            </div>
          ))}
        </div>

        {errors.length > 0 && (
          <div style={{ marginBottom: '1rem' }}>
            {errors.map((e, i) => (
              <div key={i} style={{ padding: '0.5rem 0.75rem', background: 'rgba(251,113,133,0.08)', border: '1px solid rgba(251,113,133,0.2)', borderRadius: '0.5rem', fontSize: '0.8125rem', color: 'var(--rose)', marginBottom: '0.25rem' }}>
                ❌ {e}
              </div>
            ))}
          </div>
        )}

        <button onClick={submit} disabled={loading} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '0.875rem', fontSize: '0.9375rem' }}>
          {loading ? '⏳ Activation en cours...' : '🚀 Activer mon infrastructure'}
        </button>
      </div>
    )
  }

  // SUCCESS state
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Infrastructure activée !</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
        Votre cabinet <strong>{data.organization}</strong> est prêt.
      </p>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <div style={{ ...recapStyle, textAlign: 'center' }}>
          <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--cyan)' }}>{result.rules_loaded}</div>
          <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Règles actives</div>
        </div>
        <div style={{ ...recapStyle, textAlign: 'center' }}>
          <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--emerald)' }}>{result.agents_created}</div>
          <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Agents</div>
        </div>
        <div style={{ ...recapStyle, textAlign: 'center' }}>
          <div className="mono" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--violet)' }}>{result.regulatory_seeded}</div>
          <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Textes RAG</div>
        </div>
      </div>

      {/* First message */}
      {result.first_message && (
        <div style={{ background: 'rgba(30,41,59,0.4)', borderRadius: '0.75rem', padding: '1.25rem', border: '1px solid var(--border)', marginBottom: '1.5rem', textAlign: 'left', fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.7, whiteSpace: 'pre-line' }}>
          🤖 {result.first_message}
        </div>
      )}

      <button onClick={() => onComplete(result)} className="btn btn-primary" style={{ padding: '0.875rem 2rem', fontSize: '0.9375rem' }}>
        Accéder au Dashboard →
      </button>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════
// SHARED STYLES
// ═══════════════════════════════════════════════════════════════

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '0.625rem 0.875rem', borderRadius: '0.5rem',
  background: 'rgba(15,23,42,0.8)', border: '1px solid var(--border)',
  color: 'var(--text)', fontSize: '0.875rem', outline: 'none',
  fontFamily: 'Inter, sans-serif',
  transition: 'border-color 0.2s',
}

const labelStyle: React.CSSProperties = {
  display: 'block', fontSize: '0.75rem', fontWeight: 600,
  color: 'var(--text-muted)', marginBottom: '0.375rem',
}

const previewItemStyle: React.CSSProperties = {
  fontSize: '0.8125rem', color: 'var(--text-muted)', padding: '0.375rem 0',
}

const recapStyle: React.CSSProperties = {
  padding: '0.75rem', background: 'rgba(30,41,59,0.4)',
  borderRadius: '0.5rem', border: '1px solid var(--border)',
}
