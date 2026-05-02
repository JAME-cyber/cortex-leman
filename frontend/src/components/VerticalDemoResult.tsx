import { useState, useEffect } from 'react'

/* ═══════════════════════════════════════════════════════════
   CORTEX LEMAN V5 — Vertical Demo Result
   Tangible compliance result for the comptable vertical.
   Shows a real-world audit scenario with rules, scores, 
   journal entries and final decision.
   ═══════════════════════════════════════════════════════════ */

// ── Real rules from comptable.json ─────────────────────────
const RULES = [
  { id: 'comptable-001', name: 'Aucune décision fiscale automatique', severity: 'critical', status: 'passed' },
  { id: 'comptable-002', name: 'Données client en EU uniquement', severity: 'high', status: 'passed' },
  { id: 'comptable-003', name: 'Montant > 10K€ nécessite validation', severity: 'high', status: 'triggered' },
  { id: 'comptable-004', name: 'Anti-biais: vérification cohérence', severity: 'medium', status: 'passed' },
  { id: 'comptable-005', name: 'Audit trail obligatoire pour écritures', severity: 'critical', status: 'passed' },
  { id: 'comptable-006', name: 'Déduction fiscale élevée', severity: 'high', status: 'triggered' },
  { id: 'comptable-007', name: 'Conflit de déduction entre sources', severity: 'high', status: 'passed' },
]

// ── Simulated journal entries ──────────────────────────────
const JOURNAL_ENTRIES = [
  { hash: 'a3f8...b2c1', time: '14:32:01', event: 'intention.new', agent: 'Orchestrateur', detail: 'Vertical: comptable — Client: Dupont SARL' },
  { hash: '7d2e...4a9f', time: '14:32:02', event: 'mediator.check', agent: 'Médiateur', detail: '7 règles évaluées — 2 déclenchées' },
  { hash: 'f1b3...8c7d', time: '14:32:03', event: 'data.query', agent: 'Data', detail: 'RAG: 3 sources (BOFIP, CGI, AFC) — confiance: 0.91' },
  { hash: 'e9a4...2d6b', time: '14:32:04', event: 'reasoning.analyze', agent: 'Raisonnement', detail: 'TVA déductible: 47 320€ sur 312 150€ HT' },
  { hash: 'c5d1...f3a8', time: '14:32:05', event: 'mediator.freeze', agent: 'Médiateur', detail: 'Règle comptable-006: Déduction > 50K CHF → GEL' },
  { hash: 'b8f2...1e4c', time: '14:32:06', event: 'journal.append', agent: 'Journal', detail: 'WORM entry #47 — SHA-256 chain verified ✓' },
  { hash: 'd4a7...9b5e', time: '14:32:18', event: 'arbitration.decision', agent: 'Humain', detail: 'Expert validé: déduction conforme, dégel autorisé' },
  { hash: '6c3f...a7d2', time: '14:32:19', event: 'action.execute', agent: 'Action', detail: 'Écriture comptable générée + audit trail ✓' },
]

