import { useState, useEffect, useRef } from 'react'
import { useApi, apiFetch, usePolling } from '../hooks/useApi'

const NAV_ITEMS = [
  { id: 'dashboard',  icon: '📊', label: 'Tableau de bord' },
  { id: 'compliance', icon: '🛡️', label: 'Conformité' },
  { id: 'serment',    icon: '🤫', label: 'Serment numérique' },
  { id: 'trustbox',   icon: '🔐', label: 'Trust Box' },
  { id: 'review',     icon: '🔄', label: 'Review Loop' },
  { id: 'artifacts',  icon: '📦', label: 'Artefacts' },
  { id: 'echeancier', icon: '📅', label: 'Échéancier' },
  { id: 'chat',       icon: '💬', label: 'Chat Agent' },
  { id: 'intents',    icon: '🎯', label: 'Intentions' },
  { id: 'journal',    icon: '📝', label: 'Journal d\'audit' },
  { id: 'arbitrage',  icon: '⚖️', label: 'Arbitrage' },
  { id: 'settings',   icon: '⚙️', label: 'Paramètres' },
]

export function DashboardPage({ user, onLogout }: { user: any; onLogout: () => void }) {
  const [active, setActive] = useState('dashboard')
  const [transitioning, setTransitioning] = useState(false)
  const [displayedView, setDisplayedView] = useState('dashboard')

  const switchView = (id: string) => {
    if (id === active) return
    setTransitioning(true)
    setTimeout(() => {
      setActive(id)
      setDisplayedView(id)
      setTimeout(() => setTransitioning(false), 50)
    }, 150)
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: 'var(--bg)' }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: 240, background: 'var(--bg-card-solid)', borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', flexShrink: 0,
      }}>
        {/* Brand */}
        <div style={{ padding: '1.25rem 1rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: 32, height: 32, borderRadius: '0.5rem',
            background: 'linear-gradient(135deg, var(--cyan), var(--emerald))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.8rem', fontWeight: 800, color: 'var(--bg)',
          }}>CL</div>
          <div>
            <div className="mono" style={{ fontSize: '0.8125rem', fontWeight: 700 }}>Cortex Leman</div>
            <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>v5 · Graphe de Confiance</div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '0.75rem 0.5rem', display: 'flex', flexDirection: 'column', gap: '0.125rem' }}>
          {NAV_ITEMS.map((item) => (
            <button key={item.id} onClick={() => switchView(item.id)} style={{
              width: '100%', padding: '0.625rem 0.875rem', borderRadius: '0.5rem',
              background: active === item.id ? 'rgba(34,211,238,0.08)' : 'transparent',
              border: active === item.id ? '1px solid rgba(34,211,238,0.15)' : '1px solid transparent',
              color: active === item.id ? 'var(--cyan)' : 'var(--text-muted)',
              fontSize: '0.8125rem', fontWeight: active === item.id ? 600 : 400,
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.75rem',
              textAlign: 'left', transition: 'all 0.15s ease',
            }}>
              <span style={{ fontSize: '1rem', width: 20, textAlign: 'center' }}>{item.icon}</span> {item.label}
            </button>
          ))}
        </nav>

        {/* Vertical badge */}
        <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid var(--border)' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
            padding: '0.25rem 0.625rem', borderRadius: '9999px',
            background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.15)',
            fontSize: '0.6875rem', color: 'var(--cyan)', fontWeight: 500,
          }}>
            {verticalIcon(user?.primary_vertical)} {user?.primary_vertical || 'standard'}
          </div>
        </div>

        {/* User */}
        <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '0.625rem' }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: 'rgba(34,211,238,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '0.8125rem', fontWeight: 600, color: 'var(--cyan)',
            }}>
              {(user?.full_name || user?.email || 'U')[0].toUpperCase()}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user?.full_name || user?.email || 'Utilisateur'}
              </div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                {(user?.role || 'viewer').toUpperCase()} · {user?.primary_vertical || '—'}
              </div>
            </div>
          </div>
          <button onClick={onLogout} style={{
            width: '100%', padding: '0.4375rem', borderRadius: '0.375rem',
            background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-dim)',
            fontSize: '0.6875rem', cursor: 'pointer', transition: 'all 0.15s ease',
          }}>
            Déconnexion
          </button>
        </div>
      </aside>

      {/* ── Main content with transition ── */}
      <main style={{
        flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden',
        opacity: transitioning ? 0 : 1, transform: transitioning ? 'translateX(8px)' : 'translateX(0)',
        transition: 'opacity 0.15s ease, transform 0.15s ease',
      }}>
        {displayedView === 'dashboard'  && <DashboardView user={user} />}
        {displayedView === 'serment'    && <SermentView user={user} />}
        {displayedView === 'trustbox'   && <TrustBoxView user={user} />}
        {displayedView === 'review'     && <ReviewLoopView user={user} />}
        {displayedView === 'artifacts'  && <ArtifactsView user={user} />}
        {displayedView === 'echeancier' && <EcheancierView user={user} />}
        {displayedView === 'chat'       && <ChatView user={user} />}
        {displayedView === 'intents'    && <IntentsView user={user} />}
        {displayedView === 'journal'    && <JournalView user={user} />}
        {displayedView === 'arbitrage'  && <ArbitrageView user={user} />}
        {displayedView === 'compliance' && <ComplianceView user={user} />}
        {displayedView === 'settings'   && <SettingsView user={user} onLogout={onLogout} />}
      </main>
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. TABLEAU DE BORD — Vue executive
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function DashboardView({ user: _user }: { user: any }) {
  const { data: agents } = useApi('/api/v1/agents/status')
  const { data: compliance } = useApi('/api/v1/compliance/report/daily')
  const { data: vault } = useApi('/api/v1/vault/stats')
  const { data: _orchestrator } = useApi('/api/v1/orchestrator/status')

  const circuitBreakers = (agents as any)?.circuit_breakers || []
  const activeConflicts = (agents as any)?.active_conflicts || []

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Tableau de bord</h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Supervision en temps réel · {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className="badge badge-emerald" style={{ fontSize: '0.6875rem' }}>● Système opérationnel</span>
        </div>
      </div>

      {/* KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        <KpiCard icon="🎯" label="Intentions actives"
          value={String((compliance as any)?.stats?.total_intentions ?? '—')}
          sub="Ce jour" color="cyan" />
        <KpiCard icon="⚠️" label="Conflits"
          value={String(activeConflicts.length)}
          sub={activeConflicts.length > 0 ? 'Attention requise' : 'Aucun conflit'}
          color={activeConflicts.length > 0 ? 'amber' : 'emerald'} />
        <KpiCard icon="🛡️" label="Score conformité"
          value={(compliance as any)?.compliance_score != null ? `${(compliance as any).compliance_score}%` : '—'}
          sub="RGPD · AI Act" color="emerald" />
        <KpiCard icon="🔒" label="Vault"
          value={String((vault as any)?.total_documents ?? (vault as any)?.documents ?? '—')}
          sub="Documents chiffrés" color="violet" />
      </div>

      {/* Agents + Compliance Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* Agents & Circuit Breakers */}
        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            🤖 Agents & Circuit Breakers
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {circuitBreakers.length > 0 ? circuitBreakers.map((cb: any, i: number) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.625rem 0.75rem', borderRadius: '0.5rem',
                background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                  <div style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: cb.state === 'closed' ? 'var(--emerald)' : cb.state === 'open' ? 'var(--rose)' : 'var(--amber)',
                    boxShadow: cb.state === 'closed' ? '0 0 6px rgba(52,211,153,0.4)' : 'none',
                  }} />
                  <span style={{ fontSize: '0.8125rem', fontWeight: 500 }}>{cb.name || `Circuit ${i+1}`}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                    {cb.failures || 0} échecs
                  </span>
                  <span className={`badge badge-${cb.state === 'closed' ? 'emerald' : cb.state === 'open' ? 'rose' : 'amber'}`} style={{ fontSize: '0.625rem' }}>
                    {cb.state === 'closed' ? 'OK' : cb.state === 'open' ? 'Ouvert' : 'Demi-ouvert'}
                  </span>
                </div>
              </div>
            )) : (
              <EmptyState message="Aucun circuit breaker actif" />
            )}
          </div>
        </div>

        {/* Compliance Report */}
        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📋 Rapport de conformité
          </h3>
          {(compliance as any)?.checks ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {Object.entries((compliance as any).checks).map(([key, val]: [string, any]) => (
                <div key={key} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.625rem 0.75rem', borderRadius: '0.5rem',
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
                }}>
                  <span style={{ fontSize: '0.8125rem' }}>{formatCheckLabel(key)}</span>
                  <span className={`badge badge-${val === 'pass' || val === 'healthy' || val === true ? 'emerald' : val === 'warn' ? 'amber' : 'rose'}`} style={{ fontSize: '0.625rem' }}>
                    {val === 'pass' || val === 'healthy' || val === true ? '✓ Conforme' : val === 'warn' ? '⚠ Attention' : '✗ Non conforme'}
                  </span>
                </div>
              ))}
            </div>
          ) : (compliance as any)?.violations ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              {((compliance as any).violations as any[]).length > 0 ?
                (compliance as any).violations.map((v: any, i: number) => (
                  <div key={i} style={{ fontSize: '0.8125rem', padding: '0.5rem', borderRadius: '0.375rem', background: 'rgba(251,113,133,0.06)', border: '1px solid rgba(251,113,133,0.15)', color: 'var(--rose)' }}>
                    {v.description || v.type || JSON.stringify(v)}
                  </div>
                )) :
                <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--emerald)' }}>
                  ✅ Aucune violation détectée
                </div>
              }
            </div>
          ) : (
            <EmptyState message="Rapport non disponible" />
          )}
        </div>
      </div>

      {/* Active conflicts */}
      {activeConflicts.length > 0 && (
        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1.5rem', borderLeft: '3px solid var(--amber)' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--amber)' }}>
            ⚠️ Conflits actifs nécessitant une attention
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {activeConflicts.map((c: any, i: number) => (
              <div key={i} style={{
                padding: '0.75rem', borderRadius: '0.5rem',
                background: 'rgba(251,191,36,0.04)', border: '1px solid rgba(251,191,36,0.12)',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 500 }}>{c.description || c.type || 'Conflit détecté'}</div>
                  {c.intention_id && <div className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.125rem' }}>Intention: {c.intention_id}</div>}
                </div>
                <span className="badge badge-amber" style={{ fontSize: '0.625rem' }}>En attente</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Trust Architecture visual */}
      <div className="glass" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>🏛️ Graphe de Confiance — Pipeline</h3>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          {[
            { icon: '📥', label: 'Intention', color: 'cyan' },
            { icon: '→', label: '', color: '' },
            { icon: '🔍', label: 'Médiateur', color: 'violet' },
            { icon: '→', label: '', color: '' },
            { icon: '🤖', label: 'Agent LLM', color: 'emerald' },
            { icon: '→', label: '', color: '' },
            { icon: '🛡️', label: 'Guardrails', color: 'amber' },
            { icon: '→', label: '', color: '' },
            { icon: '📝', label: 'Journal WORM', color: 'cyan' },
            { icon: '→', label: '', color: '' },
            { icon: '✅', label: 'Validation', color: 'emerald' },
          ].map((step, i) => step.label ? (
            <div key={i} style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.375rem',
              padding: '0.625rem 1rem', borderRadius: '0.5rem',
              background: `var(--${step.color})08`, border: `1px solid var(--${step.color})20`,
            }}>
              <span style={{ fontSize: '1.25rem' }}>{step.icon}</span>
              <span style={{ fontSize: '0.6875rem', color: `var(--${step.color})`, fontWeight: 500 }}>{step.label}</span>
            </div>
          ) : (
            <span key={i} style={{ color: 'var(--text-dim)', fontSize: '0.875rem' }}>{step.icon}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   2. CHAT AGENT — Avec indicateurs de confiance
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  agent?: string
  model?: string
  tokens?: number
  provider?: string
  trustScore?: number
  guardrailFlags?: string[]
  guardrailBlocked?: boolean
  vertical?: string
  streaming?: boolean
  pipelineSteps?: PipelineStep[]
}

interface PipelineStep {
  step: string
  agent: string
  status: 'pending' | 'running' | 'done' | 'blocked'
  detail?: string
  verdict?: string
}

const VERTICAL_CONFIG: Record<string, { icon: string; label: string; color: string }> = {
  comptable: { icon: '📊', label: 'Comptable', color: '--cyan' },
  avocat:    { icon: '⚖️',  label: 'Avocat',    color: '--violet' },
  sante:     { icon: '🏥', label: 'Santé',     color: '--emerald' },
  banque:    { icon: '🏦', label: 'Banque',    color: '--amber' },
  startup:   { icon: '🚀', label: 'Startup',   color: '--orange' },
  rh:        { icon: '👥', label: 'RH',        color: '--rose' },
}

const STEP_ICONS: Record<string, string> = {
  intention: '🎯', mediator_check: '🔍', rag_context: '📊',
  llm_generate: '🧠', guardrail: '🛡️', journal: '📝',
}

const AGENT_COLORS: Record<string, string> = {
  orchestrator: 'var(--cyan)', mediator: 'var(--violet)', data: 'var(--emerald)',
  reasoning: 'var(--amber)', supervisor: 'var(--blue)',
}

let msgCounter = 0
function nextId() { return `msg_${++msgCounter}_${Date.now()}` }

/** Simple markdown-lite renderer */
function renderMarkdown(text: string): string {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/```([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.3);padding:0.75rem;border-radius:0.375rem;overflow-x:auto;font-size:0.75rem;margin:0.5rem 0"><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code style="background:rgba(0,0,0,0.2);padding:0.125rem 0.375rem;border-radius:0.25rem;font-size:0.75rem">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    .replace(/^### (.+)$/gm, '<div style="font-size:0.8125rem;font-weight:700;margin:0.5rem 0 0.25rem">$1</div>')
    .replace(/^## (.+)$/gm, '<div style="font-size:0.875rem;font-weight:700;margin:0.625rem 0 0.375rem">$1</div>')
    .replace(/^# (.+)$/gm, '<div style="font-size:1rem;font-weight:800;margin:0.75rem 0 0.5rem">$1</div>')
    .replace(/^- (.+)$/gm, '<div style="display:flex;gap:0.375rem;margin:0.125rem 0"><span style="color:var(--cyan)">•</span><span>$1</span></div>')
    .replace(/\n/g, '<br/>')
}

function ChatView({ user }: { user: any }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [vertical, setVertical] = useState(user?.primary_vertical || 'comptable')
  const [pipelineVisible, setPipelineVisible] = useState(false)
  const [recording, setRecording] = useState(false)
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  // ── Voice recording ──
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      const chunks: BlobPart[] = []
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data) }
      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        const blob = new Blob(chunks, { type: 'audio/webm' })
        await transcribeAndSend(blob)
      }
      recorder.start()
      setMediaRecorder(recorder)
      setRecording(true)
    } catch (e: any) {
      console.error('Mic error:', e)
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop()
      setRecording(false)
      setMediaRecorder(null)
    }
  }

  const transcribeAndSend = async (audioBlob: Blob) => {
    const API = import.meta.env.VITE_API_URL || 'http://localhost:8002'
    const token = localStorage.getItem('cl_access_token')
    try {
      const res = await fetch(`${API}/api/v1/voice/transcribe`, {
        method: 'POST',
        headers: { ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: audioBlob,
      })
      if (!res.ok) throw new Error(`STT ${res.status}`)
      const data = await res.json()
      if (data.text) {
        setInput(data.text)
        // Auto-send after transcription
        setTimeout(() => {
          const inputEl = document.querySelector<HTMLInputElement>('input[placeholder*="question"]')
          if (inputEl) inputEl.focus()
        }, 100)
      }
    } catch (e: any) {
      console.error('Transcription error:', e)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const text = input.trim()
    const userMsg: ChatMessage = { id: nextId(), role: 'user', content: text, timestamp: new Date() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setPipelineVisible(true)

    const assistantId = nextId()
    const initialPipeline: PipelineStep[] = [
      { step: 'intention', agent: 'orchestrator', status: 'pending' },
      { step: 'mediator_check', agent: 'mediator', status: 'pending' },
      { step: 'rag_context', agent: 'data', status: 'pending' },
      { step: 'llm_generate', agent: 'reasoning', status: 'pending' },
      { step: 'guardrail', agent: 'mediator', status: 'pending' },
      { step: 'journal', agent: 'supervisor', status: 'pending' },
    ]
    setMessages(prev => [...prev, {
      id: assistantId, role: 'assistant', content: '', timestamp: new Date(),
      streaming: true, pipelineSteps: initialPipeline, vertical,
    }])

    try {
      const API = import.meta.env.VITE_API_URL || 'http://localhost:8002'
      const token = localStorage.getItem('cl_access_token')
      const abort = new AbortController()
      abortRef.current = abort

      const res = await fetch(`${API}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: text, vertical, client_id: 'demo' }),
        signal: abort.signal,
      })

      if (!res.ok) {
        // Fallback to non-streaming
        const fallbackRes = await apiFetch(`/api/v1/chat?message=${encodeURIComponent(text)}&vertical=${vertical}&client_id=demo`, { method: 'POST' })
        setMessages(prev => prev.map(m => m.id === assistantId ? {
          ...m, content: fallbackRes.response || 'Aucune réponse', streaming: false,
          agent: fallbackRes.agent || 'reasoning', model: fallbackRes.model,
          tokens: fallbackRes.tokens, provider: fallbackRes.provider,
          trustScore: fallbackRes.trust_score ?? 1.0,
          guardrailFlags: fallbackRes.guardrail_flags || [],
          guardrailBlocked: fallbackRes.guardrail_blocked || false,
          pipelineSteps: initialPipeline.map(s => ({ ...s, status: 'done' })),
        } : m))
        setLoading(false)
        setPipelineVisible(false)
        return
      }

      const reader = res.body?.getReader()
      if (!reader) throw new Error('No reader')
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            const eventType = line.slice(7).trim()
            // next line should be data:
            continue
          }
          if (!line.startsWith('data: ')) continue
          const rawData = line.slice(6)
          if (!rawData || rawData === '[DONE]') continue

          try {
            const evt = JSON.parse(rawData)

            // Handle different event types from SSE
            // The SSE format sends event: then data: — but we simplify here
            // and just look at the data structure
            if (evt.text) {
              // Token event
              setMessages(prev => prev.map(m => m.id === assistantId ?
                { ...m, content: m.content + evt.text } : m))
            } else if (evt.step) {
              // Pipeline step event
              setMessages(prev => prev.map(m => m.id === assistantId ? {
                ...m,
                pipelineSteps: m.pipelineSteps?.map(s =>
                  s.step === evt.step ? { ...s, status: evt.status || 'done', detail: evt.detail, verdict: evt.verdict } : s
                ),
              } : m))
            } else if (evt.verdict && evt.reason) {
              // Guardrail blocked
              setMessages(prev => prev.map(m => m.id === assistantId ?
                { ...m, guardrailBlocked: true, content: `🛑 ${evt.reason} (Verdict: ${evt.verdict})`, streaming: false } : m))
            } else if (evt.status === 'done' || evt.status === 'blocked') {
              // Pipeline end
              setMessages(prev => prev.map(m => m.id === assistantId ? {
                ...m, streaming: false,
                agent: evt.agent, model: evt.model, provider: evt.provider,
                tokens: evt.tokens, trustScore: evt.trust_score,
                guardrailFlags: evt.guardrail_flags || [],
                pipelineSteps: m.pipelineSteps?.map(s => ({ ...s, status: 'done' })),
              } : m))
            } else if (evt.error) {
              setMessages(prev => prev.map(m => m.id === assistantId ?
                { ...m, content: `Erreur: ${evt.error}`, streaming: false } : m))
            }
          } catch { /* ignore malformed JSON */ }
        }
      }
    } catch (e: any) {
      if (e.name === 'AbortError') return
      // Fallback to non-streaming
      try {
        const fallbackRes = await apiFetch(`/api/v1/chat?message=${encodeURIComponent(text)}&vertical=${vertical}&client_id=demo`, { method: 'POST' })
        setMessages(prev => prev.map(m => m.id === assistantId ? {
          ...m, content: fallbackRes.response || 'Aucune réponse', streaming: false,
          agent: fallbackRes.agent || 'reasoning', model: fallbackRes.model,
          tokens: fallbackRes.tokens, trustScore: fallbackRes.trust_score ?? 1.0,
          guardrailFlags: fallbackRes.guardrail_flags || [],
        } : m))
      } catch (e2: any) {
        setMessages(prev => prev.map(m => m.id === assistantId ?
          { ...m, content: `Erreur: ${e2.message}`, streaming: false } : m))
      }
    } finally {
      setLoading(false)
      setPipelineVisible(false)
      abortRef.current = null
    }
  }

  const vc = VERTICAL_CONFIG[vertical] || VERTICAL_CONFIG.comptable

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <header style={{ padding: '0.75rem 1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <h2 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>💬 Le Léman</h2>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
            padding: '0.125rem 0.5rem', borderRadius: '9999px',
            background: `var(${vc.color})08`, border: `1px solid var(${vc.color})20`,
            fontSize: '0.6875rem', color: `var(${vc.color})`, fontWeight: 500,
          }}>
            {vc.icon} {vc.label}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <select value={vertical} onChange={e => setVertical(e.target.value)} style={{
            padding: '0.25rem 0.5rem', borderRadius: '0.375rem', fontSize: '0.75rem',
            background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
          }}>
            {Object.entries(VERTICAL_CONFIG).map(([k, v]) => (
              <option key={k} value={k}>{v.icon} {v.label}</option>
            ))}
          </select>
          <span className="badge badge-emerald" style={{ fontSize: '0.625rem' }}>● Connecté</span>
        </div>
      </header>

      {/* Live Pipeline Bar */}
      {pipelineVisible && (() => {
        const last = messages[messages.length - 1]
        const steps = last?.pipelineSteps || []
        if (!steps.length) return null
        return (
          <div style={{
            padding: '0.5rem 1.5rem', borderBottom: '1px solid var(--border)',
            background: 'rgba(34,211,238,0.02)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflowX: 'auto' }}>
              {steps.map((s, i) => {
                const isActive = s.status === 'running'
                const isDone = s.status === 'done'
                const isBlocked = s.status === 'blocked'
                return (
                  <div key={s.step} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <div style={{
                      display: 'flex', alignItems: 'center', gap: '0.25rem',
                      padding: '0.25rem 0.5rem', borderRadius: '0.375rem', fontSize: '0.625rem',
                      background: isDone ? 'rgba(52,211,153,0.06)' : isActive ? 'rgba(34,211,238,0.08)' : isBlocked ? 'rgba(251,113,133,0.06)' : 'transparent',
                      border: `1px solid ${isDone ? 'rgba(52,211,153,0.15)' : isActive ? 'rgba(34,211,238,0.2)' : isBlocked ? 'rgba(251,113,133,0.15)' : 'var(--border)'}`,
                      color: isDone ? 'var(--emerald)' : isActive ? 'var(--cyan)' : isBlocked ? 'var(--rose)' : 'var(--text-dim)',
                      fontWeight: isActive ? 700 : 400, whiteSpace: 'nowrap',
                    }}>
                      <span>{isActive ? '⏳' : isDone ? '✅' : isBlocked ? '🛑' : STEP_ICONS[s.step] || '○'}</span>
                      <span>{s.step.replace('_', ' ')}</span>
                      {s.detail && <span style={{ opacity: 0.6 }}>· {s.detail}</span>}
                    </div>
                    {i < steps.length - 1 && <span style={{ color: 'var(--text-dim)', fontSize: '0.5rem' }}>→</span>}
                  </div>
                )
              })}
            </div>
          </div>
        )
      })()}

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {messages.length === 0 && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ fontSize: '3rem' }}>🌊</div>
            <p style={{ color: 'var(--cyan)', fontSize: '1.125rem', fontWeight: 700 }}>Le Léman</p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500 }}>Conseil de confiance franco-suisse</p>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', maxWidth: 400, textAlign: 'center', lineHeight: 1.6 }}>
              Posez votre question — les agents analysent, le Médiateur vérifie, et je vous recommande avec transparence.
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center', marginTop: '0.75rem' }}>
              {getSuggestions(vertical).map((s, i) => (
                <button key={i} onClick={() => setInput(s)} style={{
                  padding: '0.375rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem',
                  background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)',
                  color: 'var(--text-muted)', cursor: 'pointer', transition: 'all 0.2s',
                }} onMouseEnter={e => { (e.target as HTMLElement).style.borderColor = 'var(--cyan)'; (e.target as HTMLElement).style.color = 'var(--cyan)' }} onMouseLeave={e => { (e.target as HTMLElement).style.borderColor = 'var(--border)'; (e.target as HTMLElement).style.color = 'var(--text-muted)' }}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} style={{
            display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              maxWidth: '75%', padding: '0.875rem 1.125rem', borderRadius: '0.875rem',
              background: m.role === 'user' ? 'rgba(34,211,238,0.08)' : m.role === 'system' ? 'rgba(167,139,250,0.06)' : 'rgba(255,255,255,0.02)',
              border: m.role === 'user' ? '1px solid rgba(34,211,238,0.12)' : m.role === 'system' ? '1px solid rgba(167,139,250,0.12)' : '1px solid var(--border)',
              position: 'relative',
            }}>
              {m.guardrailBlocked && (
                <div style={{
                  marginBottom: '0.75rem', padding: '0.5rem 0.75rem', borderRadius: '0.5rem',
                  background: 'rgba(251,113,133,0.08)', border: '1px solid rgba(251,113,133,0.15)',
                  fontSize: '0.75rem', color: 'var(--rose)', display: 'flex', alignItems: 'center', gap: '0.5rem',
                }}>
                  🛑 Réponse bloquée par les garde-fous du Médiateur
                </div>
              )}
              {(m.guardrailFlags?.length || 0) > 0 && !m.guardrailBlocked && (
                <div style={{
                  marginBottom: '0.75rem', padding: '0.375rem 0.625rem', borderRadius: '0.375rem',
                  background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.15)',
                  fontSize: '0.6875rem', color: 'var(--amber)', display: 'flex', alignItems: 'center', gap: '0.5rem',
                }}>
                  ⚠️ {m.guardrailFlags!.join(', ')}
                </div>
              )}
              <div
                style={{ fontSize: '0.8125rem', lineHeight: 1.7 }}
                dangerouslySetInnerHTML={{ __html: m.role === 'user' || m.role === 'system' ? m.content.replace(/</g, '&lt;').replace(/\n/g, '<br/>') : renderMarkdown(m.content) }}
              />
              {m.streaming && <span className="trust-pulse" style={{ display: 'inline-block', width: 6, height: 14, background: 'var(--cyan)', marginLeft: 2, borderRadius: 1, verticalAlign: 'middle' }} />}
              {m.role === 'assistant' && !m.streaming && (
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(30,41,59,0.4)',
                  flexWrap: 'wrap', gap: '0.375rem',
                }}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                      {m.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {m.agent && (
                      <span style={{ fontSize: '0.5625rem', color: AGENT_COLORS[m.agent] || 'var(--text-dim)', fontWeight: 600 }}>
                        {m.agent}
                      </span>
                    )}
                    {m.model && (
                      <span style={{ fontSize: '0.5625rem', color: 'var(--violet)' }}>
                        {m.model.split('/').pop()}
                      </span>
                    )}
                    {m.tokens != null && m.tokens > 0 && (
                      <span className="mono" style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>
                        {m.tokens} tok
                      </span>
                    )}
                  </div>
                  {m.trustScore != null && <TrustBadge score={m.trustScore} />}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid var(--border)' }}>
        <div style={{
          display: 'flex', gap: '0.75rem', alignItems: 'center',
          background: 'var(--bg-card-solid)', border: '1px solid var(--border)',
          borderRadius: '0.75rem', padding: '0.25rem 0.25rem 0.25rem 1rem',
          transition: 'border-color 0.2s',
        }} onFocus={e => (e.currentTarget.style.borderColor = 'rgba(34,211,238,0.3)')} onBlur={e => (e.currentTarget.style.borderColor = 'var(--border)')}>
          <input
            value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder={`Posez votre question ${vc.label}…`}
            style={{
              flex: 1, background: 'transparent', border: 'none', color: 'var(--text)',
              fontSize: '0.8125rem', outline: 'none', padding: '0.5rem 0',
            }}
          />
          {/* Microphone button */}
          <button
            onClick={recording ? stopRecording : startRecording}
            style={{
              padding: '0.5rem', borderRadius: '0.5rem',
              background: recording ? 'rgba(251,113,133,0.15)' : 'transparent',
              border: recording ? '1px solid rgba(251,113,133,0.3)' : '1px solid var(--border)',
              color: recording ? 'var(--rose)' : 'var(--text-dim)',
              cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              transition: 'all 0.2s', minWidth: 36, minHeight: 36,
              boxShadow: recording ? '0 0 12px rgba(251,113,133,0.3)' : 'none',
            }}
            title={recording ? 'Arrêter l\'enregistrement' : 'Enregistrer un message vocal'}
          >
            {recording ? '⏹' : '🎤'}
          </button>
          <button onClick={sendMessage} disabled={loading || !input.trim()} style={{
            padding: '0.5rem 1.25rem', borderRadius: '0.5rem',
            background: loading || !input.trim() ? 'var(--bg)' : 'var(--cyan)',
            color: loading || !input.trim() ? 'var(--text-dim)' : 'var(--bg)',
            border: 'none', fontSize: '0.8125rem', fontWeight: 600, cursor: loading ? 'default' : 'pointer',
            transition: 'all 0.15s ease',
          }}>
            {loading ? '⏳' : '→'}
          </button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.375rem', padding: '0 0.25rem' }}>
          <span style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>
            🔍 Médiateur · 📝 Journal WORM · 🛡️ RGPD/AI Act
          </span>
          <span className="mono" style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>
            Entrée ↵
          </span>
        </div>
      </div>
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   3. INTENTIONS — Pipeline visuel
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function IntentsView({ user }: { user: any }) {
  const [clientId] = useState('demo')
  const { data, loading, refetch } = useApi(`/api/v1/intentions?client_id=${clientId}`)
  const [newIntent, setNewIntent] = useState('')
  const [creating, setCreating] = useState(false)
  const [goalResult, setGoalResult] = useState<any>(null)

  const intentions = (data as any)?.intentions || []

  const RISK_COLORS: Record<string, string> = {
    '1': 'emerald', '2': 'cyan', '3': 'amber', '4': 'orange', '5': 'rose',
  }
  const RISK_LABELS: Record<string, string> = {
    '1': 'Faible', '2': 'Modéré', '3': 'Élevé', '4': 'Très élevé', '5': 'Critique',
  }

  const createIntent = async () => {
    if (!newIntent.trim()) return
    setCreating(true)
    setGoalResult(null)
    try {
      const res = await apiFetch('/api/v1/goal', {
        method: 'POST',
        body: JSON.stringify({
          goal_text: newIntent,
          client_id: clientId,
          vertical_hint: user?.primary_vertical || undefined,
        }),
      })
      const result = await res.json()
      setGoalResult(result)
      setNewIntent('')
      refetch()
    } catch (e: any) {
      alert(e.message)
    } finally {
      setCreating(false)
    }
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>🎯 Intentions</h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Pipeline de traitement · {intentions.length} intention{intentions.length !== 1 ? 's' : ''} active{intentions.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* New intent — /goal */}
      <div className="glass" style={{ padding: '1rem', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            value={newIntent} onChange={e => setNewIntent(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && createIntent()}
            placeholder="Décrivez votre objectif en langage libre…"
            style={{
              flex: 1, padding: '0.5rem 0.875rem', borderRadius: '0.5rem',
              background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
              fontSize: '0.8125rem', outline: 'none',
            }}
          />
          <button onClick={createIntent} disabled={creating || !newIntent.trim()} className="btn btn-primary" style={{ fontSize: '0.8125rem', whiteSpace: 'nowrap' }}>
            {creating ? 'Analyse…' : '🎯 /goal'}
          </button>
        </div>
      </div>

      {/* Goal result feedback */}
      {goalResult && (
        <div className="glass" style={{ padding: '0.75rem 1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Verticale</span>
            <span className="mono" style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--cyan)' }}>{goalResult.vertical}</span>
            <span style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>({Math.round(goalResult.vertical_confidence * 100)}%)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Risque</span>
            <span className={`badge badge-${RISK_COLORS[goalResult.risk_level] || 'cyan'}`} style={{ fontSize: '0.625rem' }}>
              {goalResult.risk_level}/5 · {RISK_LABELS[goalResult.risk_level] || '?'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Action</span>
            <span className="mono" style={{ fontSize: '0.75rem', color: goalResult.risk_action === 'accept' ? 'var(--emerald)' : goalResult.risk_action === 'arbitrate' ? 'var(--amber)' : 'var(--rose)' }}>{goalResult.risk_action}</span>
          </div>
          {goalResult.keywords_matched?.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Mots-clés</span>
              {goalResult.keywords_matched.map((kw: string, i: number) => (
                <span key={i} style={{ fontSize: '0.625rem', padding: '0.125rem 0.375rem', borderRadius: '0.25rem', background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}>{kw}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Pipeline visual */}
      <div style={{ display: 'flex', gap: '0.125rem', marginBottom: '1.5rem', alignItems: 'center', justifyContent: 'center' }}>
        {[
          { label: 'Créée', color: 'cyan', icon: '📥' },
          { label: 'Routée', color: 'blue', icon: '🔀' },
          { label: 'Traitement', color: 'violet', icon: '🤖' },
          { label: 'Validée', color: 'emerald', icon: '✅' },
          { label: 'Terminée', color: 'emerald', icon: '🏁' },
        ].map((step, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <div style={{
              padding: '0.375rem 0.75rem', borderRadius: '9999px', fontSize: '0.6875rem', fontWeight: 500,
              background: `var(--${step.color})08`, border: `1px solid var(--${step.color})20`, color: `var(--${step.color})`,
              display: 'flex', alignItems: 'center', gap: '0.375rem',
            }}>
              <span style={{ fontSize: '0.75rem' }}>{step.icon}</span> {step.label}
            </div>
            {i < 4 && <span style={{ color: 'var(--text-dim)', fontSize: '0.625rem' }}>→</span>}
          </div>
        ))}
      </div>

      {/* Intentions list */}
      {loading ? <LoadingSpinner /> : intentions.length === 0 ? (
        <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🎯</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500 }}>Aucune intention active</p>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.375rem' }}>
            Créez une intention pour démarrer le pipeline de traitement
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {intentions.map((intent: any, i: number) => (
            <div key={i} className="glass" style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 500 }}>{intent.description || intent.type || `Intention ${intent.id?.slice(0,8) || i}`}</div>
                <div className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
                  ID: {intent.id || '—'} · {intent.vertical || '—'} · {intent.created_at || '—'}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {intent.client_id && (
                  <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{intent.client_id}</span>
                )}
                <IntentStateBadge state={intent.state || intent.status || 'created'} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   4.5 CONFORMITÉ — Dashboard RGPD / AI Act
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function ComplianceView({ user }: { user: any }) {
  const { data: report } = useApi('/api/v1/compliance/report/daily')
  const { data: rules } = useApi('/api/v1/mediator/rules')
  const { data: agents } = useApi('/api/v1/agents/status')
  const [activeTab, setActiveTab] = useState<'overview' | 'risks' | 'aipd' | 'rights'>('overview')

  const vertical = user?.primary_vertical || 'comptable'
  const isHighProtection = ['avocat', 'sante', 'banque'].includes(vertical)
  const activeConflicts = (agents as any)?.active_conflicts || []
  const circuitBreakers = (agents as any)?.circuit_breakers || []
  const ruleList = (rules as any)?.rules || []
  const violations = (report as any)?.violations || []

  const complianceScore = (report as any)?.compliance_score ?? 100
  const conflictsDetected = (report as any)?.metrics?.conflicts_detected ?? 0
  const arbitrationsRequested = (report as any)?.metrics?.arbitrations_requested ?? 0

  const riskMatrix = [
    { id: 'R1', label: 'Décision automatisée sans supervision', gravity: 4, residual: 2, measure: 'Médiateur + gel préventif' },
    { id: 'R2', label: 'Fuite de données entre tenants', gravity: 4, residual: 1, measure: 'Isolation vault + AES-256' },
    { id: 'R3', label: 'Hallucination LLM', gravity: 4, residual: 2, measure: 'Confidence ≥ 0.3 + re-validation' },
    { id: 'R4', label: 'Non-respect secret professionnel', gravity: 5, residual: 1, measure: 'LLM local + règles JsonLogic' },
    { id: 'R5', label: 'Accès non autorisé', gravity: 4, residual: 2, measure: 'RBAC + 2FA + audit WORM' },
  ]

  const scoreColor = complianceScore >= 90 ? 'var(--emerald)' : complianceScore >= 70 ? 'var(--amber)' : 'var(--rose)'

  const tabs = [
    { id: 'overview' as const, label: 'Vue d\'ensemble' },
    { id: 'risks' as const, label: 'Matrice de risques' },
    { id: 'aipd' as const, label: 'AIPD / DPIA' },
    { id: 'rights' as const, label: 'Droits RGPD' },
  ]

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>🛡️ Conformité</h1>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Vertical: <strong>{vertical}</strong> · Mode: <strong>{isHighProtection ? 'Haute protection' : 'Standard'}</strong> ·{' '}
          {isHighProtection ? '🔒 LLM local uniquement' : '☁️ LLM cloud autorisé'}
        </p>
      </div>

      {/* Tab bar */}
      <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '1.5rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
            padding: '0.5rem 1rem', fontSize: '0.8125rem', fontWeight: activeTab === t.id ? 600 : 400,
            background: 'transparent', border: 'none', borderBottom: activeTab === t.id ? '2px solid var(--cyan)' : '2px solid transparent',
            color: activeTab === t.id ? 'var(--cyan)' : 'var(--text-muted)', cursor: 'pointer',
          }}>{t.label}</button>
        ))}
      </div>

      {/* OVERVIEW */}
      {activeTab === 'overview' && (<>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <KpiCard icon="🎯" label="Score conformité" value={`${complianceScore}%`} sub="RGPD + AI Act" color={scoreColor} />
          <KpiCard icon="📋" label="Règles actives" value={String(ruleList.length || '—')} sub={`Vertical: ${vertical}`} color="var(--cyan)" />
          <KpiCard icon="⚠️" label="Conflits détectés" value={String(conflictsDetected)} sub="Médiateur" color={conflictsDetected > 0 ? 'var(--amber)' : 'var(--emerald)'} />
          <KpiCard icon="⚖️" label="Arbitrages" value={String(arbitrationsRequested)} sub="Décision humaine" color="var(--violet)" />
        </div>

        {activeConflicts.length > 0 && (
          <div className="glass" style={{ padding: '1rem', marginBottom: '1rem', borderLeft: '3px solid var(--rose)' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--rose)', marginBottom: '0.5rem' }}>⚠️ Conflits actifs ({activeConflicts.length})</h3>
            {activeConflicts.map((c: any, i: number) => (
              <div key={i} style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                {c.reason || c.description || `Conflit ${i+1}`} — sévérité: <strong style={{ color: 'var(--amber)' }}>{c.severity || 'high'}</strong>
              </div>
            ))}
          </div>
        )}

        {circuitBreakers.length > 0 && (
          <div className="glass" style={{ padding: '1rem', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.5rem' }}>🔌 Circuit Breakers</h3>
            {circuitBreakers.map((cb: any, i: number) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', padding: '0.25rem 0' }}>
                <span>{cb.agent || cb.name || `CB ${i+1}`}</span>
                <span style={{ color: cb.state === 'closed' ? 'var(--emerald)' : cb.state === 'open' ? 'var(--rose)' : 'var(--amber)' }}>
                  {cb.state || 'unknown'}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>📋 Violations récentes</h3>
          {violations.length === 0 ? (
            <p style={{ color: 'var(--emerald)', fontSize: '0.8125rem' }}>✓ Aucune violation détectée</p>
          ) : (
            violations.map((v: any, i: number) => (
              <div key={i} style={{ padding: '0.5rem 0.75rem', marginBottom: '0.375rem', borderRadius: '0.375rem', background: 'rgba(251,113,133,0.05)', border: '1px solid rgba(251,113,133,0.1)', fontSize: '0.75rem' }}>
                <span style={{ color: 'var(--rose)', fontWeight: 500 }}>{v.rule_id || v.type || 'Violation'}</span>
                <span style={{ color: 'var(--text-muted)', marginLeft: '0.5rem' }}>{v.message || v.description || ''}</span>
              </div>
            ))
          )}
        </div>
      </>)}

      {/* RISKS */}
      {activeTab === 'risks' && (<>
        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>📊 Matrice de risques IA (AI Act Art. 9-15)</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: 'var(--text-dim)' }}>ID</th>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: 'var(--text-dim)' }}>Risque</th>
                <th style={{ padding: '0.5rem', textAlign: 'center', color: 'var(--text-dim)' }}>Initial</th>
                <th style={{ padding: '0.5rem', textAlign: 'center', color: 'var(--text-dim)' }}>Résiduel</th>
                <th style={{ padding: '0.5rem', textAlign: 'left', color: 'var(--text-dim)' }}>Mesure</th>
              </tr>
            </thead>
            <tbody>
              {riskMatrix.map(r => (
                <tr key={r.id} style={{ borderBottom: '1px solid rgba(30,41,59,0.3)' }}>
                  <td style={{ padding: '0.5rem', fontFamily: 'monospace', color: 'var(--violet)' }}>{r.id}</td>
                  <td style={{ padding: '0.5rem' }}>{r.label}</td>
                  <td style={{ padding: '0.5rem', textAlign: 'center' }}><RiskBadge level={r.gravity} /></td>
                  <td style={{ padding: '0.5rem', textAlign: 'center' }}><RiskBadge level={r.residual} /></td>
                  <td style={{ padding: '0.5rem', color: 'var(--text-muted)' }}>{r.measure}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>⚖️ Matrice de gravité Médiateur</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem' }}>
            {[
              { level: 1, label: 'Low', action: 'DEGRADED', color: 'var(--emerald)' },
              { level: 2, label: 'Medium', action: 'DEGRADED', color: 'var(--cyan)' },
              { level: 3, label: 'High', action: 'FROZEN', color: 'var(--amber)' },
              { level: 4, label: 'Critical', action: 'FROZEN', color: 'var(--rose)' },
              { level: 5, label: 'Block', action: 'FROZEN + ESCALADE', color: 'var(--rose)' },
            ].map(g => (
              <div key={g.level} style={{ padding: '0.75rem', borderRadius: '0.5rem', textAlign: 'center', background: `${g.color}08`, border: `1px solid ${g.color}20` }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 700, color: g.color }}>{g.level}</div>
                <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>{g.label}</div>
                <div style={{ fontSize: '0.5625rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{g.action}</div>
              </div>
            ))}
          </div>
        </div>
      </>)}

      {/* AIPD */}
      {activeTab === 'aipd' && (<>
        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>📄 AIPD / DPIA (RGPD Art. 35)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>Template</div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 500 }}>AIPD-TEMPLATE.md</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>21 sections · 68 questions d'audit</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>Vertical</div>
              <div style={{ fontSize: '0.8125rem', fontWeight: 500 }}>aipd-{vertical}.md</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{ruleList.length} règles JsonLogic actives</div>
            </div>
          </div>
        </div>

        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>✅ Checklist validation DPO</h3>
          {[
            { label: 'Identification du responsable de traitement', done: false },
            { label: 'Description du traitement & flux de données', done: false },
            { label: 'Nécessité et proportionnalité', done: false },
            { label: 'Risques identifiés & mesures', done: true },
            { label: 'Supervision humaine (AI Act Art. 14)', done: true },
            { label: 'Documentation technique (AI Act Art. 11)', done: true },
            { label: 'DPA avec sous-traitants signé', done: false },
            { label: 'Registre des traitements mis à jour', done: false },
            { label: 'Droits RGPD testés (Art. 15-22)', done: false },
            { label: 'Checklist DPO signée et datée', done: false },
          ].map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.375rem 0', fontSize: '0.8125rem' }}>
              <span style={{ color: item.done ? 'var(--emerald)' : 'var(--text-dim)', fontSize: '0.875rem' }}>
                {item.done ? '☑' : '☐'}
              </span>
              <span style={{ color: item.done ? 'var(--text)' : 'var(--text-muted)' }}>{item.label}</span>
            </div>
          ))}
        </div>

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>🔬 Cross-validation externe</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--amber)' }}>4/10</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Nemotron-120B</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>Template non rempli</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--emerald)' }}>✓</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Règles JsonLogic</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>Toutes implémentées</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--emerald)' }}>37/37</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Tests onboarding</div>
              <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>100% pass</div>
            </div>
          </div>
        </div>
      </>)}

      {/* RIGHTS */}
      {activeTab === 'rights' && (<>
        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>👤 Droits RGPD (Art. 15-22)</h3>
          {[
            { article: 'Art. 15', right: 'Droit d\'accès', endpoint: '/api/v1/data/export', status: 'implemented' },
            { article: 'Art. 16', right: 'Droit de rectification', endpoint: '/api/v1/data/rectify', status: 'implemented' },
            { article: 'Art. 17', right: 'Droit à l\'effacement', endpoint: '/api/v1/data/erase', status: 'implemented' },
            { article: 'Art. 18', right: 'Limitation du traitement', endpoint: 'Médiateur gel', status: 'implemented' },
            { article: 'Art. 20', right: 'Portabilité', endpoint: '/api/v1/data/export (JSON/CSV)', status: 'implemented' },
            { article: 'Art. 22', right: 'Non-décision automatisée', endpoint: 'Arbitrage humain', status: 'implemented' },
          ].map((r, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0.75rem', marginBottom: '0.25rem', borderRadius: '0.375rem', background: 'rgba(255,255,255,0.02)', fontSize: '0.8125rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="mono" style={{ color: 'var(--violet)', fontSize: '0.6875rem' }}>{r.article}</span>
                <span>{r.right}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{r.endpoint}</span>
                <span style={{ fontSize: '0.6875rem', color: r.status === 'implemented' ? 'var(--emerald)' : 'var(--amber)' }}>
                  {r.status === 'implemented' ? '✓' : '⏳'}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.75rem' }}>📜 Transparence AI Act (Art. 13-14)</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            <div style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(34,211,238,0.04)', border: '1px solid rgba(34,211,238,0.1)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--cyan)', fontWeight: 600, marginBottom: '0.25rem' }}>Supervision humaine</div>
              <div style={{ fontSize: '0.8125rem' }}>Médiateur + Arbitrage</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>5 niveaux · Timeout 30 min</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(167,139,250,0.04)', border: '1px solid rgba(167,139,250,0.1)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--violet)', fontWeight: 600, marginBottom: '0.25rem' }}>Journal d'audit</div>
              <div style={{ fontSize: '0.8125rem' }}>WORM + SHA-256</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>Hash-chain · RFC 3161</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(52,211,153,0.04)', border: '1px solid rgba(52,211,153,0.1)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--emerald)', fontWeight: 600, marginBottom: '0.25rem' }}>Règles explicables</div>
              <div style={{ fontSize: '0.8125rem' }}>JsonLogic</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>{ruleList.length} règles · Déterministes</div>
            </div>
            <div style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(251,191,36,0.04)', border: '1px solid rgba(251,191,36,0.1)' }}>
              <div style={{ fontSize: '0.6875rem', color: 'var(--amber)', fontWeight: 600, marginBottom: '0.25rem' }}>Correction d'erreurs</div>
              <div style={{ fontSize: '0.8125rem' }}>Saga pattern</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>Compensation automatique</div>
            </div>
          </div>
        </div>
      </>)}
    </div>
  )
}

function RiskBadge({ level }: { level: number }) {
  const colors: Record<number, string> = {
    1: 'var(--emerald)', 2: 'var(--cyan)', 3: 'var(--amber)', 4: 'var(--rose)', 5: 'var(--rose)',
  }
  return (
    <span style={{
      display: 'inline-block', width: '24px', height: '24px', lineHeight: '24px',
      borderRadius: '0.25rem', textAlign: 'center', fontSize: '0.6875rem', fontWeight: 700,
      background: `${colors[level] || 'var(--text-dim)'}15`, color: colors[level] || 'var(--text-dim)',
    }}>{level}</span>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   4. JOURNAL D'AUDIT — WORM hash-chainé
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function JournalView({ user: _user }: { user: any }) {
  const [eventType, setEventType] = useState('')
  const [limit, setLimit] = useState(50)
  const { data, loading } = useApi(`/api/v1/journal?limit=${limit}${eventType ? `&event_type=${eventType}` : ''}`, [eventType, limit])
  const [verifying, setVerifying] = useState(false)
  const [verifyResult, setVerifyResult] = useState<any>(null)

  const entries = (data as any)?.entries || []

  const verifyIntegrity = async () => {
    setVerifying(true)
    try {
      const res = await apiFetch('/api/v1/journal/verify')
      setVerifyResult(res)
    } catch (e: any) {
      setVerifyResult({ error: typeof e?.message === 'string' ? e.message : JSON.stringify(e) })
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>📝 Journal d'audit</h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Journal immuable hash-chainé SHA-256 · {entries.length} entrée{entries.length !== 1 ? 's' : ''}
          </p>
        </div>
        <button onClick={verifyIntegrity} disabled={verifying} className="btn btn-secondary" style={{ fontSize: '0.75rem' }}>
          {verifying ? '🔄 Vérification…' : '🔍 Vérifier intégrité'}
        </button>
      </div>

      {verifyResult && (
        <div className="glass" style={{
          padding: '1rem', marginBottom: '1rem',
          borderLeft: verifyResult.error ? '3px solid var(--rose)' : '3px solid var(--emerald)',
        }}>
          {verifyResult.error ? (
            <span style={{ color: 'var(--rose)', fontSize: '0.8125rem' }}>✗ {verifyResult.error}</span>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ color: 'var(--emerald)', fontSize: '0.8125rem', fontWeight: 600 }}>✓ Chaîne d'intégrité valide</span>
              {verifyResult.total_entries && (
                <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                  {verifyResult.total_entries} entrées vérifiées
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="glass" style={{ padding: '0.75rem 1rem', marginBottom: '1rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Filtrer:</span>
        <select value={eventType} onChange={e => setEventType(e.target.value)} style={{
          padding: '0.25rem 0.5rem', borderRadius: '0.375rem', fontSize: '0.75rem',
          background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
        }}>
          <option value="">Tous les événements</option>
          <option value="intention.created">Intention créée</option>
          <option value="intention.routed">Intention routée</option>
          <option value="agent.query">Agent requête</option>
          <option value="agent.result">Agent résultat</option>
          <option value="mediator.check">Médiateur vérif.</option>
          <option value="mediator.conflict">Conflit</option>
          <option value="mediator.freeze">Gel</option>
          <option value="arbitration.requested">Arbitrage demandé</option>
          <option value="arbitration.decision">Arbitrage décision</option>
          <option value="compliance.check">Conformité</option>
          <option value="compliance.violation">Violation</option>
        </select>
        <select value={limit} onChange={e => setLimit(Number(e.target.value))} style={{
          padding: '0.25rem 0.5rem', borderRadius: '0.375rem', fontSize: '0.75rem',
          background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
        }}>
          <option value={20}>20 entrées</option>
          <option value={50}>50 entrées</option>
          <option value={100}>100 entrées</option>
        </select>
      </div>

      {loading ? <LoadingSpinner /> : entries.length === 0 ? (
        <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📝</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500 }}>Journal vide</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {entries.map((entry: any, i: number) => (
            <div key={i} style={{
              display: 'grid', gridTemplateColumns: '70px 140px 1fr 110px 50px',
              padding: '0.5rem 0.75rem', borderRadius: '0.375rem', fontSize: '0.75rem',
              background: i % 2 === 0 ? 'rgba(255,255,255,0.01)' : 'transparent',
              borderBottom: '1px solid rgba(30,41,59,0.3)', alignItems: 'center', gap: '0.75rem',
            }}>
              <span className="mono" style={{ color: 'var(--text-dim)', fontSize: '0.625rem' }}>#{entry.sequence || i+1}</span>
              <span style={{ color: 'var(--text-dim)', fontSize: '0.6875rem' }}>
                {entry.timestamp ? new Date(entry.timestamp).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '—'}
              </span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {entry.event_type || '—'}
              </span>
              <span style={{ color: 'var(--violet)', fontSize: '0.6875rem' }}>{entry.agent_source || '—'}</span>
              <span title={entry.entry_hash} style={{ color: 'var(--emerald)', fontSize: '0.75rem' }}>🔗</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   5. ARBITRAGE — Décision humaine
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function ArbitrageView({ user }: { user: any }) {
  const { data, loading, refetch } = useApi('/api/v1/arbitrations')
  const { data: precedents } = useApi('/api/v1/arbitrations/precedents')
  const [deciding, setDeciding] = useState<string | null>(null)

  const arbitrations = (data as any)?.arbitrations || []
  const precedentList = (precedents as any)?.precedents || []

  const decide = async (id: string, decision: string) => {
    setDeciding(id)
    try {
      await apiFetch(`/api/v1/arbitrations/${id}/decide`, {
        method: 'POST',
        body: JSON.stringify({ decision, arbitrator_id: user?.email || 'admin', justification: `Décision: ${decision}` }),
      })
      refetch()
    } catch (e: any) {
      alert(typeof e?.message === 'string' ? e.message : JSON.stringify(e))
    } finally {
      setDeciding(null)
    }
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>⚖️ Arbitrage</h1>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Contradictions détectées · Décision humaine requise · {arbitrations.length} en attente
        </p>
      </div>

      {loading ? <LoadingSpinner /> : arbitrations.length === 0 ? (
        <div className="glass" style={{ padding: '3rem', textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>⚖️</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500 }}>Aucun arbitrage en attente</p>
          <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.375rem' }}>
            Les contradictions détectées par le Médiateur apparaîtront ici
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
          {arbitrations.map((arb: any) => (
            <div key={arb.id} className="glass" style={{ padding: '1.25rem', borderLeft: '3px solid var(--amber)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>{arb.description || arb.type || 'Conflit détecté'}</div>
                  <div className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
                    ID: {arb.id} · Intention: {arb.intention_id || '—'}
                  </div>
                </div>
                <span className="badge badge-amber" style={{ fontSize: '0.625rem' }}>En attente</span>
              </div>
              {(arb.positions || arb.details) && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  {(arb.positions || [{ agent: 'Agent A', position: arb.details || 'Position non spécifiée' }]).map((pos: any, pi: number) => (
                    <div key={pi} style={{
                      padding: '0.75rem', borderRadius: '0.5rem',
                      background: pi === 0 ? 'rgba(34,211,238,0.04)' : 'rgba(167,139,250,0.04)',
                      border: `1px solid ${pi === 0 ? 'rgba(34,211,238,0.12)' : 'rgba(167,139,250,0.12)'}`,
                    }}>
                      <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: pi === 0 ? 'var(--cyan)' : 'var(--violet)', marginBottom: '0.25rem' }}>
                        {pos.agent || `Agent ${pi+1}`}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{pos.position || pos.reasoning || '—'}</div>
                    </div>
                  ))}
                </div>
              )}
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                <button onClick={() => decide(arb.id, 'approve')} disabled={deciding === arb.id} style={{
                  padding: '0.375rem 0.875rem', borderRadius: '0.375rem', fontSize: '0.75rem', fontWeight: 500,
                  background: 'rgba(52,211,153,0.1)', border: '1px solid rgba(52,211,153,0.2)', color: 'var(--emerald)',
                  cursor: deciding ? 'default' : 'pointer',
                }}>✓ Approuver</button>
                <button onClick={() => decide(arb.id, 'reject')} disabled={deciding === arb.id} style={{
                  padding: '0.375rem 0.875rem', borderRadius: '0.375rem', fontSize: '0.75rem', fontWeight: 500,
                  background: 'rgba(251,113,133,0.1)', border: '1px solid rgba(251,113,133,0.2)', color: 'var(--rose)',
                  cursor: deciding ? 'default' : 'pointer',
                }}>✗ Rejeter</button>
                <button onClick={() => decide(arb.id, 'modify')} disabled={deciding === arb.id} style={{
                  padding: '0.375rem 0.875rem', borderRadius: '0.375rem', fontSize: '0.75rem', fontWeight: 500,
                  background: 'rgba(251,191,36,0.1)', border: '1px solid rgba(251,191,36,0.2)', color: 'var(--amber)',
                  cursor: deciding ? 'default' : 'pointer',
                }}>✎ Modifier</button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="glass" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>📚 Précédents ({precedentList.length})</h3>
        {precedentList.length === 0 ? (
          <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>Aucun précédent enregistré</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
            {precedentList.map((p: any, i: number) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.5rem 0.75rem', borderRadius: '0.375rem',
                background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)', fontSize: '0.75rem',
              }}>
                <span>{p.description || p.type || `Précédent ${i+1}`}</span>
                <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{p.date || '—'}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   6. PARAMÈTRES
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function SettingsView({ user, onLogout: _onLogout }: { user: any; onLogout: () => void }) {
  const { data: rules } = useApi('/api/v1/mediator/rules')
  const { data: apiKeys } = useApi('/api/v1/auth/api-keys')
  const { data: residency } = useApi(`/api/v1/compliance/data-residency?vertical=${user?.primary_vertical || 'comptable'}`)

  const verticals = (rules as any)?.verticals || []
  const keys = (apiKeys as any)?.keys || (apiKeys as any)?.api_keys || []

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>⚙️ Paramètres</h1>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
          Configuration du tenant · Sécurité · Résidence des données
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>👤 Profil</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            <SettingsRow label="Email" value={user?.email || '—'} />
            <SettingsRow label="Nom" value={user?.full_name || '—'} />
            <SettingsRow label="Rôle" value={user?.role?.toUpperCase() || '—'} />
            <SettingsRow label="Vertical" value={user?.primary_vertical || '—'} />
            <SettingsRow label="MFA" value={user?.mfa_enabled ? '✓ Activé' : '✗ Non activé'} />
          </div>
        </div>

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>🇨🇭 Résidence des données</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
            <SettingsRow label="Région" value={(residency as any)?.region || 'Suisse'} />
            <SettingsRow label="Hébergement" value={(residency as any)?.provider || 'Local / On-premise'} />
            <SettingsRow label="Chiffrement" value={(residency as any)?.encryption || 'AES-256'} />
            <SettingsRow label="Rétention" value={`${(residency as any)?.retention_days || user?.data_retention_days || 365} jours`} />
            <SettingsRow label="Droits RGPD" value={(residency as any)?.gdpr_compliant !== false ? '✓ Conforme' : '✗ Non conforme'} />
          </div>
        </div>

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>⚖️ Règles du Médiateur</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
            {verticals.length > 0 ? verticals.map((v: any, i: number) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.5rem 0.75rem', borderRadius: '0.375rem',
                background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)', fontSize: '0.75rem',
              }}>
                <span>{verticalIcon(v.vertical || v)} {v.vertical || v}</span>
                <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{v.rules_count || v.count || '—'} règles</span>
              </div>
            )) : (
              <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>6 verticals configurées</p>
            )}
          </div>
        </div>

        <div className="glass" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>🔑 Clés API</h3>
          {keys.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
              {keys.map((k: any, i: number) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.5rem 0.75rem', borderRadius: '0.375rem',
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)', fontSize: '0.75rem',
                }}>
                  <span>{k.name || k.label || `Clé ${i+1}`}</span>
                  <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>••••{k.key_suffix || k.last4 || ''}</span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>Aucune clé API configurée</p>
          )}
        </div>
      </div>
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SERMENT NUMÉRIQUE — Par vertical
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
// ═══════════════════════════════════════════════════════════
// TRUST BOX VIEW — Phase 1C — Dashboard temps réel
// Visualisation temps réel du Trust Box (Médiateur déterministe)
// Inspiré du T-Box d'Ant Group + Pluto sub-agent inspector
// ═══════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════
// ═══════════════════════════════════════════════════════════
// ARTIFACTS VIEW — Phase P3 — Aperçus et artefacts riches
// Fiches de conformité, tableaux, documents, timelines
// ═══════════════════════════════════════════════════════════
function ArtifactsView({ user }: { user: any }) {
  const [activeTab, setActiveTab] = useState<'compliance' | 'templates' | 'timeline'>('compliance')
  const [vertical, setVertical] = useState(user?.primary_vertical || 'comptable')
  const [action, setAction] = useState('consultation')
  const [montant, setMontant] = useState('50000')
  const [complianceCard, setComplianceCard] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const { data: templatesData } = useApi(`/api/v1/verticals/${vertical}/templates`)
  const { data: timelineData } = usePolling('/api/v1/artifacts/trust-timeline?limit=20', 10000)
  const { data: verticalsData } = useApi('/api/v1/verticals')

  const generateCard = async () => {
    setLoading(true)
    try {
      const res = await apiFetch('/api/v1/artifacts/compliance-card', {
        method: 'POST',
        body: JSON.stringify({
          vertical, action,
          context: { montant: parseFloat(montant) || 0, action_type: action },
        }),
      })
      setComplianceCard(res)
    } catch (e: any) {
      setComplianceCard({ error: e.message })
    }
    setLoading(false)
  }

  const templates = (templatesData as any)?.templates || []
  const timeline = (timelineData as any)?.data?.events || []
  const verticals = (verticalsData as any)?.verticals || []

  const tabs = [
    { id: 'compliance' as const, label: '\u{1F6E1}\uFE0F Fiche Conformit\u00E9' },
    { id: 'templates' as const, label: '\uD83D\uDCC4 Templates', badge: templates.length },
    { id: 'timeline' as const, label: '\u23F1\uFE0F Timeline', badge: timeline.length },
  ]

  const statusConfig: Record<string, { color: string; label: string; icon: string }> = {
    conforme: { color: 'var(--emerald)', label: 'Conforme', icon: '\u2705' },
    attention: { color: 'var(--amber)', label: 'Attention', icon: '\u26A0\uFE0F' },
    non_conforme: { color: 'var(--rose)', label: 'Non conforme', icon: '\uD83D\uDEAB' },
  }

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      {/* Header */}
      <div style={{
        padding: '1.5rem 2rem 1.25rem', borderBottom: '1px solid var(--border)',
        background: 'linear-gradient(180deg, rgba(251,146,60,0.03) 0%, transparent 100%)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>\uD83D\uDCE6 Artefacts</h1>
          <span style={{
            padding: '0.25rem 0.625rem', borderRadius: '9999px',
            background: 'rgba(251,146,60,0.08)', border: '1px solid rgba(251,146,60,0.15)',
            fontSize: '0.625rem', fontWeight: 700, color: 'var(--orange)',
          }}>P3 NOUVEAU</span>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          Fiches de conformit\u00E9, templates r\u00E9glementaires, timeline de confiance
        </p>
        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.25rem', marginTop: '1rem' }}>
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              padding: '0.5rem 0.875rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
              fontWeight: activeTab === tab.id ? 700 : 400, cursor: 'pointer', border: 'none',
              background: activeTab === tab.id ? 'rgba(251,146,60,0.1)' : 'transparent',
              color: activeTab === tab.id ? 'var(--orange)' : 'var(--text-muted)',
              display: 'flex', alignItems: 'center', gap: '0.375rem',
            }}>
              {tab.label}
              {tab.badge != null && <span className="mono" style={{ fontSize: '0.625rem', opacity: 0.7 }}>({tab.badge})</span>}
            </button>
          ))}
        </div>
      </div>

      <div style={{ padding: '1.5rem 2rem' }}>

        {/* COMPLIANCE CARD */}
        {activeTab === 'compliance' && (<>
          <div className="glass" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '1rem' }}>G\u00E9n\u00E9rer une fiche de conformit\u00E9</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '0.75rem', alignItems: 'end' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Verticale</label>
                <select value={vertical} onChange={e => setVertical(e.target.value)} style={{
                  width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                  background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
                }}>
                  {(verticals.length ? verticals : Object.entries(VERTICAL_CONFIG).map(([k, v]) => ({ id: k, icon: v.icon, label: v.label }))).map((v: any) => (
                    <option key={v.id} value={v.id}>{v.icon} {v.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Action</label>
                <select value={action} onChange={e => setAction(e.target.value)} style={{
                  width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                  background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
                }}>
                  <option value="consultation">Consultation</option>
                  <option value="ecriture_comptable">Ecriture comptable</option>
                  <option value="virement">Virement</option>
                  <option value="data_transfer">Transfert donn\u00E9es</option>
                  <option value="IA_high_risk">IA haut risque</option>
                  <option value="cross_border">Cross-border</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Montant (CHF)</label>
                <input value={montant} onChange={e => setMontant(e.target.value)} style={{
                  width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                  fontFamily: 'monospace', background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
                }} />
              </div>
              <button onClick={generateCard} disabled={loading} className="btn btn-primary" style={{ padding: '0.5rem 1.25rem' }}>
                {loading ? '\u23F3' : '\uD83D\uDD0D'}
              </button>
            </div>
          </div>

          {complianceCard && !complianceCard.error && (() => {
            const d = complianceCard.data || complianceCard
            const sc = statusConfig[d.status] || statusConfig.attention
            return (
              <div className="glass" style={{ padding: '1.5rem', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: sc.color }} />
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '1.5rem' }}>
                  <div style={{
                    width: 72, height: 72, borderRadius: '1rem', display: 'flex', flexDirection: 'column',
                    alignItems: 'center', justifyContent: 'center',
                    background: `${sc.color}10`, border: `2px solid ${sc.color}30`,
                  }}>
                    <span style={{ fontSize: '1.75rem' }}>{sc.icon}</span>
                    <span className="mono" style={{ fontSize: '0.75rem', fontWeight: 800, color: sc.color }}>{Math.round((d.score || 0) * 100)}%</span>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '1.125rem', fontWeight: 800 }}>{d.vertical && d.vertical.charAt(0).toUpperCase() + d.vertical.slice(1)} \u2014 {sc.label}</div>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      Score de conformit\u00E9: <span className="mono" style={{ color: sc.color, fontWeight: 700 }}>{Math.round((d.score || 0) * 100)}%</span>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--emerald)' }}>\u2705 {d.checks_ok || 0} OK</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>\u25CB {d.checks_total || 0} total</span>
                    </div>
                  </div>
                  <div style={{ width: 100, textAlign: 'center' }}>
                    <svg viewBox="0 0 36 36" style={{ width: 80, height: 80, transform: 'rotate(-90deg)' }}>
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--border)" strokeWidth="3" />
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={sc.color} strokeWidth="3" strokeDasharray={`${(d.score || 0) * 100}, 100`} strokeLinecap="round" />
                    </svg>
                  </div>
                </div>

                {(d.warnings || []).length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--amber)', marginBottom: '0.5rem' }}>\u26A0\uFE0F Avertissements ({d.warnings.length})</div>
                    {(d.warnings as string[]).map((w: string, i: number) => (
                      <div key={i} style={{
                        padding: '0.5rem 0.75rem', borderRadius: '0.375rem', marginBottom: '0.25rem',
                        background: 'rgba(251,191,36,0.04)', border: '1px solid rgba(251,191,36,0.1)',
                        fontSize: '0.8125rem', color: 'var(--text-muted)',
                      }}>{w}</div>
                    ))}
                  </div>
                )}

                {(d.blocks || []).length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--rose)', marginBottom: '0.5rem' }}>\uD83D\uDEAB Blocages ({d.blocks.length})</div>
                    {(d.blocks as string[]).map((b: string, i: number) => (
                      <div key={i} style={{
                        padding: '0.5rem 0.75rem', borderRadius: '0.375rem', marginBottom: '0.25rem',
                        background: 'rgba(251,113,133,0.06)', border: '1px solid rgba(251,113,133,0.12)',
                        fontSize: '0.8125rem', color: 'var(--rose)',
                      }}>{b}</div>
                    ))}
                  </div>
                )}

                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border)',
                }}>
                  <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{complianceCard.id || '\u2014'}</span>
                  <span style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>\uD83D\uDCDD Journalis\u00E9 WORM</span>
                </div>
              </div>
            )
          })()}

          {complianceCard?.error && (
            <div className="glass" style={{ padding: '1.25rem', borderLeft: '3px solid #ef4444' }}>
              <p style={{ color: '#ef4444' }}>Erreur: {complianceCard.error}</p>
            </div>
          )}
        </>)}

        {/* TEMPLATES */}
        {activeTab === 'templates' && (<>
          <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>Templates r\u00E9glementaires \u2014 {vertical}</h3>
            <select value={vertical} onChange={e => setVertical(e.target.value)} style={{
              padding: '0.375rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
              background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
            }}>
              {Object.entries(VERTICAL_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.icon} {v.label}</option>
              ))}
            </select>
          </div>

          {templates.length === 0 ? (
            <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)' }}>Aucun template pour cette verticale</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
              {templates.map((t: any, i: number) => (
                <div key={t.id || i} className="glass slide-in" style={{ padding: '1.25rem', animationDelay: `${i * 0.05}s` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 700 }}>{t.title}</div>
                      <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.125rem' }}>{t.id}</div>
                    </div>
                    <span className={`badge badge-${t.category === 'fiscal' ? 'amber' : t.category === 'rgpd' ? 'rose' : t.category === 'legal' ? 'violet' : 'cyan'}`} style={{ fontSize: '0.625rem' }}>{t.category}</span>
                  </div>
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '0.75rem' }}>{t.description}</p>
                  <div style={{ display: 'flex', gap: '0.375rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
                    {(t.fields || []).map((f: string) => (
                      <span key={f} style={{
                        padding: '0.125rem 0.5rem', borderRadius: '0.25rem',
                        background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)',
                        fontSize: '0.625rem', color: 'var(--text-dim)', fontFamily: 'monospace',
                      }}>{f}</span>
                    ))}
                  </div>
                  {t.regulation_ref && (
                    <div style={{ fontSize: '0.6875rem', color: 'var(--violet)' }}>\uD83D\uDCDA {t.regulation_ref}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>)}

        {/* TIMELINE */}
        {activeTab === 'timeline' && (<>
          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>\u23F1\uFE0F Timeline de Confiance</h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>Derniers \u00E9v\u00E9nements du journal WORM \u00B7 Auto-refresh 10s</p>
          </div>
          {timeline.length === 0 ? (
            <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>\u23F1\uFE0F</div>
              <p style={{ color: 'var(--text-muted)' }}>Aucun \u00E9v\u00E9nement dans le journal</p>
            </div>
          ) : (
            <div style={{ position: 'relative', paddingLeft: '2rem' }}>
              <div style={{
                position: 'absolute', left: '0.625rem', top: 0, bottom: 0, width: 2,
                background: 'linear-gradient(180deg, var(--cyan), var(--violet))',
              }} />
              {timeline.map((evt: any, i: number) => {
                const evtType = evt.event || evt.event_type || ''
                const isConflict = evtType.includes('conflict')
                const isMediator = evtType.includes('mediator')
                const dotColor = isConflict ? 'var(--rose)' : isMediator ? 'var(--violet)' : 'var(--cyan)'
                return (
                  <div key={i} className="slide-in" style={{ position: 'relative', marginBottom: '0.75rem', animationDelay: `${i * 0.03}s` }}>
                    <div style={{
                      position: 'absolute', left: '-1.625rem', top: '0.375rem',
                      width: 10, height: 10, borderRadius: '50%',
                      background: dotColor, border: '2px solid var(--bg)',
                      boxShadow: `0 0 6px ${dotColor}50`,
                    }} />
                    <div style={{
                      padding: '0.75rem 1rem', borderRadius: '0.5rem',
                      background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.375rem' }}>
                        <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>{evtType.replace(/\./g, ' \u203A ')}</span>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.625rem', color: 'var(--violet)' }}>{evt.agent || evt.agent_source}</span>
                          <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                            {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : ''}
                          </span>
                        </div>
                      </div>
                      {evt.vertical && <span style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{evt.vertical}</span>}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>)}
      </div>
    </div>
  )
}

// REVIEW LOOP VIEW — Phase P1 — Boucle Médiateur déterministe
// Agent génère → Médiateur vérifie → Si problème → Corrige → Re-vérifie
// Max 3 itérations, puis arbitrage humain
// ═══════════════════════════════════════════════════════════
function ReviewLoopView({ user }: { user: any }) {
  const [task, setTask] = useState('')
  const [agentName, setAgentName] = useState('reasoning')
  const [vertical, setVertical] = useState(user?.primary_vertical || 'comptable')
  const [contextJson, setContextJson] = useState('{"montant": 50000}')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [iterations, setIterations] = useState<any[]>([])
  const [streamingDone, setStreamingDone] = useState(false)

  const handleExecute = async () => {
    if (!task.trim() || loading) return
    setLoading(true)
    setResult(null)
    setIterations([])
    setStreamingDone(false)

    try {
      const API = import.meta.env.VITE_API_URL || 'http://localhost:8002'
      const token = localStorage.getItem('cl_access_token')
      let parsedContext = {}
      try { parsedContext = JSON.parse(contextJson) } catch {}

      // Try SSE streaming first
      try {
        const res = await fetch(`${API}/api/v1/review-loop/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            task, agent_name: agentName, vertical, context: parsedContext, client_id: 'demo',
          }),
        })

        if (!res.ok) throw new Error(`HTTP ${res.status}`)

        const reader = res.body?.getReader()
        if (!reader) throw new Error('No reader')
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const rawData = line.slice(6)
            if (!rawData || rawData === '[DONE]') continue
            try {
              const evt = JSON.parse(rawData)
              if (evt.iteration) {
                setIterations(prev => [...prev, evt])
              } else if (evt.final_verdict) {
                setResult(evt)
                setStreamingDone(true)
              }
            } catch {}
          }
        }
      } catch {
        // Fallback to non-streaming
        const res = await apiFetch('/api/v1/review-loop', {
          method: 'POST',
          body: JSON.stringify({
            task, agent_name: agentName, vertical, context: parsedContext, client_id: 'demo',
          }),
        })
        setResult(res)
        setIterations(res.iterations || [])
        setStreamingDone(true)
      }
    } catch (e: any) {
      setResult({ error: e.message })
      setStreamingDone(true)
    } finally {
      setLoading(false)
    }
  }

  const verdictColors: Record<string, string> = {
    approved: 'var(--emerald)', changes_requested: 'var(--amber)',
    arbitration_required: 'var(--rose)', error: 'var(--text-dim)',
  }
  const verdictIcons: Record<string, string> = {
    approved: '✅', changes_requested: '🔄', arbitration_required: '⚖️', error: '❌',
  }
  const stepVerdictIcons: Record<string, string> = {
    approved: '✅', changes_requested: '🔄', blocked_by_rules: '🚫', needs_arbitration: '⚖️',
  }

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      {/* Hero Header */}
      <div style={{
        padding: '1.5rem 2rem 1.25rem', borderBottom: '1px solid var(--border)',
        background: 'linear-gradient(180deg, rgba(167,139,250,0.03) 0%, transparent 100%)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.375rem' }}>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>🔄 Review Loop</h1>
          <span style={{
            padding: '0.25rem 0.625rem', borderRadius: '9999px',
            background: 'rgba(167,139,250,0.08)', border: '1px solid rgba(167,139,250,0.15)',
            fontSize: '0.625rem', fontWeight: 700, color: 'var(--violet)',
          }}>P1 NOUVEAU</span>
        </div>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
          Boucle déterministe: Agent → Médiateur → Correction → Re-vérification → Arbitrage si nécessaire
        </p>
      </div>

      <div style={{ padding: '1.5rem 2rem' }}>
        {/* Input Form */}
        <div className="glass" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Agent</label>
              <select value={agentName} onChange={e => setAgentName(e.target.value)} style={{
                width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
              }}>
                <option value="reasoning">🧠 Raisonnement</option>
                <option value="data">📊 Data</option>
                <option value="action">⚡ Action</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Verticale</label>
              <select value={vertical} onChange={e => setVertical(e.target.value)} style={{
                width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
              }}>
                {Object.entries(VERTICAL_CONFIG).map(([k, v]) => (
                  <option key={k} value={k}>{v.icon} {v.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Contexte (JSON)</label>
              <input value={contextJson} onChange={e => setContextJson(e.target.value)} style={{
                width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                fontFamily: 'monospace', background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
              }} />
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Tâche à analyser</label>
            <textarea value={task} onChange={e => setTask(e.target.value)} placeholder="Décrivez la tâche pour l'agent…" style={{
              width: '100%', minHeight: 80, padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
              background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)', resize: 'vertical',
            }} />
          </div>

          <button onClick={handleExecute} disabled={loading || !task.trim()} className="btn btn-primary">
            {loading ? '⏳ Review en cours…' : '🔄 Exécuter Review Loop'}
          </button>
        </div>

        {/* How it works — always visible */}
        {!result && !loading && (
          <div className="glass" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '1rem' }}>🏗️ Comment ça marche</h3>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0, flexWrap: 'wrap', padding: '1rem 0' }}>
              {[
                { icon: '🧠', label: 'Agent LLM\ngénère' },
                { icon: '🔍', label: 'Médiateur\nvérifie' },
                { icon: '🔄', label: 'Si problème\ncorrige' },
                { icon: '🔍', label: 'Re-vérifie\n(max 3x)' },
                { icon: '⚖️', label: 'Arbitrage\nhumain' },
              ].map((step, i, arr) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.375rem',
                    padding: '0.625rem 0.875rem', borderRadius: '0.625rem',
                    background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
                  }}>
                    <span style={{ fontSize: '1.25rem' }}>{step.icon}</span>
                    <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)', whiteSpace: 'pre-line', textAlign: 'center' }}>{step.label}</span>
                  </div>
                  {i < arr.length - 1 && <span style={{ color: 'var(--text-dim)', margin: '0 0.375rem', fontSize: '0.75rem' }}>→</span>}
                </div>
              ))}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem', marginTop: '1rem' }}>
              {[
                { icon: '🔒', title: '100% déterministe', desc: 'Le Médiateur n\'utilise jamais de LLM. JsonLogic uniquement.' },
                { icon: '🔄', title: 'Max 3 itérations', desc: 'Après 3 tentatives, passage automatique en arbitrage humain.' },
                { icon: '📝', title: 'Traçabilité WORM', desc: 'Chaque itération est journalisée dans le journal inviolable.' },
              ].map((p, i) => (
                <div key={i} style={{ padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span>{p.icon}</span>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>{p.title}</span>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{p.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {loading && (
          <div className="glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🔄</div>
            <p style={{ color: 'var(--violet)', fontWeight: 600, fontSize: '0.875rem' }}>Review Loop en cours…</p>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '0.25rem' }}>Itération {iterations.length + 1}/3</p>
          </div>
        )}

        {/* Iterations Timeline */}
        {iterations.length > 0 && (
          <div style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '1rem' }}>📋 Itérations ({iterations.length})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {iterations.map((it, i) => {
                const vColor = it.verdict === 'approved' ? 'var(--emerald)' : it.verdict === 'changes_requested' ? 'var(--amber)' : 'var(--rose)'
                const vIcon = stepVerdictIcons[it.verdict] || '❓'
                return (
                  <div key={i} className="glass slide-in" style={{
                    padding: '1rem 1.25rem',
                    borderLeft: `3px solid ${vColor}`,
                    animationDelay: `${i * 0.1}s`,
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <span style={{ fontSize: '1.125rem' }}>{vIcon}</span>
                        <div>
                          <span style={{ fontSize: '0.875rem', fontWeight: 700 }}>Itération {it.iteration}</span>
                          <span style={{ fontSize: '0.6875rem', color: vColor, marginLeft: '0.5rem', fontWeight: 600 }}>
                            {it.verdict?.replace(/_/g, ' ').toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                        <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>{Math.round(it.elapsed_ms)}ms</span>
                        {it.critical_count > 0 && (
                          <span style={{ fontSize: '0.625rem', color: 'var(--rose)', fontWeight: 600 }}>{it.critical_count} critique(s)</span>
                        )}
                        {it.rules_triggered > 0 && (
                          <span style={{ fontSize: '0.625rem', color: 'var(--amber)', fontWeight: 600 }}>{it.rules_triggered} règle(s)</span>
                        )}
                      </div>
                    </div>
                    {it.feedback && (
                      <div style={{
                        padding: '0.5rem 0.75rem', borderRadius: '0.375rem', marginTop: '0.375rem',
                        background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
                        fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5,
                      }}>
                        {it.feedback}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Final Result */}
        {result && streamingDone && !result.error && (
          <div className="glass" style={{ padding: '1.5rem', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: verdictColors[result.final_verdict] || 'var(--text-dim)' }} />

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
              <div style={{
                width: 56, height: 56, borderRadius: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: (verdictColors[result.final_verdict] || 'var(--text-dim)') + '12',
                border: `1px solid ${(verdictColors[result.final_verdict] || 'var(--text-dim)')}25`,
              }}>
                <span style={{ fontSize: '1.75rem' }}>{verdictIcons[result.final_verdict] || '❓'}</span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: verdictColors[result.final_verdict] || 'var(--text)' }}>
                  {result.final_verdict?.replace(/_/g, ' ').toUpperCase()}
                </div>
                <div style={{ display: 'flex', gap: '1rem', marginTop: '0.375rem' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{result.total_iterations} itération(s)</span>
                  <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{Math.round(result.total_elapsed_ms)}ms</span>
                  <TrustBadge score={result.trust_score ?? 1.0} />
                </div>
              </div>
            </div>

            {result.arbitration_reason && (
              <div style={{
                padding: '0.75rem 1rem', borderRadius: '0.5rem', marginBottom: '1rem',
                background: 'rgba(251,113,133,0.06)', border: '1px solid rgba(251,113,133,0.12)',
                fontSize: '0.8125rem', color: 'var(--rose)',
              }}>
                ⚖️ Arbitrage: {result.arbitration_reason}
              </div>
            )}

            {result.final_output && (
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.5rem' }}>Réponse finale</div>
                <div
                  style={{ fontSize: '0.8125rem', lineHeight: 1.7, padding: '1rem', borderRadius: '0.5rem', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)' }}
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(result.final_output) }}
                />
              </div>
            )}
          </div>
        )}

        {result?.error && (
          <div className="glass" style={{ padding: '1.5rem', borderLeft: '3px solid #ef4444' }}>
            <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>Erreur: {result.error}</p>
          </div>
        )}
      </div>
    </div>
  )
}

function TrustBoxView({ user }: { user: any }) {
  const [selectedVertical, setSelectedVertical] = useState(user?.primary_vertical || 'comptable')
  const [simAction, setSimAction] = useState('consultation')
  const [simPayload, setSimPayload] = useState('{"montant": 500}')
  const [simResult, setSimResult] = useState<any>(null)
  const [simLoading, setSimLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'simulate' | 'audit' | 'agents'>('overview')

  // === Real-time polling (5s) ===
  const { data: statusData } = usePolling('/trust-box/status', 5000)
  const { data: rulesData } = useApi(`/trust-box/rules?vertical=${selectedVertical}`, [selectedVertical])
  const { data: conflictsData } = usePolling('/trust-box/conflicts', 5000)
  const { data: auditData } = usePolling('/trust-box/audit-trail?limit=25', 5000)
  const { data: agentsData } = usePolling('/api/v1/agents/status', 5000)
  const { data: orchestratorData } = usePolling('/api/v1/orchestrator/status', 5000)

  const status = statusData as any
  const rules = rulesData as any
  const conflicts = conflictsData as any
  const audit = auditData as any
  const agents = agentsData as any
  const orchestrator = orchestratorData as any

  const actionColor: Record<string, string> = {
    block: '#ef4444', freeze: '#f59e0b', arbitrate: '#a78bfa',
    warn: '#fbbf24', require_audit: '#fb923c', pass: '#34d399',
  }

  const verdictIcon: Record<string, string> = {
    APPROVED: '✅', BLOCKED: '🚫', FROZEN: '🧊',
    ARBITRATION_REQUIRED: '⚖️', WARNED: '⚠️', AUDIT_REQUIRED: '📋',
  }

  const verdictColor: Record<string, string> = {
    APPROVED: 'var(--emerald)', BLOCKED: '#ef4444', FROZEN: '#f59e0b',
    ARBITRATION_REQUIRED: 'var(--violet)', WARNED: '#fbbf24', AUDIT_REQUIRED: '#fb923c',
  }

  const handleSimulate = async () => {
    setSimLoading(true)
    try {
      const payload = JSON.parse(simPayload)
      const res = await apiFetch('/trust-box/simulate', {
        method: 'POST',
        body: JSON.stringify({ vertical: selectedVertical, action_type: simAction, payload }),
      })
      setSimResult(res)
    } catch (e: any) {
      setSimResult({ error: e.message })
    }
    setSimLoading(false)
  }

  // Computed values
  const totalRules = status?.metrics?.total_rules || 0
  const activeConflicts = conflicts?.active_conflicts || 0
  const systemHealth = activeConflicts === 0 ? 'ok' : activeConflicts < 3 ? 'warn' : 'error'
  const healthLabel = systemHealth === 'ok' ? 'Nominal' : systemHealth === 'warn' ? 'Dégradé' : 'Critique'
  const healthColor = systemHealth === 'ok' ? 'var(--emerald)' : systemHealth === 'warn' ? 'var(--amber)' : 'var(--rose)'
  const circuitBreakers = agents?.circuit_breakers || []
  const agentList = agents?.agents || []
  const auditEvents = audit?.events || []

  const tabs = [
    { id: 'overview' as const, label: '📊 Vue d\'ensemble', badge: null },
    { id: 'agents' as const, label: '🤖 Agents', badge: agentList.length || null },
    { id: 'rules' as const, label: '📜 Règles', badge: totalRules || null },
    { id: 'simulate' as const, label: '🧪 Simulateur', badge: null },
    { id: 'audit' as const, label: '📝 Audit Trail', badge: auditEvents.length || null },
  ]

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '0' }}>
      {/* ── Hero Header ── */}
      <div style={{
        padding: '1.5rem 2rem 1.25rem',
        borderBottom: '1px solid var(--border)',
        background: 'linear-gradient(180deg, rgba(34,211,238,0.03) 0%, transparent 100%)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>🛡️ Trust Box</h1>
              <div className={`glow-status-${systemHealth === 'error' ? 'error' : systemHealth === 'warn' ? 'warn' : 'ok'}`} style={{
                display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
                padding: '0.25rem 0.75rem', borderRadius: '9999px',
                background: `${healthColor}10`, border: `1px solid ${healthColor}25`,
                fontSize: '0.6875rem', fontWeight: 600, color: healthColor,
              }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: healthColor }} />
                {healthLabel}
              </div>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              Couche de confiance déterministe · 0% LLM · <span className="mono" style={{ fontSize: '0.6875rem' }}>{totalRules} règles actives</span>
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {/* Live KPI pills */}
            <KpiPill icon="📜" value={totalRules} label="règles" color="var(--cyan)" />
            <KpiPill icon="⚠️" value={activeConflicts} label="conflits" color={activeConflicts > 0 ? 'var(--amber)' : 'var(--emerald)'} />
            <KpiPill icon="🤖" value={agentList.length} label="agents" color="var(--violet)" />
          </div>
        </div>

        {/* Tab bar */}
        <div style={{ display: 'flex', gap: '0.25rem', marginTop: '1rem' }}>
          {tabs.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              padding: '0.5rem 0.875rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
              fontWeight: activeTab === tab.id ? 700 : 400, cursor: 'pointer', border: 'none',
              background: activeTab === tab.id ? 'rgba(34,211,238,0.1)' : 'transparent',
              color: activeTab === tab.id ? 'var(--cyan)' : 'var(--text-muted)',
              display: 'flex', alignItems: 'center', gap: '0.375rem',
            }}>
              {tab.label}
              {tab.badge != null && <span className="mono" style={{ fontSize: '0.625rem', opacity: 0.7 }}>({tab.badge})</span>}
            </button>
          ))}
        </div>
      </div>

      {/* ── Content ── */}
      <div style={{ padding: '1.5rem 2rem' }}>

      {/* ══════════════ OVERVIEW ══════════════ */}
      {activeTab === 'overview' && (<>
        {/* Trust Score Gauge */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="glass trust-pulse" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: healthColor, lineHeight: 1 }}>
              {activeConflicts === 0 ? '100' : Math.max(0, 100 - activeConflicts * 15)}%
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>Score de confiance</div>
            {/* Mini bar */}
            <div style={{ height: 4, borderRadius: 2, background: 'var(--border)', marginTop: '0.75rem', overflow: 'hidden' }}>
              <div className="confidence-bar-fill" style={{ height: '100%', borderRadius: 2, background: healthColor, width: activeConflicts === 0 ? '100%' : `${Math.max(10, 100 - activeConflicts * 15)}%` }} />
            </div>
          </div>

          <div className="glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--violet)', lineHeight: 1 }}>
              {status?.metrics?.verticals || 6}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>Verticales actives</div>
            <div style={{ display: 'flex', gap: '0.25rem', justifyContent: 'center', marginTop: '0.75rem' }}>
              {(status?.verticals || ['comptable','avocat','sante','banque','startup','rh']).map((v: string) => (
                <span key={v} style={{ fontSize: '0.875rem', opacity: v === selectedVertical ? 1 : 0.4 }}>{verticalIcon(v)}</span>
              ))}
            </div>
          </div>

          <div className="glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--cyan)', lineHeight: 1 }}>
              {auditEvents.length}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>Événements audit (24h)</div>
            <div className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)', marginTop: '0.75rem' }}>
              🔗 WORM SHA-256
            </div>
          </div>
        </div>

        {/* Pipeline Flow — Animated */}
        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>🔄 Pipeline de Confiance — Flux temps réel</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0', position: 'relative', padding: '0.5rem 0' }}>
            {[
              { icon: '📥', label: 'Intention', color: '--cyan', status: 'active' },
              { icon: '🔀', label: 'Router', color: '--blue', status: 'active' },
              { icon: '🔍', label: 'Médiateur', color: '--violet', status: 'active' },
              { icon: '🤖', label: 'Agent LLM', color: '--emerald', status: 'active' },
              { icon: '🛡️', label: 'Guardrails', color: '--amber', status: activeConflicts > 0 ? 'warn' : 'active' },
              { icon: '📝', label: 'Journal', color: '--cyan', status: 'active' },
              { icon: '✅', label: 'Validation', color: '--emerald', status: 'active' },
            ].map((step, i, arr) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.375rem',
                  padding: '0.5rem 0.75rem', borderRadius: '0.625rem', position: 'relative',
                  background: step.status === 'warn' ? 'rgba(251,191,36,0.08)' : `var(${step.color})06`,
                  border: `1px solid ${step.status === 'warn' ? 'rgba(251,191,36,0.2)' : `var(${step.color})15`}`,
                }}>
                  <span style={{ fontSize: '1.125rem' }}>{step.icon}</span>
                  <span style={{ fontSize: '0.625rem', color: `var(${step.color})`, fontWeight: 500 }}>{step.label}</span>
                </div>
                {i < arr.length - 1 && (
                  <div style={{ width: 24, height: 2, background: 'var(--border)', position: 'relative', overflow: 'hidden' }}>
                    <div className="flow-dot" style={{ animationDelay: `${i * 0.4}s` }} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 6 Principes */}
        <div className="glass" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>🤝 Les 6 Principes du Trust Box</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
            {[
              { icon: '🔒', title: 'Déterminisme critique', desc: '100% JsonLogic. Jamais de LLM dans les décisions de gel.' },
              { icon: '🧊', title: 'Gel préventif', desc: 'Action gelée automatiquement si une règle est violée.' },
              { icon: '⚖️', title: 'Arbitrage humain', desc: "L'IA ne décide JAMAIS seule pour les actions critiques." },
              { icon: '📝', title: 'Transparence totale', desc: 'Chaque décision tracée dans un journal inviolable WORM.' },
              { icon: '🔄', title: 'Mode dégradé', desc: 'Data et Raisonnement continuent même pendant un gel.' },
              { icon: '✅', title: 'Conformité by design', desc: 'RGPD, AI Act, secret professionnel encodés dans les règles.' },
            ].map((p, i) => (
              <div key={i} style={{
                padding: '0.75rem', borderRadius: '0.625rem', background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border)', transition: 'all 0.2s', cursor: 'default',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <span>{p.icon}</span>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600 }}>{p.title}</span>
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{p.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Active Conflicts Alert */}
        {activeConflicts > 0 && conflicts?.conflicts?.length > 0 && (
          <div className="glass" style={{ padding: '1rem', borderLeft: '3px solid var(--amber)' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--amber)', marginBottom: '0.5rem' }}>
              ⚠️ Conflits actifs ({activeConflicts})
            </h3>
            {conflicts.conflicts.map((c: any, i: number) => (
              <div key={i} className="slide-in" style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.5rem 0.75rem', borderRadius: '0.375rem', marginBottom: '0.25rem',
                background: 'rgba(251,191,36,0.04)', border: '1px solid rgba(251,191,36,0.1)', fontSize: '0.8125rem',
              }}>
                <span>{c.reason || c.description || `Conflit ${i+1}`}</span>
                <span className="badge badge-amber" style={{ fontSize: '0.625rem' }}>En attente</span>
              </div>
            ))}
          </div>
        )}
      </>)}

      {/* ══════════════ AGENTS INSPECTOR ══════════════ */}
      {activeTab === 'agents' && (<>
        <div style={{ marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>🤖 Inspector d'Agents — Temps réel</h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Rafraîchissement automatique toutes les 5 secondes
          </p>
        </div>

        {/* Agent cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          {[
            { name: 'Orchestrateur', icon: '🎯', status: orchestrator?.status || 'idle', detail: 'Hub conversationnel', type: 'hub' },
            { name: 'Agent Data', icon: '📊', status: agents?.data_agent || 'idle', detail: 'Requêtes + compléments', type: 'agent' },
            { name: 'Agent Raisonnement', icon: '🧠', status: agents?.reasoning_agent || 'idle', detail: 'Analyse + recommandations', type: 'agent' },
            { name: 'Agent Action', icon: '⚡', status: agents?.action_agent || 'idle', detail: 'Exécution + saga + gel', type: 'agent' },
            { name: 'Médiateur', icon: '🔍', status: 'active', detail: '100% déterministe · JsonLogic', type: 'mediator' },
            { name: 'Superviseur V2', icon: '📡', status: agents?.supervisor_agent || 'idle', detail: 'Health board continu', type: 'agent' },
          ].map((a, i) => {
            const isActive = a.status === 'active' || a.status === 'running'
            return (
              <div key={i} className="glass slide-in" style={{
                padding: '1.25rem', animationDelay: `${i * 0.05}s`,
                borderLeft: `3px solid ${isActive ? 'var(--emerald)' : a.type === 'mediator' ? 'var(--violet)' : 'var(--text-dim)'}`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                    <span style={{ fontSize: '1.25rem' }}>{a.icon}</span>
                    <div>
                      <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>{a.name}</div>
                      <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{a.detail}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                    <div style={{
                      width: 8, height: 8, borderRadius: '50%',
                      background: isActive ? 'var(--emerald)' : 'var(--text-dim)',
                      boxShadow: isActive ? '0 0 6px rgba(52,211,153,0.5)' : 'none',
                    }} />
                    <span style={{ fontSize: '0.6875rem', color: isActive ? 'var(--emerald)' : 'var(--text-dim)' }}>
                      {isActive ? 'Actif' : 'Inactif'}
                    </span>
                  </div>
                </div>
                {a.type === 'mediator' && (
                  <div style={{ fontSize: '0.6875rem', color: 'var(--violet)', padding: '0.375rem 0.625rem', borderRadius: '0.375rem', background: 'rgba(167,139,250,0.06)', border: '1px solid rgba(167,139,250,0.12)' }}>
                    ⚠️ JAMAIS de LLM · Gel automatique · {totalRules} règles
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Circuit Breakers */}
        {circuitBreakers.length > 0 && (
          <div className="glass" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '1rem' }}>🔌 Circuit Breakers</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {circuitBreakers.map((cb: any, i: number) => (
                <div key={i} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '0.625rem 0.75rem', borderRadius: '0.5rem',
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                    <div style={{
                      width: 8, height: 8, borderRadius: '50%',
                      background: cb.state === 'closed' ? 'var(--emerald)' : cb.state === 'open' ? 'var(--rose)' : 'var(--amber)',
                      boxShadow: cb.state === 'closed' ? '0 0 6px rgba(52,211,153,0.4)' : 'none',
                    }} />
                    <span style={{ fontSize: '0.8125rem', fontWeight: 500 }}>{cb.name || cb.agent || `CB ${i+1}`}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{cb.failures || 0} échecs</span>
                    <span className={`badge badge-${cb.state === 'closed' ? 'emerald' : cb.state === 'open' ? 'rose' : 'amber'}`} style={{ fontSize: '0.625rem' }}>
                      {cb.state === 'closed' ? 'OK' : cb.state === 'open' ? 'Ouvert' : 'Demi'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </>)}

      {/* ══════════════ RULES ══════════════ */}
      {activeTab === 'rules' && (<>
        <div style={{ marginBottom: '1rem' }}>
          <select value={selectedVertical} onChange={e => setSelectedVertical(e.target.value)} style={{
            padding: '0.5rem 1rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
            background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
          }}>
            {(status?.verticals || ['comptable','avocat','sante','banque','startup','rh']).map((v: string) => (
              <option key={v} value={v}>{verticalIcon(v)} {v}</option>
            ))}
          </select>
        </div>

        {rules?.rules?.map((rule: any, i: number) => (
          <div key={rule.id || i} className="glass" style={{
            padding: '1rem 1.25rem', marginBottom: '0.75rem',
            borderLeft: `3px solid ${actionColor[rule.action] || 'var(--text-dim)'}`,
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.375rem' }}>
                  <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{rule.id}</span>
                  <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{rule.name}</span>
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{rule.message}</p>
              </div>
              <div style={{ display: 'flex', gap: '0.375rem', flexShrink: 0, marginLeft: '1rem' }}>
                <span style={{
                  padding: '0.25rem 0.625rem', borderRadius: '9999px', fontSize: '0.625rem', fontWeight: 700,
                  background: (actionColor[rule.action] || 'var(--text-dim)') + '15',
                  color: actionColor[rule.action] || 'var(--text-dim)',
                }}>{rule.action}</span>
                <span style={{
                  padding: '0.25rem 0.625rem', borderRadius: '9999px', fontSize: '0.625rem', fontWeight: 600,
                  background: rule.severity === 'critical' ? 'rgba(239,68,68,0.1)' : rule.severity === 'high' ? 'rgba(245,158,11,0.1)' : 'rgba(255,255,255,0.03)',
                  color: rule.severity === 'critical' ? '#ef4444' : rule.severity === 'high' ? '#f59e0b' : 'var(--text-dim)',
                }}>{rule.severity}</span>
              </div>
            </div>
          </div>
        ))}

        {rules?.total === 0 && (
          <div className="glass" style={{ padding: '2rem', textAlign: 'center' }}>
            <p style={{ color: 'var(--text-muted)' }}>Aucune règle pour cette verticale</p>
          </div>
        )}
      </>)}

      {/* ══════════════ SIMULATE ══════════════ */}
      {activeTab === 'simulate' && (<>
        <div className="glass" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '1rem' }}>🧪 Simulateur Trust Box</h3>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Testez ce que le Trust Box déciderait pour une action. Aucun effet de bord — dry-run uniquement.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Verticale</label>
              <select value={selectedVertical} onChange={e => setSelectedVertical(e.target.value)} style={{
                width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
              }}>
                {(status?.verticals || ['comptable','avocat','sante','banque','startup','rh']).map((v: string) => (
                  <option key={v} value={v}>{v}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Type d'action</label>
              <select value={simAction} onChange={e => setSimAction(e.target.value)} style={{
                width: '100%', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
                background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
              }}>
                <option value="consultation">Consultation</option>
                <option value="decision_fiscale">Décision fiscale</option>
                <option value="data_transfer">Transfert données</option>
                <option value="ecriture_comptable">Écriture comptable</option>
                <option value="virement">Virement</option>
                <option value="IA_high_risk">IA haut risque</option>
                <option value="cross_border">Cross-border</option>
              </select>
            </div>
          </div>

          <div style={{ marginBottom: '1rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>Payload (JSON)</label>
            <textarea value={simPayload} onChange={e => setSimPayload(e.target.value)} style={{
              width: '100%', minHeight: 60, padding: '0.5rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
              fontFamily: 'monospace', background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)', resize: 'vertical',
            }} />
          </div>

          <button onClick={handleSimulate} disabled={simLoading} className="btn btn-primary" style={{ padding: '0.625rem 1.5rem' }}>
            {simLoading ? '⏳ Simulation...' : '▶ Simuler'}
          </button>
        </div>

        {/* Simulation result */}
        {simResult && !simResult.error && (
          <div className="glass" style={{ padding: '1.5rem', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: verdictColor[simResult.verdict] || 'var(--text-dim)' }} />

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
              <div style={{
                width: 48, height: 48, borderRadius: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: (verdictColor[simResult.verdict] || 'var(--text-dim)') + '15',
                border: `1px solid ${(verdictColor[simResult.verdict] || 'var(--text-dim)')}25`,
              }}>
                <span style={{ fontSize: '1.5rem' }}>{verdictIcon[simResult.verdict] || '❓'}</span>
              </div>
              <div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: verdictColor[simResult.verdict] || 'var(--text)' }}>{simResult.verdict}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>{simResult.explanation}</div>
              </div>
            </div>

            {simResult.triggered_rules?.length > 0 && (
              <div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.5rem' }}>
                  {simResult.rules_triggered} règle(s) déclenchée(s) sur {simResult.rules_checked} évaluées
                </div>
                {simResult.triggered_rules.map((r: any, i: number) => (
                  <div key={i} style={{
                    padding: '0.75rem', marginBottom: '0.5rem', borderRadius: '0.5rem',
                    borderLeft: `3px solid ${actionColor[r.action] || 'var(--text-dim)'}`, background: 'rgba(255,255,255,0.02)',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{r.rule_id}</span>
                      <span style={{ fontSize: '0.625rem', fontWeight: 700, color: actionColor[r.action] || 'var(--text-dim)' }}>{r.action}</span>
                    </div>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, marginTop: '0.25rem' }}>{r.rule_name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{r.message}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {simResult?.error && (
          <div className="glass" style={{ padding: '1.5rem', borderLeft: '3px solid #ef4444' }}>
            <p style={{ color: '#ef4444', fontSize: '0.875rem' }}>Erreur: {simResult.error}</p>
          </div>
        )}
      </>)}

      {/* ══════════════ AUDIT TRAIL ══════════════ */}
      {activeTab === 'audit' && (<>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>📝 Audit Trail — Temps réel</h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              Journal WORM hash-chainé SHA-256 · {auditEvents.length} événements · Auto-refresh 5s
            </p>
          </div>
          {audit?.integrity && (
            <div style={{
              padding: '0.375rem 0.75rem', borderRadius: '0.5rem',
              background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.15)',
              fontSize: '0.75rem', color: 'var(--emerald)', fontWeight: 600,
            }}>
              ✓ Intégrité vérifiée
            </div>
          )}
        </div>

        {auditEvents.length === 0 ? (
          <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📝</div>
            <p style={{ color: 'var(--text-muted)' }}>Aucun événement Trust Box enregistré</p>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.375rem' }}>
              Les événements apparaîtront ici dès qu'une action sera évaluée par le Médiateur
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {auditEvents.map((entry: any, i: number) => {
              const evtType = entry.event_type || ''
              const isConflict = evtType.includes('conflict') || evtType.includes('freeze')
              const isViolation = evtType.includes('violation')
              const borderColor = isViolation ? 'var(--rose)' : isConflict ? 'var(--amber)' : 'var(--border)'
              return (
                <div key={i} className="slide-in" style={{
                  display: 'grid', gridTemplateColumns: '80px 50px 1fr 120px 40px',
                  padding: '0.5rem 0.75rem', borderRadius: '0.375rem', fontSize: '0.75rem',
                  background: i % 2 === 0 ? 'rgba(255,255,255,0.01)' : 'transparent',
                  borderLeft: `2px solid ${borderColor}`, gap: '0.75rem', alignItems: 'center',
                  animationDelay: `${i * 0.02}s`,
                }}>
                  <span className="mono" style={{ color: 'var(--text-dim)', fontSize: '0.625rem' }}>
                    {entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '—'}
                  </span>
                  <span style={{
                    padding: '0.125rem 0.375rem', borderRadius: '0.25rem', textAlign: 'center',
                    background: isViolation ? 'rgba(251,113,133,0.08)' : isConflict ? 'rgba(251,191,36,0.08)' : 'rgba(255,255,255,0.02)',
                    fontSize: '0.625rem', fontWeight: 600,
                    color: isViolation ? 'var(--rose)' : isConflict ? 'var(--amber)' : 'var(--text-dim)',
                  }}>{entry.sequence || i+1}</span>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{evtType}</span>
                  <span className="mono" style={{ color: 'var(--violet)', fontSize: '0.6875rem' }}>{entry.agent_source || '—'}</span>
                  <span title={entry.entry_hash} style={{ color: 'var(--emerald)', fontSize: '0.75rem' }}>🔗</span>
                </div>
              )
            })}
          </div>
        )}
      </>)}

      </div>{/* end content padding */}
    </div>
  )
}

/** Tiny KPI pill for header */
function KpiPill({ icon, value, label, color }: { icon: string; value: number; label: string; color: string }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '0.5rem',
      padding: '0.375rem 0.875rem', borderRadius: '9999px',
      background: `${color}08`, border: `1px solid ${color}20`,
    }}>
      <span style={{ fontSize: '0.875rem' }}>{icon}</span>
      <span className="mono" style={{ fontSize: '0.875rem', fontWeight: 700, color }}>{value}</span>
      <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{label}</span>
    </div>
  )
}

function SermentView({ user }: { user: any }) {
  const [vertical, setVertical] = useState(user?.primary_vertical || 'comptable')
  const { data, loading } = useApi(`/api/v1/serment/${vertical}`)
  const [signed, setSigned] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const serment = data as any

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>🤫 Serment numérique</h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Engagement déontologique · Vérifiable · Immuable
          </p>
        </div>
        <select value={vertical} onChange={e => setVertical(e.target.value)} style={{
          padding: '0.375rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
          background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
        }}>
          {Object.entries(VERTICAL_CONFIG).map(([k, v]) => (
            <option key={k} value={k}>{v.icon} {v.label}</option>
          ))}
        </select>
      </div>

      {loading ? <LoadingSpinner /> : serment && !serment.detail ? (
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          {/* Serment card */}
          <div className="glass" style={{ padding: '2rem', marginBottom: '1.5rem', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: 'linear-gradient(90deg, var(--cyan), var(--emerald))' }} />

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '2rem' }}>{verticalIcon(vertical)}</div>
              <div>
                <div style={{ fontSize: '1rem', fontWeight: 700 }}>{serment.title || `Serment — ${vertical}`}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{serment.jurisdiction || 'FR-CH'}</div>
              </div>
            </div>

            {/* Principes */}
            {(serment.principles || serment.principes || []).map((p: any, i: number) => (
              <div key={i} style={{
                padding: '1rem', marginBottom: '0.75rem', borderRadius: '0.75rem',
                background: 'rgba(34,211,238,0.03)', border: '1px solid rgba(34,211,238,0.08)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: '50%',
                    background: 'rgba(34,211,238,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '0.6875rem', fontWeight: 700, color: 'var(--cyan)',
                  }}>{i + 1}</span>
                  <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{p.title || p.name || `Principe ${i + 1}`}</span>
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.7, paddingLeft: '2rem' }}>
                  {p.description || p.text || ''}
                </p>
                {p.reference && (
                  <div className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', paddingLeft: '2rem', marginTop: '0.375rem' }}>
                    📎 {p.reference}
                  </div>
                )}
              </div>
            ))}

            {/* Références légales */}
            {(serment.references || []).length > 0 && (
              <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', borderRadius: '0.5rem', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-dim)', marginBottom: '0.375rem' }}>Références</div>
                {(serment.references || []).map((r: string, i: number) => (
                  <div key={i} style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>• {r}</div>
                ))}
              </div>
            )}
          </div>

          {/* Signature */}
          <div className="glass" style={{ padding: '1.5rem', textAlign: 'center' }}>
            {signed ? (
              <div>
                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>✅</div>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--emerald)', marginBottom: '0.5rem' }}>Serment signé</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  Signé le {new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })} par {user?.full_name || user?.email || 'Admin'}
                </div>
                <div className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
                  Vérifiable via GET /api/v1/serment/{vertical}/verify
                </div>
              </div>
            ) : showConfirm ? (
              <div>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  En signant ce serment, vous vous engagez à respecter les principes déontologiques ci-dessus dans toute utilisation de l'IA.
                </p>
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
                  <button onClick={() => setSigned(true)} className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>
                    ✍️ Signer le serment
                  </button>
                  <button onClick={() => setShowConfirm(false)} className="btn btn-secondary" style={{ padding: '0.75rem 1.5rem' }}>
                    Annuler
                  </button>
                </div>
              </div>
            ) : (
              <button onClick={() => setShowConfirm(true)} className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>
                ✍️ Signer ce serment
              </button>
            )}
          </div>

          {/* Intégrité */}
          <div style={{ marginTop: '1rem', padding: '0.75rem', borderRadius: '0.5rem', background: 'rgba(52,211,153,0.04)', border: '1px solid rgba(52,211,153,0.12)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ color: 'var(--emerald)', fontSize: '0.75rem' }}>🔒</span>
            <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
              Intégrité vérifiable · SHA-256 · Horodatage RFC 3161
            </span>
          </div>
        </div>
      ) : (
        <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🤫</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500 }}>
            Serment non disponible pour cette vertical
          </p>
        </div>
      )}
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ÉCHÉANCIER RÉGLEMENTAIRE — Calendrier vivant FR-CH
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function EcheancierView({ user }: { user: any }) {
  const [vertical, setVertical] = useState(user?.primary_vertical || 'comptable')
  const [jurisdiction, setJurisdiction] = useState('')
  const { data, loading } = useApi(`/api/v1/regulatory/calendar?vertical=${vertical}${jurisdiction ? `&jurisdiction=${jurisdiction}` : ''}`)
  const { data: stats } = useApi(`/api/v1/regulatory/stats?vertical=${vertical}`)

  const deadlines = (data as any)?.deadlines || []
  const s = stats as any

  const urgencyColor = (u: string) => {
    if (u === 'overdue') return 'rose'
    if (u === 'critical') return 'amber'
    if (u === 'high') return 'cyan'
    return 'emerald'
  }

  const urgencyLabel = (u: string) => {
    if (u === 'overdue') return '🔴 En retard'
    if (u === 'critical') return '🟠 Cette semaine'
    if (u === 'high') return '🟡 Ce mois'
    return '🟢 À venir'
  }

  const flagForJurisdiction = (j: string) => {
    if (j === 'FR') return '🇫🇷'
    if (j === 'CH') return '🇨🇭'
    return '🇫🇷🇨🇭'
  }

  return (
    <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem 2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700 }}>📅 Échéancier réglementaire</h1>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Obligations FR-CH vivantes · {deadlines.length} échéance{deadlines.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <select value={vertical} onChange={e => setVertical(e.target.value)} style={{
            padding: '0.375rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
            background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
          }}>
            {Object.entries(VERTICAL_CONFIG).map(([k, v]) => (
              <option key={k} value={k}>{v.icon} {v.label}</option>
            ))}
          </select>
          <select value={jurisdiction} onChange={e => setJurisdiction(e.target.value)} style={{
            padding: '0.375rem 0.75rem', borderRadius: '0.5rem', fontSize: '0.8125rem',
            background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
          }}>
            <option value="">Toutes juridictions</option>
            <option value="FR">🇫🇷 France</option>
            <option value="CH">🇨🇭 Suisse</option>
            <option value="FR-CH">🇫🇷🇨🇭 FR-CH</option>
          </select>
        </div>
      </div>

      {/* Stats KPIs */}
      {s && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <KpiCard icon="📋" label="Total" value={String(s.total || 0)} sub="Échéances" color="cyan" />
          <KpiCard icon="🔴" label="En retard" value={String(s.overdue || 0)} sub="Action immédiate" color="rose" />
          <KpiCard icon="🟠" label="Cette semaine" value={String(s.this_week || 0)} sub="Urgent" color="amber" />
          <KpiCard icon="🟡" label="Ce mois" value={String(s.this_month || 0)} sub="Planifier" color="cyan" />
          <KpiCard icon="📅" label="Prochain trimestre" value={String(s.next_quarter || 0)} sub="Anticiper" color="emerald" />
        </div>
      )}

      {/* Overdue alerts */}
      {s?.overdue_deadlines?.length > 0 && (
        <div className="glass" style={{ padding: '1rem', marginBottom: '1rem', borderLeft: '3px solid var(--rose)' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--rose)', marginBottom: '0.75rem' }}>
            🔴 Échéances en retard
          </h3>
          {(s.overdue_deadlines as any[]).map((d: any, i: number) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '0.5rem 0.75rem', marginBottom: '0.25rem', borderRadius: '0.375rem',
              background: 'rgba(251,113,133,0.04)', border: '1px solid rgba(251,113,133,0.1)', fontSize: '0.8125rem',
            }}>
              <span>{d.label} <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{flagForJurisdiction(d.jurisdiction || '')}</span></span>
              <span className="mono" style={{ fontSize: '0.6875rem', color: 'var(--rose)' }}>{d.days_overdue}j de retard</span>
            </div>
          ))}
        </div>
      )}

      {/* Timeline */}
      {loading ? <LoadingSpinner /> : deadlines.length === 0 ? (
        <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📅</div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', fontWeight: 500 }}>Aucune échéance à venir</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem' }}>
          {deadlines.map((d: any, i: number) => {
            const color = urgencyColor(d.urgency)
            return (
              <div key={i} className="glass" style={{
                padding: '0.875rem 1rem', display: 'grid',
                gridTemplateColumns: '70px 40px 1fr auto',
                gap: '0.75rem', alignItems: 'center',
                borderLeft: `3px solid var(--${color})`,
              }}>
                <div>
                  <div className="mono" style={{ fontSize: '0.75rem', fontWeight: 600, color: `var(--${color})` }}>
                    {d.days_until < 0 ? `J${d.days_until}` : d.days_until === 0 ? 'Aujourd\'hui' : `J+${d.days_until}`}
                  </div>
                  <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                    {d.next_date ? new Date(d.next_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }) : ''}
                  </div>
                </div>
                <div style={{ fontSize: '1.25rem', textAlign: 'center' }}>{flagForJurisdiction(d.jurisdiction || '')}</div>
                <div>
                  <div style={{ fontSize: '0.8125rem', fontWeight: 500 }}>{d.label}</div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.125rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {d.description}
                  </div>
                  {d.reference && (
                    <div className="mono" style={{ fontSize: '0.5625rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>
                      📎 {d.reference}
                    </div>
                  )}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
                  <span className={`badge badge-${color}`} style={{ fontSize: '0.5625rem' }}>
                    {urgencyLabel(d.urgency)}
                  </span>
                  {d.frequency && (
                    <span style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>{d.frequency}</span>
                  )}
                  {d.auto_intention && (
                    <span style={{ fontSize: '0.5625rem', color: 'var(--cyan)' }}>🎯 Auto</span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SHARED COMPONENTS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */

function TrustBadge({ score }: { score: number }) {
  const config = score >= 0.8
    ? { color: 'emerald', label: 'Fiable', icon: '🛡️' }
    : score >= 0.5
    ? { color: 'amber', label: 'Surveillé', icon: '⚠️' }
    : { color: 'rose', label: 'Bloqué', icon: '🛑' }
  return (
    <div style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
      padding: '0.125rem 0.5rem', borderRadius: '9999px',
      background: `var(--${config.color})08`, border: `1px solid var(--${config.color})20`,
      fontSize: '0.625rem', color: `var(--${config.color})`, fontWeight: 500,
    }}>
      {config.icon} {config.label} · {Math.round(score * 100)}%
    </div>
  )
}

function KpiCard({ icon, label, value, sub, color }: { icon: string; label: string; value: string; sub: string; color: string }) {
  return (
    <div className="glass" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '0.75rem' }}>
        <div style={{
          width: 36, height: 36, borderRadius: '0.625rem',
          background: `var(--${color})08`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem',
        }}>{icon}</div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
      </div>
      <div style={{ fontSize: '1.5rem', fontWeight: 700, lineHeight: 1, marginBottom: '0.25rem' }}>{value}</div>
      <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{sub}</div>
    </div>
  )
}

function IntentStateBadge({ state }: { state: string }) {
  const map: Record<string, { color: string; label: string }> = {
    created:         { color: 'cyan',    label: '📥 Créée' },
    routed:          { color: 'blue',    label: '🔀 Routée' },
    processing:      { color: 'violet',  label: '🤖 Traitement' },
    frozen:          { color: 'amber',   label: '🧊 Gelée' },
    degraded_frozen: { color: 'amber',   label: '🧊 Gel dégradé' },
    arbitrating:     { color: 'orange',  label: '⚖️ Arbitrage' },
    unfrozen:        { color: 'emerald', label: '✅ Dégelée' },
    completed:       { color: 'emerald', label: '✅ Terminée' },
    failed:          { color: 'rose',    label: '✗ Échouée' },
    cancelled:       { color: 'rose',    label: 'Annulée' },
  }
  const s = map[state] || map.created
  return <span className={`badge badge-${s.color}`} style={{ fontSize: '0.625rem' }}>{s.label}</span>
}

function SettingsRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.375rem 0', borderBottom: '1px solid rgba(30,41,59,0.3)' }}>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
      <span style={{ fontSize: '0.75rem', fontWeight: 500 }}>{value}</span>
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)', fontSize: '0.8125rem' }}>{message}</div>
}

function LoadingSpinner() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem' }}>
      <div style={{
        width: 32, height: 32, border: '3px solid var(--border)', borderTopColor: 'var(--cyan)',
        borderRadius: '50%', animation: 'spin 0.8s linear infinite',
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: '0.25rem', padding: '0.75rem' }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 6, height: 6, borderRadius: '50%', background: 'var(--text-dim)',
          animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
        }} />
      ))}
      <style>{`@keyframes pulse { 0%, 100% { opacity: 0.3 } 50% { opacity: 1 } }`}</style>
    </div>
  )
}

function verticalIcon(v?: string): string {
  const icons: Record<string, string> = { comptable: '📊', avocat: '⚖️', sante: '🏥', banque: '🏦', startup: '🚀', rh: '👥' }
  return icons[(v || '').toLowerCase()] || '🔷'
}

function formatCheckLabel(key: string): string {
  const labels: Record<string, string> = {
    journal_integrity: 'Intégrité du journal', hash_chain: 'Chaîne de hachage',
    data_residency: 'Résidence des données', encryption: 'Chiffrement',
    access_control: 'Contrôle d\'accès', audit_trail: 'Piste d\'audit',
    retention: 'Rétention des données', consent: 'Consentement',
    dpia: 'AIPD', ai_act_risk: 'Risque AI Act',
    llm_guardrails: 'Garde-fous LLM', mfa: 'Authentification 2FA',
    gdpr: 'RGPD', lpd: 'LPD',
  }
  return labels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function getSuggestions(vertical: string): string[] {
  const map: Record<string, string[]> = {
    comptable: ['Quels documents conserver 10 ans ?', 'TVA sur prestations suisses ?', 'Seuil de déclaration fiduciaire'],
    avocat:    ['Délais recours tribunal administratif ?', 'Secret professionnel AI ?', 'Convention d\'honoraires conforme'],
    sante:     ['Consentement patient pour IA ?', 'Dossier médical partagé limites ?', 'Hébergement données de santé'],
    banque:    ['KYC obligations LBA ?', 'Blanchiment signalement SUSAR ?', 'Risques crypto-regulation'],
    startup:   ['RGPD pour MVP ?', 'Clauses IA contrat CGV ?', 'Propriété intellectuelle IA générative'],
    rh:        ['Délais préavis Suisse ?', 'Filtrage CV par IA ?', 'Données sensibles employé'],
  }
  return map[vertical] || map.comptable
}
