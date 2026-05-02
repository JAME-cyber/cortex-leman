import { useState, useEffect, useRef, useCallback } from 'react'

/* ═══════════════════════════════════════════════════════════
   CORTEX LEMAN V5 — Agent Flow Animation
   Interactive visualization of multi-agent communication
   via NATS JetStream bus in the Graphe de Confiance.
   ═══════════════════════════════════════════════════════════ */

// ── Types ──────────────────────────────────────────────────
interface AgentNode {
  id: string
  label: string
  icon: string
  color: string
  x: number
  y: number
  type: 'llm' | 'prog' | 'human'
}

interface Message {
  id: number
  from: string
  to: string
  subject: string
  color: string
  progress: number
  phase: number
}

interface LogEntry {
  id: number
  timestamp: string
  event: string
  agent: string
  detail: string
  type: 'info' | 'warn' | 'success' | 'freeze'
}

// ── Agent positions (hexagonal graph layout) ───────────────
const AGENTS: AgentNode[] = [
  { id: 'orchestrator', label: 'Orchestrateur', icon: '🎯', color: '#22d3ee', x: 50, y: 10, type: 'llm' },
  { id: 'data',         label: 'Data',          icon: '📡', color: '#60a5fa', x: 15, y: 38, type: 'llm' },
  { id: 'reasoning',    label: 'Raisonnement',   icon: '🧠', color: '#a78bfa', x: 85, y: 38, type: 'llm' },
  { id: 'mediator',     label: 'Médiateur',      icon: '🛡️', color: '#fbbf24', x: 50, y: 50, type: 'prog' },
  { id: 'action',       label: 'Action',         icon: '⚡', color: '#34d399', x: 25, y: 75, type: 'prog' },
  { id: 'supervisor',   label: 'Superviseur',    icon: '👁️', color: '#fb7185', x: 75, y: 75, type: 'prog' },
  { id: 'journal',      label: 'Journal WORM',   icon: '📝', color: '#94a3b8', x: 50, y: 92, type: 'prog' },
]

// ── Scenario: a realistic compliance workflow ──────────────
const SCENARIO_PHASES = [
  // Phase 0: User sends intention
  {
    messages: [
      { from: 'orchestrator', to: 'mediator', subject: 'cleman.intention.new', color: '#22d3ee' },
    ],
    logs: [
      { event: 'Intention reçue', agent: 'Orchestrateur', detail: '"Vérifier conformité TVA client Dupont"', type: 'info' as const },
    ],
    highlight: ['orchestrator'],
  },
  // Phase 1: Mediator checks rules
  {
    messages: [
      { from: 'mediator', to: 'data', subject: 'cleman.data.query', color: '#fbbf24' },
    ],
    logs: [
      { event: 'Règle comptable.seuil_tva vérifiée', agent: 'Médiateur', detail: 'JsonLogic: PASSED ✓', type: 'success' as const },
      { event: 'Requête data envoyée', agent: 'Médiateur', detail: 'Recherche TVA + seuils AFC', type: 'info' as const },
    ],
    highlight: ['mediator'],
  },
  // Phase 2: Data agent responds
  {
    messages: [
      { from: 'data', to: 'reasoning', subject: 'cleman.agent.result', color: '#60a5fa' },
      { from: 'data', to: 'supervisor', subject: 'cleman.agent.result', color: '#60a5fa' },
    ],
    logs: [
      { event: 'Résultat data', agent: 'Data', detail: 'Score confiance: 0.87 — 3 sources trouvées', type: 'success' as const },
    ],
    highlight: ['data'],
  },
  // Phase 3: Reasoning analyzes
  {
    messages: [
      { from: 'reasoning', to: 'mediator', subject: 'cleman.reasoning.analyze', color: '#a78bfa' },
    ],
    logs: [
      { event: 'Analyse juridique', agent: 'Raisonnement', detail: 'Option A: conforme (0.91) — Option B: risque (0.42)', type: 'info' as const },
      { event: 'Incohérence détectée', agent: 'Raisonnement', detail: 'Recommandation contredit data.confiance', type: 'warn' as const },
    ],
    highlight: ['reasoning'],
  },
  // Phase 4: Mediator freezes (conflict!)
  {
    messages: [
      { from: 'mediator', to: 'action', subject: 'cleman.mediator.freeze', color: '#fbbf24' },
    ],
    logs: [
      { event: '⚠️ CONFLIT DÉTECTÉ', agent: 'Médiateur', detail: 'data=0.87 vs reasoning=0.42 — Gel préventif', type: 'freeze' as const },
      { event: 'Intention gelée', agent: 'Médiateur', detail: 'Action bloquée en attente arbitrage', type: 'warn' as const },
    ],
    highlight: ['mediator', 'action'],
  },
  // Phase 5: Journal records everything
  {
    messages: [
      { from: 'supervisor', to: 'journal', subject: 'journal.append', color: '#fb7185' },
      { from: 'mediator', to: 'journal', subject: 'journal.append', color: '#fbbf24' },
    ],
    logs: [
      { event: 'Entrée WORM #47', agent: 'Journal', detail: 'SHA-256: a3f8...b2c1 — Append-only ✓', type: 'success' as const },
      { event: 'Dossier arbitrage', agent: 'Superviseur', detail: 'Préparé pour décision humaine', type: 'info' as const },
    ],
    highlight: ['supervisor', 'journal'],
  },
  // Phase 6: Human arbitration
  {
    messages: [
      { from: 'orchestrator', to: 'mediator', subject: 'cleman.arbitration.decision', color: '#22d3ee' },
    ],
    logs: [
      { event: '👨‍⚖️ Arbitrage humain', agent: 'Orchestrateur', detail: 'Décision: Option A retenue — Dégel autorisé', type: 'success' as const },
    ],
    highlight: ['orchestrator'],
  },
  // Phase 7: Action executes (unfrozen)
  {
    messages: [
      { from: 'mediator', to: 'action', subject: 'cleman.action.execute', color: '#34d399' },
    ],
    logs: [
      { event: 'Dégel confirmé', agent: 'Médiateur', detail: 'Verrou libéré — Exécution autorisée', type: 'success' as const },
      { event: 'Action exécutée', agent: 'Action', detail: 'Rapport TVA généré + saga compensée ✓', type: 'success' as const },
    ],
    highlight: ['action'],
  },
  // Phase 8: Final journal entry
  {
    messages: [
      { from: 'action', to: 'journal', subject: 'journal.append', color: '#34d399' },
    ],
    logs: [
      { event: 'Entrée WORM #48', agent: 'Journal', detail: 'SHA-256: b7d2...e4f3 — Flux complet ✓', type: 'success' as const },
      { event: '✅ Intention complétée', agent: 'Orchestrateur', detail: 'Conformité TVA validée — 2.3s total', type: 'success' as const },
    ],
    highlight: ['journal', 'orchestrator'],
  },
]