// ── Animated counter hook ──────────────────────────────────
function useAnimatedNumber(target: number, duration: number = 1500, start: boolean = true) {
  const [value, setValue] = useState(0)
  useEffect(() => {
    if (!start) return
    let startTime: number
    const animate = (now: number) => {
      if (!startTime) startTime = now
      const progress = Math.min((now - startTime) / duration, 1)
      setValue(Math.round(progress * target))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [target, duration, start])
  return value
}

// ── Severity badge ─────────────────────────────────────────
function SeverityBadge({ severity }: { severity: string }) {
  const config: Record<string, { bg: string; color: string; label: string }> = {
    critical: { bg: 'rgba(251,113,133,0.1)', color: '#fb7185', label: 'CRITIQUE' },
    high: { bg: 'rgba(251,191,36,0.1)', color: '#fbbf24', label: 'ÉLEVÉ' },
    medium: { bg: 'rgba(96,165,250,0.1)', color: '#60a5fa', label: 'MOYEN' },
  }
  const c = config[severity] || config.medium
  return (
    <span style={{
      padding: '0.125rem 0.5rem', borderRadius: '0.25rem',
      background: c.bg, color: c.color, fontSize: '0.5625rem',
      fontWeight: 700, fontFamily: 'JetBrains Mono, monospace',
    }}>
      {c.label}
    </span>
  )
}

// ── Status indicator ───────────────────────────────────────
function StatusIndicator({ status }: { status: string }) {
  if (status === 'triggered') {
    return (
      <span style={{
        padding: '0.125rem 0.5rem', borderRadius: '0.25rem',
        background: 'rgba(251,191,36,0.1)', color: '#fbbf24',
        fontSize: '0.5625rem', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace',
      }}>
        ⚠️ DÉCLENCHÉE
      </span>
    )
  }
  return (
    <span style={{
      padding: '0.125rem 0.5rem', borderRadius: '0.25rem',
      background: 'rgba(52,211,153,0.1)', color: '#34d399',
      fontSize: '0.5625rem', fontWeight: 700, fontFamily: 'JetBrains Mono, monospace',
    }}>
      ✓ CONFORME
    </span>
  )
}

// ── Main Component ─────────────────────────────────────────
export function VerticalDemoResult() {
  const [activeTab, setActiveTab] = useState<'rules' | 'journal' | 'report'>('rules')
  const [visible, setVisible] = useState(false)
  const [animatedRules, setAnimatedRules] = useState(0)

  // Animate rules appearing one by one
  useEffect(() => {
    if (!visible) return
    let count = 0
    const interval = setInterval(() => {
      count++
      setAnimatedRules(count)
      if (count >= RULES.length) clearInterval(interval)
    }, 200)
    return () => clearInterval(interval)
  }, [visible])

  // Intersection observer to trigger animation
  const refCallback = (node: HTMLDivElement | null) => {
    if (!node) return
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true) },
      { threshold: 0.3 }
    )
    observer.observe(node)
    return () => observer.disconnect()
  }

  const complianceScore = useAnimatedNumber(86, 2000, visible)
  const rulesPassed = RULES.filter(r => r.status === 'passed').length
  const rulesTriggered = RULES.filter(r => r.status === 'triggered').length

  const tabs = [
    { id: 'rules' as const, label: '🛡️ Règles JsonLogic', },
    { id: 'journal' as const, label: '📝 Journal WORM', },
    { id: 'report' as const, label: '📊 Rapport', },
  ]

  return (
    <div ref={refCallback} className="glass" style={{ padding: '2rem', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>📊</span>
            <h3 className="mono" style={{ fontSize: '1.125rem', fontWeight: 700 }}>
              Résultat concret — Vertical Comptable
            </h3>
          </div>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', maxWidth: 500 }}>
            Audit TVA pour le cabinet <strong style={{ color: 'var(--cyan)' }}>Dupont SARL</strong> — 
            Vérification déduction fiscale Q1 2026 — Montant: <strong style={{ color: 'var(--amber)' }}>47 320€</strong>
          </p>
        </div>

        {/* Score circle */}
        <div style={{
          width: 80, height: 80, borderRadius: '50%',
          background: `conic-gradient(var(--cyan) ${complianceScore * 3.6}deg, var(--border) 0deg)`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          position: 'relative',
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: '50%',
            background: 'var(--bg-card-solid)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            flexDirection: 'column',
          }}>
            <span className="mono" style={{ fontSize: '1.25rem', fontWeight: 800, color: complianceScore >= 80 ? 'var(--cyan)' : 'var(--amber)' }}>
              {complianceScore}%
            </span>
            <span style={{ fontSize: '0.5rem', color: 'var(--text-dim)' }}>CONFORMITÉ</span>
          </div>
        </div>
      </div>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem', marginBottom: '1.5rem' }}>
        {[
          { icon: '🛡️', label: 'Règles évaluées', value: `${animatedRules}/7`, color: 'var(--cyan)' },
          { icon: '✅', label: 'Conformes', value: String(rulesPassed), color: 'var(--emerald)' },
          { icon: '⚠️', label: 'Déclenchées', value: String(rulesTriggered), color: 'var(--amber)' },
          { icon: '🔒', label: 'Gel préventif', value: '1', color: 'var(--rose)' },
          { icon: '👨‍⚖️', label: 'Arbitrage humain', value: '1', color: 'var(--violet)' },
          { icon: '⏱️', label: 'Temps total', value: '2.3s', color: 'var(--blue)' },
        ].map((stat, i) => (
          <div
            key={i}
            style={{
              padding: '0.75rem',
              borderRadius: '0.5rem',
              background: 'rgba(2,6,23,0.6)',
              border: '1px solid var(--border)',
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateY(0)' : 'translateY(10px)',
              transition: `all 0.4s ease ${i * 0.1}s`,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.375rem' }}>
              <span style={{ fontSize: '0.875rem' }}>{stat.icon}</span>
              <span style={{ fontSize: '0.625rem', color: 'var(--text-dim)', fontWeight: 600 }}>{stat.label}</span>
            </div>
            <div className="mono" style={{ fontSize: '1.125rem', fontWeight: 800, color: stat.color }}>{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.25rem', marginBottom: '1rem', background: 'rgba(2,6,23,0.6)', borderRadius: '0.5rem', padding: '0.25rem' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1, padding: '0.5rem 0.75rem', borderRadius: '0.375rem',
              background: activeTab === tab.id ? 'rgba(34,211,238,0.1)' : 'transparent',
              border: 'none', color: activeTab === tab.id ? 'var(--cyan)' : 'var(--text-dim)',
              fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer',
              fontFamily: 'JetBrains Mono, monospace',
              transition: 'all 0.2s',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ minHeight: 320 }}>
        {/* ── Rules Tab ── */}
        {activeTab === 'rules' && (
          <div>
            <div style={{
              display: 'grid', gridTemplateColumns: '1fr auto auto auto',
              gap: '0.5rem 1rem', padding: '0.5rem 0.75rem',
              fontSize: '0.5625rem', fontWeight: 700, color: 'var(--text-dim)',
              borderBottom: '1px solid var(--border)', marginBottom: '0.375rem',
              fontFamily: 'JetBrains Mono, monospace', textTransform: 'uppercase',
            }}>
              <span>Règle JsonLogic</span>
              <span>ID</span>
              <span>Sévérité</span>
              <span>Statut</span>
            </div>
            {RULES.map((rule, i) => (
              <div
                key={rule.id}
                style={{
                  display: 'grid', gridTemplateColumns: '1fr auto auto auto',
                  gap: '0.5rem 1rem', padding: '0.625rem 0.75rem',
                  alignItems: 'center',
                  borderBottom: '1px solid rgba(30,41,59,0.3)',
                  background: rule.status === 'triggered' ? 'rgba(251,191,36,0.03)' : 'transparent',
                  opacity: i < animatedRules ? 1 : 0,
                  transform: i < animatedRules ? 'translateX(0)' : 'translateX(-10px)',
                  transition: 'all 0.3s ease',
                }}
              >
                <span className="mono" style={{ fontSize: '0.75rem', fontWeight: 500 }}>
                  {rule.name}
                </span>
                <span className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                  {rule.id}
                </span>
                <SeverityBadge severity={rule.severity} />
                <StatusIndicator status={rule.status} />
              </div>
            ))}

            {/* Triggered rule detail */}
            {animatedRules >= 7 && (
              <div style={{
                marginTop: '1rem', padding: '1rem',
                borderRadius: '0.5rem',
                background: 'rgba(251,191,36,0.05)',
                border: '1px solid rgba(251,191,36,0.2)',
                animation: 'fade-up 0.5s ease-out',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '1rem' }}>⚠️</span>
                  <span className="mono" style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--amber)' }}>
                    Règles déclenchées — Détails
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
                  <div><strong style={{ color: 'var(--text)' }}>comptable-003:</strong> Montant 47 320€ = seuil dépassé (10K€) → Arbitrage requis (anti-blanchiment)</div>
                  <div><strong style={{ color: 'var(--text)' }}>comptable-006:</strong> Déduction fiscale élevée → Gel préventif, vérification CA et éligibilité requise</div>
                  <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(52,211,153,0.05)', borderRadius: '0.375rem', borderLeft: '3px solid var(--emerald)' }}>
                    <strong style={{ color: 'var(--emerald)' }}>Résolution:</strong> Expert comptable a validé — déduction conforme au BOFIP art. 236. Gel levé.
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Journal Tab ── */}
        {activeTab === 'journal' && (
          <div style={{ maxHeight: 400, overflowY: 'auto' }}>
            {JOURNAL_ENTRIES.map((entry, i) => (
              <div
                key={i}
                style={{
                  display: 'grid', gridTemplateColumns: '80px 70px 120px 1fr',
                  gap: '0.5rem', padding: '0.625rem 0.75rem',
                  borderBottom: '1px solid rgba(30,41,59,0.3)',
                  fontSize: '0.6875rem',
                  fontFamily: 'JetBrains Mono, monospace',
                  alignItems: 'center',
                  opacity: visible ? 1 : 0,
                  transition: `opacity 0.3s ease ${i * 0.1}s`,
                }}
              >
                <span style={{ color: 'var(--text-dim)', fontSize: '0.625rem' }}>{entry.time}</span>
                <span style={{
                  padding: '0.125rem 0.375rem', borderRadius: '0.25rem',
                  background: entry.event.includes('freeze') ? 'rgba(251,191,36,0.1)' :
                    entry.event.includes('arbitration') ? 'rgba(167,139,250,0.1)' :
                    entry.event.includes('action') ? 'rgba(52,211,153,0.1)' :
                    'rgba(34,211,238,0.05)',
                  color: entry.event.includes('freeze') ? '#fbbf24' :
                    entry.event.includes('arbitration') ? '#a78bfa' :
                    entry.event.includes('action') ? '#34d399' :
                    '#94a3b8',
                  fontSize: '0.5625rem', fontWeight: 600,
                }}>
                  {entry.event}
                </span>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.625rem' }}>{entry.agent}</span>
                <div>
                  <span style={{ color: 'var(--text-dim)', fontSize: '0.5625rem' }}>{entry.detail}</span>
                  <div style={{ fontSize: '0.5rem', color: 'rgba(148,163,184,0.4)', marginTop: '0.125rem' }}>
                    SHA-256: {entry.hash}
                  </div>
                </div>
              </div>
            ))}

            {/* Integrity verification */}
            <div style={{
              marginTop: '1rem', padding: '0.75rem 1rem',
              borderRadius: '0.5rem',
              background: 'rgba(52,211,153,0.05)',
              border: '1px solid rgba(52,211,153,0.15)',
              display: 'flex', alignItems: 'center', gap: '0.75rem',
            }}>
              <span style={{ fontSize: '1.25rem' }}>🔐</span>
              <div>
                <div className="mono" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--emerald)' }}>
                  Intégrité WORM vérifiée
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                  8 entrées — Hash-chain SHA-256 continue — Aucune altération détectée
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ── Report Tab ── */}
        {activeTab === 'report' && (
          <div>
            {/* Executive summary */}
            <div style={{
              padding: '1.25rem', borderRadius: '0.75rem',
              background: 'rgba(34,211,238,0.03)',
              border: '1px solid rgba(34,211,238,0.15)',
              marginBottom: '1rem',
            }}>
              <h4 className="mono" style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--cyan)', marginBottom: '0.75rem' }}>
                📋 Rapport de Conformité — Executive Summary
              </h4>
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>
                <strong style={{ color: 'var(--text)' }}>Client:</strong> Dupont SARL — Cabinet d'expertise comptable, Annecy (74)<br />
                <strong style={{ color: 'var(--text)' }}>Objet:</strong> Vérification conformité TVA — Déduction Q1 2026<br />
                <strong style={{ color: 'var(--text)' }}>Montant:</strong> 47 320€ de TVA déductible sur 312 150€ HT<br />
                <strong style={{ color: 'var(--text)' }}>Sources:</strong> BOFIP art. 236, CGI art. 271, AFC guide 2026<br />
                <strong style={{ color: 'var(--text)' }}>Décision:</strong> <span style={{ color: 'var(--emerald)', fontWeight: 700 }}>CONFORME — Déduction validée</span><br />
                <strong style={{ color: 'var(--text)' }}>Référence audit:</strong> WORM-2026-04-29-#47-#48
              </div>
            </div>

            {/* Timeline */}
            <h4 className="mono" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '0.75rem' }}>
              CHRONOLOGIE DU FLUX
            </h4>
            <div style={{ position: 'relative', paddingLeft: '1.5rem' }}>
              {/* Timeline line */}
              <div style={{
                position: 'absolute', left: '0.5rem', top: 0, bottom: 0, width: 2,
                background: 'linear-gradient(to bottom, var(--cyan), var(--amber), var(--emerald))',
                borderRadius: 1,
              }} />

              {[
                { time: '14:32:01', label: 'Intention soumise', detail: '"Vérifier conformité TVA client Dupont Q1 2026"', color: '#22d3ee' },
                { time: '14:32:02', label: 'Médiateur: 7 règles évaluées', detail: '5 conformes, 2 déclenchées → Gel préventif', color: '#fbbf24' },
                { time: '14:32:03', label: 'Data: 3 sources RAG trouvées', detail: 'BOFIP + CGI + AFC — Score confiance: 0.91', color: '#60a5fa' },
                { time: '14:32:04', label: 'Raisonnement: Analyse fiscale', detail: 'TVA 15.2% — Taux normal, déduction éligible', color: '#a78bfa' },
                { time: '14:32:05', label: '⚠️ Gel préventif automatique', detail: 'comptable-006: Montant > seuil → Action bloquée', color: '#fbbf24' },
                { time: '14:32:18', label: '👨‍⚖️ Arbitrage humain', detail: 'Expert: "Déduction conforme au BOFIP" — Dégel', color: '#a78bfa' },
                { time: '14:32:19', label: 'Action: Écriture générée', detail: 'Écriture TVA-2026-Q1-DUPONT + audit trail', color: '#34d399' },
                { time: '14:32:19', label: '✅ Flux complété', detail: 'Score conformité: 86% — 2.3s total', color: '#34d399' },
              ].map((step, i) => (
                <div
                  key={i}
                  style={{
                    position: 'relative', paddingBottom: '1rem',
                    opacity: visible ? 1 : 0,
                    transition: `opacity 0.3s ease ${i * 0.08}s`,
                  }}
                >
                  {/* Dot */}
                  <div style={{
                    position: 'absolute', left: '-1.125rem', top: '0.25rem',
                    width: 10, height: 10, borderRadius: '50%',
                    background: step.color, border: `2px solid var(--bg-card-solid)`,
                  }} />
                  <div style={{ paddingLeft: '0.25rem' }}>
                    <div className="mono" style={{ fontSize: '0.6875rem', fontWeight: 700, color: step.color }}>
                      {step.time} — {step.label}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{step.detail}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Certification footer */}
            <div style={{
              marginTop: '1rem', padding: '0.75rem 1rem',
              borderRadius: '0.5rem',
              background: 'rgba(52,211,153,0.05)',
              border: '1px solid rgba(52,211,153,0.15)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              flexWrap: 'wrap', gap: '0.5rem',
            }}>
              <div>
                <div className="mono" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--emerald)' }}>
                  🏆 Audit Trail Certifié
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>
                  Journal WORM hash-chainé · Conforme RGPD Art. 30 · AI Act Art. 12
                </div>
              </div>
              <div className="mono" style={{ fontSize: '0.625rem', color: 'var(--text-dim)' }}>
                Généré par Cortex Leman v5 — 29/04/2026
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
