import { useState } from 'react'

const VERTICALS = [
  { id: 'comptable', icon: '📊', label: 'Comptable', color: '#22d3ee' },
  { id: 'avocat',    icon: '⚖️',  label: 'Avocat',    color: '#a78bfa' },
  { id: 'sante',     icon: '🏥',  label: 'Santé',     color: '#34d399' },
  { id: 'banque',    icon: '🏦',  label: 'Banque',    color: '#fbbf24' },
  { id: 'startup',   icon: '🚀',  label: 'Startup',   color: '#fb923c' },
  { id: 'rh',        icon: '👥',  label: 'RH',        color: '#fb7185' },
]

const AGENTS = [
  { id: 'reasoning', icon: '🧠', label: 'Le Léman', type: 'LLM', persona: true },
  { id: 'data',      icon: '📊', label: 'Data',         type: 'LLM' },
  { id: 'orchestrator', icon: '🎯', label: 'Orchestrateur', type: 'LLM' },
]

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  agent?: string
  model?: string
}

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [vertical, setVertical] = useState('comptable')
  const [agent, setAgent] = useState('reasoning')
  const [sending, setSending] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || sending) return
    const msg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg, timestamp: new Date() }])
    setSending(true)

    try {
      const { chat } = await import('../lib/api')
      const res = await chat.send(msg, vertical, agent)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.response || res.error || 'Pas de réponse',
        timestamp: new Date(),
        agent: res.agent,
        model: res.model,
      }])
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Erreur: ${e.message}`,
        timestamp: new Date(),
      }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Toolbar */}
      <div style={{ display: 'flex', gap: '0.75rem', padding: '0.75rem 1rem', borderBottom: '1px solid var(--border)', alignItems: 'center', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 600 }}>VERTICAL</span>
        <div style={{ display: 'flex', gap: '0.375rem' }}>
          {VERTICALS.map(v => (
            <button key={v.id} onClick={() => setVertical(v.id)} style={{
              padding: '0.25rem 0.625rem', borderRadius: '0.375rem', border: `1px solid ${vertical === v.id ? v.color + '60' : 'var(--border)'}`,
              background: vertical === v.id ? v.color + '15' : 'transparent', color: vertical === v.id ? v.color : 'var(--text-muted)',
              fontSize: '0.6875rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem',
            }}>
              {v.icon} {v.label}
            </button>
          ))}
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 600, marginLeft: '1rem' }}>AGENT</span>
        <div style={{ display: 'flex', gap: '0.375rem' }}>
          {AGENTS.map(a => (
            <button key={a.id} onClick={() => setAgent(a.id)} style={{
              padding: '0.25rem 0.625rem', borderRadius: '0.375rem', border: `1px solid ${agent === a.id ? 'var(--cyan)' + '60' : 'var(--border)'}`,
              background: agent === a.id ? 'rgba(34,211,238,0.1)' : 'transparent', color: agent === a.id ? 'var(--cyan)' : 'var(--text-muted)',
              fontSize: '0.6875rem', fontWeight: 600, cursor: 'pointer',
            }}>
              {a.icon} {a.label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', paddingTop: '3rem', color: 'var(--text-dim)' }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🌊</div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--cyan)' }}>Le Léman</div>
            <div style={{ fontSize: '0.75rem', marginTop: '0.25rem', fontWeight: 500 }}>Conseil de confiance franco-suisse</div>
            <div style={{ fontSize: '0.6875rem', marginTop: '0.5rem', maxWidth: '360px', margin: '0.5rem auto 0' }}>
              Posez votre question — les agents analysent, le Trust Box vérifie, et je vous recommande avec transparence.
            </div>
          </div>
        )}}
        {messages.map((m, i) => (
          <div key={i} style={{
            marginBottom: '0.75rem', display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              maxWidth: '70%', padding: '0.75rem 1rem', borderRadius: '0.75rem',
              background: m.role === 'user' ? 'rgba(34,211,238,0.1)' : 'var(--bg-card-solid)',
              border: `1px solid ${m.role === 'user' ? 'rgba(34,211,238,0.2)' : 'var(--border)'}`,
            }}>
              {m.role === 'assistant' && m.model && (
                <div style={{ fontSize: '0.625rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>
                  {m.agent} · {m.model}
                </div>
              )}
              <div style={{ fontSize: '0.8125rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{m.content}</div>
              <div style={{ fontSize: '0.5625rem', color: 'var(--text-dim)', marginTop: '0.375rem', textAlign: 'right' }}>
                {m.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        {sending && (
          <div style={{ color: 'var(--cyan)', fontSize: '0.75rem', padding: '0.5rem' }}>
            ● ● ● Analyse en cours...
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.5rem' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Posez votre question à Le Léman..."
          style={{
            flex: 1, padding: '0.625rem 1rem', borderRadius: '0.5rem',
            background: 'var(--bg-card-solid)', border: '1px solid var(--border)',
            color: 'var(--text)', fontSize: '0.8125rem', outline: 'none',
          }}
        />
        <button onClick={handleSend} disabled={sending || !input.trim()} style={{
          padding: '0.625rem 1.25rem', borderRadius: '0.5rem',
          background: sending ? 'var(--text-dim)' : 'var(--cyan)', color: 'var(--bg)',
          fontWeight: 600, fontSize: '0.8125rem', border: 'none', cursor: sending ? 'not-allowed' : 'pointer',
        }}>
          Envoyer
        </button>
      </div>
    </div>
  )
}
