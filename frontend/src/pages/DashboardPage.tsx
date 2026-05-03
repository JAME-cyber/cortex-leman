import { useState, useEffect, useRef } from 'react'
import { useApi, apiFetch } from '../hooks/useApi'

const NAV_ITEMS = [
  { id: 'dashboard',  icon: '📊', label: 'Tableau de bord' },
  { id: 'serment',    icon: '🤫', label: 'Serment numérique' },
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
        {displayedView === 'echeancier' && <EcheancierView user={user} />}
        {displayedView === 'chat'       && <ChatView user={user} />}
        {displayedView === 'intents'    && <IntentsView user={user} />}
        {displayedView === 'journal'    && <JournalView user={user} />}
        {displayedView === 'arbitrage'  && <ArbitrageView user={user} />}
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
  role: 'user' | 'assistant'
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
}

const VERTICAL_CONFIG: Record<string, { icon: string; label: string; color: string }> = {
  comptable: { icon: '📊', label: 'Comptable', color: '--cyan' },
  avocat:    { icon: '⚖️',  label: 'Avocat',    color: '--violet' },
  sante:     { icon: '🏥', label: 'Santé',     color: '--emerald' },
  banque:    { icon: '🏦', label: 'Banque',    color: '--amber' },
  startup:   { icon: '🚀', label: 'Startup',   color: '--orange' },
  rh:        { icon: '👥', label: 'RH',        color: '--rose' },
}

function ChatView({ user }: { user: any }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [vertical, setVertical] = useState(user?.primary_vertical || 'comptable')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg: ChatMessage = { role: 'user', content: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await apiFetch(`/api/v1/chat?message=${encodeURIComponent(input)}&vertical=${vertical}&client_id=demo`, {
        method: 'POST',
      })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.response || res.content || res.message || 'Aucune réponse',
        timestamp: new Date(),
        agent: res.agent || 'reasoning',
        model: res.model,
        tokens: res.tokens,
        provider: res.provider,
        trustScore: res.trust_score ?? 1.0,
        guardrailFlags: res.guardrail_flags || [],
        guardrailBlocked: res.guardrail_blocked || false,
        vertical: res.vertical || vertical,
      }])
    } catch (e: any) {
      const msg = typeof e?.message === 'string' ? e.message : JSON.stringify(e)
      setMessages(prev => [...prev, {
        role: 'assistant', content: `Erreur: ${msg}`, timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }

  const vc = VERTICAL_CONFIG[vertical] || VERTICAL_CONFIG.comptable

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <header style={{ padding: '0.75rem 1.5rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <h2 style={{ fontSize: '0.9375rem', fontWeight: 700 }}>💬 Chat Agent</h2>
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

      {/* Messages */}
      <div style={{ flex: 1, overflow: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {messages.length === 0 && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ fontSize: '3rem' }}>🤖</div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9375rem', fontWeight: 500 }}>
              Agent {vc.label}
            </p>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.8125rem', maxWidth: 400, textAlign: 'center' }}>
              Posez une question. Chaque réponse est analysée par le Médiateur et enregistrée dans le journal WORM.
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center', marginTop: '0.5rem' }}>
              {getSuggestions(vertical).map((s, i) => (
                <button key={i} onClick={() => { setInput(s); }} style={{
                  padding: '0.375rem 0.75rem', borderRadius: '9999px', fontSize: '0.75rem',
                  background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)',
                  color: 'var(--text-muted)', cursor: 'pointer',
                }}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{
            display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              maxWidth: '75%', padding: '0.875rem 1.125rem', borderRadius: '0.875rem',
              background: m.role === 'user' ? 'rgba(34,211,238,0.08)' : 'rgba(255,255,255,0.02)',
              border: m.role === 'user' ? '1px solid rgba(34,211,238,0.12)' : '1px solid var(--border)',
            }}>
              {m.guardrailBlocked && (
                <div style={{
                  marginBottom: '0.75rem', padding: '0.5rem 0.75rem', borderRadius: '0.5rem',
                  background: 'rgba(251,113,133,0.08)', border: '1px solid rgba(251,113,133,0.15)',
                  fontSize: '0.75rem', color: 'var(--rose)', display: 'flex', alignItems: 'center', gap: '0.5rem',
                }}>
                  🛑 Réponse bloquée par les garde-fous de sécurité
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
              <div style={{ fontSize: '0.8125rem', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{m.content}</div>
              {m.role === 'assistant' && (
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(30,41,59,0.4)',
                }}>
                  <div style={{ display: 'flex', gap: '0.625rem', alignItems: 'center' }}>
                    <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                      {m.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    {m.model && (
                      <span style={{ fontSize: '0.625rem', color: 'var(--violet)' }}>
                        {m.model.split('/').pop()}
                      </span>
                    )}
                    {m.tokens != null && (
                      <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                        {m.tokens} tokens
                      </span>
                    )}
                  </div>
                  {m.trustScore != null && <TrustBadge score={m.trustScore} />}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid var(--border)' }}>
        <div style={{
          display: 'flex', gap: '0.75rem', alignItems: 'center',
          background: 'var(--bg-card-solid)', border: '1px solid var(--border)',
          borderRadius: '0.75rem', padding: '0.25rem 0.25rem 0.25rem 1rem',
        }}>
          <input
            value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder={`Posez votre question ${vc.label}…`}
            style={{
              flex: 1, background: 'transparent', border: 'none', color: 'var(--text)',
              fontSize: '0.8125rem', outline: 'none', padding: '0.5rem 0',
            }}
          />
          <button onClick={sendMessage} disabled={loading || !input.trim()} style={{
            padding: '0.5rem 1.25rem', borderRadius: '0.5rem',
            background: loading || !input.trim() ? 'var(--bg)' : 'var(--cyan)',
            color: loading || !input.trim() ? 'var(--text-dim)' : 'var(--bg)',
            border: 'none', fontSize: '0.8125rem', fontWeight: 600, cursor: loading ? 'default' : 'pointer',
            transition: 'all 0.15s ease',
          }}>
            Envoyer
          </button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.375rem', padding: '0 0.25rem' }}>
          <span style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>
            Médiateur actif · Journal WORM · Garde-fous RGPD
          </span>
          <span className="mono" style={{ fontSize: '0.5625rem', color: 'var(--text-dim)' }}>
            Entrée pour envoyer
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

  const intentions = (data as any)?.intentions || []

  const createIntent = async () => {
    if (!newIntent.trim()) return
    setCreating(true)
    try {
      await apiFetch('/api/v1/intentions', {
        method: 'POST',
        body: JSON.stringify({
          client_id: clientId,
          vertical: user?.primary_vertical || 'comptable',
          description: newIntent,
          priority: 'normal',
        }),
      })
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

      {/* New intent */}
      <div className="glass" style={{ padding: '1rem', marginBottom: '1.5rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <input
          value={newIntent} onChange={e => setNewIntent(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && createIntent()}
          placeholder="Décrire une nouvelle intention…"
          style={{
            flex: 1, padding: '0.5rem 0.875rem', borderRadius: '0.5rem',
            background: 'var(--bg-card-solid)', border: '1px solid var(--border)', color: 'var(--text)',
            fontSize: '0.8125rem', outline: 'none',
          }}
        />
        <button onClick={createIntent} disabled={creating || !newIntent.trim()} className="btn btn-primary" style={{ fontSize: '0.8125rem', whiteSpace: 'nowrap' }}>
          {creating ? 'Création…' : '➕ Créer'}
        </button>
      </div>

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