// ── Component ──────────────────────────────────────────────
export function AgentFlowAnimation() {
  const [phase, setPhase] = useState(-1)
  const [playing, setPlaying] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [highlightedAgents, setHighlightedAgents] = useState<Set<string>>(new Set())
  const [speed, setSpeed] = useState(1)
  const animRef = useRef<number>(0)
  const phaseTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const msgIdRef = useRef(0)

  // Reset
  const reset = useCallback(() => {
    setPhase(-1)
    setMessages([])
    setLogs([])
    setHighlightedAgents(new Set())
    setPlaying(false)
    if (phaseTimerRef.current) clearTimeout(phaseTimerRef.current)
    if (animRef.current) cancelAnimationFrame(animRef.current)
  }, [])

  // Advance phase
  const advancePhase = useCallback(() => {
    setPhase(prev => {
      const next = prev + 1
      if (next >= SCENARIO_PHASES.length) {
        // Loop: reset after last phase
        setTimeout(() => reset(), 2000)
        return prev
      }

      const scenario = SCENARIO_PHASES[next]

      // Add messages
      setMessages(prev => [
        ...prev.filter(m => m.progress < 1), // keep only traveling messages
        ...scenario.messages.map(m => ({
          id: ++msgIdRef.current,
          from: m.from,
          to: m.to,
          subject: m.subject,
          color: m.color,
          progress: 0,
          phase: next,
        })),
      ])

      // Add logs
      setLogs(prev => [
        ...prev.slice(-12), // keep last 12
        ...scenario.logs.map((l, i) => ({
          id: prev.length + i,
          timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          ...l,
        })),
      ])

      // Highlight agents
      setHighlightedAgents(new Set(scenario.highlight))

      return next
    })
  }, [reset])

  // Auto-play logic
  useEffect(() => {
    if (!playing) return

    advancePhase()

    const interval = setInterval(() => {
      setPhase(prev => {
        if (prev >= SCENARIO_PHASES.length - 1) {
          clearInterval(interval)
          return prev
        }
        return prev
      })
      advancePhase()
    }, (2200 / speed))

    return () => clearInterval(interval)
  }, [playing, speed, advancePhase])

  // Animate messages
  useEffect(() => {
    let lastTime = performance.now()

    const animate = (now: number) => {
      const dt = (now - lastTime) / 1000
      lastTime = now

      setMessages(prev =>
        prev
          .map(m => ({ ...m, progress: Math.min(1, m.progress + dt * 0.8 * speed) }))
          .filter(m => m.progress < 1.05) // slight buffer before removal
      )

      animRef.current = requestAnimationFrame(animate)
    }

    animRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animRef.current)
  }, [speed])

  // Get agent by id
  const getAgent = (id: string) => AGENTS.find(a => a.id === id)!

  // SVG coordinate helpers
  const nodeR = 28
  const svgW = 600
  const svgH = 420
  const padX = 40
  const padY = 30

  const toSvgX = (pct: number) => padX + (pct / 100) * (svgW - padX * 2)
  const toSvgY = (pct: number) => padY + (pct / 100) * (svgH - padY * 2)

  // Current phase description
  const phaseDescriptions = [
    '1️⃣ L\'utilisateur soumet une intention',
    '2️⃣ Le Médiateur vérifie les règles JsonLogic',
    '3️⃣ L\'Agent Data collecte les données',
    '4️⃣ L\'Agent Raisonnement analyse et détecte un conflit',
    '5️⃣ ⚠️ GEL PRÉVENTIF — Action bloquée !',
    '6️⃣ Journal WORM enregistre tout',
    '7️⃣ 👨‍⚖️ Arbitrage humain — L\'humain décide',
    '8️⃣ Exécution après dégel',
    '9️⃣ Flux complété — Audit trail complet',
  ]

  return (
    <div className="glass" style={{ padding: '2rem', overflow: 'hidden' }}>
      {/* Header with controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 className="mono" style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.375rem' }}>
            Communication temps réel des agents
          </h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
            Flux NATS JetStream — Cliquez Play pour démarrer la simulation
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {/* Speed control */}
          <select
            value={speed}
            onChange={e => setSpeed(Number(e.target.value))}
            style={{
              background: 'var(--bg-card-solid)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border)',
              borderRadius: '0.375rem',
              padding: '0.375rem 0.5rem',
              fontSize: '0.75rem',
              fontFamily: 'JetBrains Mono, monospace',
              cursor: 'pointer',
            }}
          >
            <option value={0.5}>0.5×</option>
            <option value={1}>1×</option>
            <option value={2}>2×</option>
            <option value={3}>3×</option>
          </select>

          {/* Play/Pause */}
          <button
            onClick={() => { if (!playing && phase >= SCENARIO_PHASES.length - 1) reset(); setPlaying(!playing) }}
            className="btn btn-primary"
            style={{ padding: '0.375rem 1rem', fontSize: '0.75rem' }}
          >
            {playing ? '⏸ Pause' : '▶ Play'}
          </button>

          {/* Reset */}
          <button
            onClick={reset}
            className="btn btn-secondary"
            style={{ padding: '0.375rem 1rem', fontSize: '0.75rem' }}
          >
            ↺ Reset
          </button>
        </div>
      </div>

      {/* Phase indicator */}
      {phase >= 0 && phase < phaseDescriptions.length && (
        <div style={{
          marginBottom: '1rem',
          padding: '0.625rem 1rem',
          borderRadius: '0.5rem',
          background: highlightedAgents.has('mediator') && phase === 4
            ? 'rgba(251,191,36,0.1)'
            : 'rgba(34,211,238,0.05)',
          border: `1px solid ${highlightedAgents.has('mediator') && phase === 4
            ? 'rgba(251,191,36,0.3)'
            : 'rgba(34,211,238,0.15)'}`,
          fontSize: '0.8125rem',
          fontWeight: 600,
          color: highlightedAgents.has('mediator') && phase === 4 ? 'var(--amber)' : 'var(--cyan)',
          fontFamily: 'JetBrains Mono, monospace',
        }}>
          {phaseDescriptions[phase]}
        </div>
      )}

      {/* Two columns: Graph + Log */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '1.25rem' }}>
        {/* Agent Graph (SVG) */}
        <div style={{
          background: 'rgba(2,6,23,0.6)',
          borderRadius: '0.75rem',
          border: '1px solid var(--border)',
          padding: '0.5rem',
          position: 'relative',
        }}>
          <svg viewBox={`0 0 ${svgW} ${svgH}`} style={{ width: '100%', height: 'auto' }}>
            {/* Connection lines (bus NATS) */}
            <defs>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
              <marker id="arrowhead" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
                <polygon points="0 0, 6 2, 0 4" fill="#475569" />
              </marker>
            </defs>

            {/* NATS Bus background lines */}
            {AGENTS.flatMap(from =>
              AGENTS.filter(to => to.id !== from.id && to.id !== 'journal').map(to => (
                <line
                  key={`${from.id}-${to.id}`}
                  x1={toSvgX(from.x)}
                  y1={toSvgY(from.y)}
                  x2={toSvgX(to.x)}
                  y2={toSvgY(to.y)}
                  stroke="rgba(30,41,59,0.5)"
                  strokeWidth="0.5"
                  strokeDasharray="4,4"
                />
              ))
            )}

            {/* Journal connections (dashed) */}
            {AGENTS.filter(a => a.id !== 'journal').map(a => (
              <line
                key={`journal-${a.id}`}
                x1={toSvgX(a.x)}
                y1={toSvgY(a.y)}
                x2={toSvgX(AGENTS[6].x)}
                y2={toSvgY(AGENTS[6].y)}
                stroke="rgba(148,163,184,0.15)"
                strokeWidth="0.5"
                strokeDasharray="2,4"
              />
            ))}

            {/* Animated messages */}
            {messages.map(msg => {
              const from = getAgent(msg.from)
              const to = getAgent(msg.to)
              const x1 = toSvgX(from.x)
              const y1 = toSvgY(from.y)
              const x2 = toSvgX(to.x)
              const y2 = toSvgY(to.y)
              const p = Math.min(msg.progress, 1)

              // Curved path
              const mx = (x1 + x2) / 2
              const my = (y1 + y2) / 2
              const dx = x2 - x1
              const dy = y2 - y1
              const offset = 20
              const cx = mx + (-dy / Math.sqrt(dx*dx + dy*dy)) * offset
              const cy = my + (dx / Math.sqrt(dx*dx + dy*dy)) * offset

              // Position on quadratic bezier
              const t = p
              const px = (1-t)*(1-t)*x1 + 2*(1-t)*t*cx + t*t*x2
              const py = (1-t)*(1-t)*y1 + 2*(1-t)*t*cy + t*t*y2

              return (
                <g key={msg.id}>
                  {/* Trail */}
                  <path
                    d={`M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`}
                    fill="none"
                    stroke={msg.color}
                    strokeWidth="1.5"
                    strokeDasharray={`${p * 100} ${200}`}
                    opacity={0.3}
                  />
                  {/* Dot */}
                  <circle
                    cx={px}
                    cy={py}
                    r="4"
                    fill={msg.color}
                    filter="url(#glow)"
                    opacity={1 - Math.max(0, msg.progress - 0.85) * 6}
                  />
                  {/* Label */}
                  {msg.progress > 0.1 && msg.progress < 0.6 && (
                    <text
                      x={px}
                      y={py - 10}
                      textAnchor="middle"
                      fill={msg.color}
                      fontSize="7"
                      fontFamily="JetBrains Mono, monospace"
                      opacity={0.8}
                    >
                      {msg.subject}
                    </text>
                  )}
                </g>
              )
            })}

            {/* Agent nodes */}
            {AGENTS.map(agent => {
              const isHighlighted = highlightedAgents.has(agent.id)
              const isFrozen = agent.id === 'action' && phase === 4
              return (
                <g key={agent.id}>
                  {/* Highlight ring */}
                  {isHighlighted && (
                    <circle
                      cx={toSvgX(agent.x)}
                      cy={toSvgY(agent.y)}
                      r={nodeR + 8}
                      fill="none"
                      stroke={agent.color}
                      strokeWidth="1.5"
                      opacity={0.4}
                      strokeDasharray="3,3"
                    >
                      <animateTransform
                        attributeName="transform"
                        type="rotate"
                        from={`0 ${toSvgX(agent.x)} ${toSvgY(agent.y)}`}
                        to={`360 ${toSvgX(agent.x)} ${toSvgY(agent.y)}`}
                        dur="4s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  )}

                  {/* Node background */}
                  <circle
                    cx={toSvgX(agent.x)}
                    cy={toSvgY(agent.y)}
                    r={nodeR}
                    fill={isFrozen ? 'rgba(251,191,36,0.15)' : isHighlighted ? `${agent.color}15` : 'rgba(15,23,42,0.9)'}
                    stroke={isFrozen ? '#fbbf24' : isHighlighted ? agent.color : 'rgba(30,41,59,0.8)'}
                    strokeWidth={isHighlighted ? 2 : 1}
                    style={{ transition: 'all 0.4s ease' }}
                  />

                  {/* Icon */}
                  <text
                    x={toSvgX(agent.x)}
                    y={toSvgY(agent.y) + 1}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize="16"
                  >
                    {agent.icon}
                  </text>

                  {/* Label */}
                  <text
                    x={toSvgX(agent.x)}
                    y={toSvgY(agent.y) + nodeR + 14}
                    textAnchor="middle"
                    fill={isHighlighted ? agent.color : '#94a3b8'}
                    fontSize="9"
                    fontFamily="JetBrains Mono, monospace"
                    fontWeight={isHighlighted ? 700 : 500}
                  >
                    {agent.label}
                  </text>

                  {/* Type badge */}
                  <text
                    x={toSvgX(agent.x)}
                    y={toSvgY(agent.y) + nodeR + 24}
                    textAnchor="middle"
                    fill={agent.type === 'llm' ? '#22d3ee' : agent.type === 'human' ? '#fbbf24' : '#475569'}
                    fontSize="7"
                    fontFamily="JetBrains Mono, monospace"
                  >
                    {agent.type === 'llm' ? 'LLM' : agent.type === 'human' ? 'HUMAN' : 'PROG'}
                  </text>

                  {/* Freeze icon for Action agent */}
                  {isFrozen && (
                    <text
                      x={toSvgX(agent.x) + nodeR - 4}
                      y={toSvgY(agent.y) - nodeR + 8}
                      textAnchor="middle"
                      fontSize="12"
                    >
                      🔒
                    </text>
                  )}
                </g>
              )
            })}

            {/* NATS Bus label */}
            <text x={svgW / 2} y={svgH - 5} textAnchor="middle" fill="#475569" fontSize="8" fontFamily="JetBrains Mono, monospace">
              NATS JetStream — Bus événementiel pair-à-pair
            </text>
          </svg>
        </div>

        {/* Event Log */}
        <div style={{
          background: 'rgba(2,6,23,0.6)',
          borderRadius: '0.75rem',
          border: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          maxHeight: '420px',
        }}>
          <div style={{
            padding: '0.625rem 0.875rem',
            borderBottom: '1px solid var(--border)',
            fontSize: '0.6875rem',
            fontWeight: 600,
            color: 'var(--text-dim)',
            fontFamily: 'JetBrains Mono, monospace',
            display: 'flex',
            justifyContent: 'space-between',
          }}>
            <span>📋 Journal d'événements</span>
            <span style={{ color: 'var(--emerald)' }}>WORM</span>
          </div>
          <div style={{
            flex: 1,
            overflow: 'auto',
            padding: '0.5rem',
          }}>
            {logs.length === 0 && (
              <div style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                Appuyez sur ▶ Play pour démarrer<br />
                <span style={{ fontSize: '0.625rem', marginTop: '0.5rem', display: 'block' }}>
                  Scénario: Audit TVA cabinet Dupont
                </span>
              </div>
            )}
            {logs.map(log => (
              <div
                key={log.id}
                style={{
                  padding: '0.5rem 0.625rem',
                  marginBottom: '0.375rem',
                  borderRadius: '0.375rem',
                  background:
                    log.type === 'freeze' ? 'rgba(251,191,36,0.08)' :
                    log.type === 'warn' ? 'rgba(251,191,36,0.05)' :
                    log.type === 'success' ? 'rgba(52,211,153,0.05)' :
                    'rgba(34,211,238,0.03)',
                  borderLeft: `3px solid ${
                    log.type === 'freeze' ? '#fbbf24' :
                    log.type === 'warn' ? '#fb923c' :
                    log.type === 'success' ? '#34d399' :
                    '#22d3ee'
                  }`,
                  fontSize: '0.6875rem',
                  fontFamily: 'JetBrains Mono, monospace',
                  animation: 'fade-up 0.3s ease-out',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.125rem' }}>
                  <span style={{ color: 'var(--text)', fontWeight: 600, fontSize: '0.625rem' }}>{log.event}</span>
                  <span style={{ color: 'var(--text-dim)', fontSize: '0.5625rem' }}>{log.timestamp}</span>
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.5625rem' }}>
                  <span style={{ color: 'var(--text-dim)' }}>[{log.agent}]</span> {log.detail}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        {[
          { color: '#22d3ee', label: 'LLM Agent' },
          { color: '#34d399', label: 'Programmatique' },
          { color: '#fbbf24', label: 'Médiateur / Gel' },
          { color: '#94a3b8', label: 'Journal WORM' },
        ].map((item, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: item.color }} />
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', fontFamily: 'JetBrains Mono, monospace' }}>
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
