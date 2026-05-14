import { useState, useEffect } from 'react'

/* ═══════════════════════════════════════════════════════════
   CORTEX LEMAN V5 — ROI Calculator
   Calculateur interactif par vertical
   Inspiré de: Harvey AI ROI Calculator + Scale AI
   ═══════════════════════════════════════════════════════════ */

const VERTICALS = [
  { id: 'avocat', icon: '⚖️', label: 'Avocat', sub: 'Cabinet juridique' },
  { id: 'comptable', icon: '📊', label: 'Comptable', sub: "Cabinet d'expertise" },
  { id: 'sante', icon: '🏥', label: 'Santé', sub: 'Cabinet médical' },
  { id: 'immobilier', icon: '🏠', label: 'Immobilier', sub: 'Agence immobilière' },
] as const

type VerticalId = typeof VERTICALS[number]['id']

interface VerticalConfig {
  labelPro: string
  labelTask: string
  taskDefault: number
  taskMin: number
  taskMax: number
  timeDefault: number
  rateDefault: number
  reductionPct: number
  breakdown: [number, number, number]
  breakdownLabels: [string, string, string]
}

const CONFIGS: Record<VerticalId, VerticalConfig> = {
  avocat: {
    labelPro: "Nombre d'avocats",
    labelTask: 'Documents / mois',
    taskDefault: 40, taskMin: 5, taskMax: 200,
    timeDefault: 4, rateDefault: 150,
    reductionPct: 0.65,
    breakdown: [60, 20, 20],
    breakdownLabels: ['Automatisation rédaction', 'Veille juridique', 'Conformité & audit'],
  },
  comptable: {
    labelPro: 'Nombre de comptables',
    labelTask: 'Dossiers clients / mois',
    taskDefault: 60, taskMin: 10, taskMax: 300,
    timeDefault: 3, rateDefault: 100,
    reductionPct: 0.55,
    breakdown: [50, 25, 25],
    breakdownLabels: ['Automatisation saisie', 'Veille fiscale', 'Conformité RGPD'],
  },
  sante: {
    labelPro: 'Nombre de médecins',
    labelTask: 'Patients / jour',
    taskDefault: 25, taskMin: 5, taskMax: 60,
    timeDefault: 2, rateDefault: 120,
    reductionPct: 0.50,
    breakdown: [45, 30, 25],
    breakdownLabels: ['Automatisation CR', 'Aide au diagnostic', 'Conformité HDS'],
  },
  immobilier: {
    labelPro: "Nombre d'agents",
    labelTask: 'Biens / mois',
    taskDefault: 15, taskMin: 3, taskMax: 80,
    timeDefault: 3, rateDefault: 90,
    reductionPct: 0.60,
    breakdown: [55, 25, 20],
    breakdownLabels: ['Marketing automatique', 'Estimation IA', 'Gestion mandates'],
  },
}

const BAR_COLORS = ['var(--cyan)', 'var(--emerald)', 'var(--violet)'] as const

function formatNum(n: number) {
  return Math.round(n).toLocaleString('fr-FR')
}

// BANT qualifying questions (Isabella pattern)
const BANT_QUESTIONS = [
  { id: 'challenge', label: 'Votre défi #1 avec l\'IA ?', options: [
    { value: 'conformite', label: '🛡️ Conformité / Sécurité' },
    { value: 'productivite', label: '⚡ Productivité' },
    { value: 'adoption', label: '👥 Adoption équipe' },
    { value: 'budget', label: '💰 Budget / ROI' },
  ]},
  { id: 'timeline', label: 'Quand souhaitez-vous démarrer ?', options: [
    { value: 'immédiat', label: '🔥 Immédiatement' },
    { value: '1mois', label: '📅 Dans 1 mois' },
    { value: 'trimestre', label: '📆 Ce trimestre' },
    { value: 'exploration', label: '🔍 Juste exploration' },
  ]},
] as const

export function ROICalculator({ onCta }: { onCta?: () => void }) {
  const [vertical, setVertical] = useState<VerticalId>('avocat')
  const [professionals, setProfessionals] = useState(5)
  const [tasks, setTasks] = useState(40)
  const [timePerTask, setTimePerTask] = useState(4)
  const [hourlyRate, setHourlyRate] = useState(150)
  const [showGate, setShowGate] = useState(false)
  const [gateEmail, setGateEmail] = useState('')
  const [gateCompany, setGateCompany] = useState('')
  const [gateAnswers, setGateAnswers] = useState<Record<string, string>>({})
  const [gateSubmitted, setGateSubmitted] = useState(false)
  const [hasInteracted, setHasInteracted] = useState(false)

  const cfg = CONFIGS[vertical]

  // Calculations
  const totalTimeMonthly = tasks * timePerTask
  const timeSavedMonthly = totalTimeMonthly * cfg.reductionPct
  const moneySavedMonthly = timeSavedMonthly * hourlyRate
  const moneySavedAnnual = moneySavedMonthly * 12

  // Pricing tier
  let monthlyCost: number
  if (professionals <= 3) monthlyCost = 1500
  else if (professionals <= 10) monthlyCost = 2500
  else if (professionals <= 25) monthlyCost = 4000
  else monthlyCost = 6000

  const roi = monthlyCost > 0 ? Math.round(moneySavedMonthly / monthlyCost) : 0
  const timeSavedPerTask = (timePerTask * cfg.reductionPct).toFixed(1)
  const reductionDisplay = Math.round(cfg.reductionPct * 100)

  function selectVertical(v: VerticalId) {
    setVertical(v)
    const c = CONFIGS[v]
    setTasks(c.taskDefault)
    setTimePerTask(c.timeDefault)
    setHourlyRate(c.rateDefault)
    setHasInteracted(true)
  }

  function handleSlider(fn: (v: number) => void) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      fn(Number(e.target.value))
      setHasInteracted(true)
    }
  }

  // Auto-show gate after meaningful interaction (Isabella: track time spent on resource)
  useEffect(() => {
    if (hasInteracted && !showGate && !gateSubmitted) {
      const timer = setTimeout(() => setShowGate(true), 8000) // 8s after first interaction
      return () => clearTimeout(timer)
    }
  }, [hasInteracted, showGate, gateSubmitted])

  function handleGateSubmit() {
    if (!gateEmail) return
    // In production: POST to /api/v1/lead/roi with { email, company, vertical, scores, bant }
    setGateSubmitted(true)
    setShowGate(false)
  }

  return (
    <section id="roi-calculator" className="section">
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-cyan" style={{ marginBottom: '1rem' }}>📊 ROI Calculator</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Combien votre cabinet <span style={{ color: 'var(--emerald)' }}>économise</span> ?
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto' }}>
          Entrez vos chiffres. Découvrez le retour sur investissement en 30 secondes.
        </p>
      </div>

      {/* Calculator Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', maxWidth: 1100, margin: '0 auto' }}>

        {/* Left: Inputs */}
        <div className="glass" style={{ padding: '2rem' }}>
          <div className="mono" style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1.5rem' }}>
            ⚙️ Votre cabinet
          </div>

          {/* Vertical Selector */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '2rem' }}>
            {VERTICALS.map(v => (
              <button
                key={v.id}
                onClick={() => selectVertical(v.id)}
                style={{
                  background: vertical === v.id ? 'var(--cyan-dim)' : 'transparent',
                  border: `1px solid ${vertical === v.id ? 'var(--cyan)' : 'var(--border)'}`,
                  borderRadius: '0.75rem',
                  padding: '1rem',
                  cursor: 'pointer',
                  textAlign: 'left' as const,
                  transition: 'all 0.2s',
                }}
              >
                <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{v.icon}</div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, color: vertical === v.id ? 'var(--cyan)' : 'var(--text)' }}>{v.label}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>{v.sub}</div>
              </button>
            ))}
          </div>

          {/* Slider: Professionals */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{cfg.labelPro}</span>
              <span className="mono" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--cyan)' }}>{professionals}</span>
            </div>
            <input type="range" min={1} max={50} value={professionals}
              onChange={handleSlider(setProfessionals)}
              style={{ width: '100%', accentColor: 'var(--cyan)' }} />
          </div>

          {/* Slider: Tasks */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{cfg.labelTask}</span>
              <span className="mono" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--cyan)' }}>{tasks}</span>
            </div>
            <input type="range" min={cfg.taskMin} max={cfg.taskMax} step={5} value={tasks}
              onChange={handleSlider(setTasks)}
              style={{ width: '100%', accentColor: 'var(--cyan)' }} />
          </div>

          {/* Slider: Time */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Temps par document (heures)</span>
              <span className="mono" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--cyan)' }}>{timePerTask}</span>
            </div>
            <input type="range" min={1} max={12} step={0.5} value={timePerTask}
              onChange={handleSlider(setTimePerTask)}
              style={{ width: '100%', accentColor: 'var(--cyan)' }} />
          </div>

          {/* Slider: Rate */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Coût horaire moyen (€)</span>
              <span className="mono" style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--cyan)' }}>{hourlyRate}</span>
            </div>
            <input type="range" min={50} max={400} step={10} value={hourlyRate}
              onChange={handleSlider(setHourlyRate)}
              style={{ width: '100%', accentColor: 'var(--cyan)' }} />
          </div>
        </div>

        {/* Right: Results */}
        <div className="glass" style={{ padding: '2rem', position: 'sticky', top: '80px', alignSelf: 'start' }}>
          <div className="mono" style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1.5rem' }}>
            💰 Votre économie
          </div>

          {/* Main result */}
          <div style={{ textAlign: 'center', padding: '1.5rem 0', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '0.25rem' }}>Économie mensuelle estimée</div>
            <div className="mono" style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--emerald)', lineHeight: 1.1 }}>
              <span style={{ fontSize: '1.5rem', verticalAlign: 'super' }}>€</span>{formatNum(moneySavedMonthly)}
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              soit {formatNum(moneySavedAnnual)}€ / an
            </div>
          </div>

          {/* Detail rows */}
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid rgba(30,41,59,0.4)' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Temps gagné / mois</span>
            <span className="mono" style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--emerald)' }}>{formatNum(timeSavedMonthly)} h</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid rgba(30,41,59,0.4)' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Temps gagné / document</span>
            <span className="mono" style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--emerald)' }}>-{timeSavedPerTask}h ({reductionDisplay}%)</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0', borderBottom: '1px solid rgba(30,41,59,0.4)' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Coût Cortex Leman / mois</span>
            <span className="mono" style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--amber)' }}>{formatNum(monthlyCost)}€</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem 0' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>ROI</span>
            <span className="mono" style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--emerald)' }}>{roi}×</span>
          </div>

          {/* ROI Badge */}
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              background: 'var(--emerald-dim)', border: '1px solid rgba(52,211,153,0.3)',
              color: 'var(--emerald)', padding: '0.5rem 1rem', borderRadius: '0.5rem',
              fontFamily: 'JetBrains Mono, monospace', fontSize: '1.1rem', fontWeight: 700,
            }}>
              🚀 {roi}× votre investissement
            </span>
          </div>

          {/* Breakdown bars */}
          <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border)' }}>
            <div className="mono" style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1rem' }}>
              Répartition du gain
            </div>
            {cfg.breakdown.map((pct, i) => (
              <div key={i} style={{ marginBottom: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{cfg.breakdownLabels[i]}</span>
                  <span style={{ color: 'var(--text)', fontWeight: 500 }}>{pct}%</span>
                </div>
                <div style={{ height: 6, background: 'rgba(30,41,59,0.6)', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${pct}%`, background: BAR_COLORS[i], borderRadius: 3, transition: 'width 0.5s ease-out' }} />
                </div>
              </div>
            ))}
          </div>

          {/* Trust note */}
          <div style={{
            marginTop: '1.5rem', padding: '1rem',
            background: 'var(--cyan-dim)', border: '1px solid rgba(34,211,238,0.2)',
            borderRadius: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5,
          }}>
            <strong style={{ color: 'var(--cyan)' }}>🔒 Conformité garantie.</strong> Chaque document est tracé dans un journal inviolable (SHA-256), vérifié par le Trust Box (0% LLM, 100% déterministe), et validé par arbitrage humain si nécessaire.
          </div>
        </div>
      </div>

      {/* BANT Gate — Email capture overlay (Isabella pattern: $180K from lead magnets) */}
      {showGate && !gateSubmitted && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 100,
          background: 'rgba(2,6,23,0.85)', backdropFilter: 'blur(8px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem',
        }}>
          <div className="glass" style={{ maxWidth: 480, width: '100%', padding: '2.5rem', position: 'relative' }}>
            <button onClick={() => setShowGate(false)} style={{
              position: 'absolute', top: '1rem', right: '1rem',
              background: 'none', border: 'none', color: 'var(--text-dim)',
              cursor: 'pointer', fontSize: '1.25rem',
            }}>✕</button>

            <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>
                Recevez votre rapport ROI personnalisé
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                + Benchmark vs votre vertical • Plan d\'action 90 jours
              </p>
            </div>

            <div style={{ marginBottom: '0.75rem' }}>
              <input type="text" value={gateCompany} onChange={e => setGateCompany(e.target.value)}
                placeholder="Nom du cabinet"
                style={{ width: '100%', padding: '0.75rem 1rem', fontSize: '0.9rem', background: 'rgba(15,23,42,0.6)', border: '1px solid var(--border)', borderRadius: '0.5rem', color: 'var(--text)', outline: 'none', fontFamily: 'inherit' }}
              />
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <input type="email" value={gateEmail} onChange={e => setGateEmail(e.target.value)}
                placeholder="Email professionnel"
                style={{ width: '100%', padding: '0.75rem 1rem', fontSize: '0.9rem', background: 'rgba(15,23,42,0.6)', border: '1px solid var(--border)', borderRadius: '0.5rem', color: 'var(--text)', outline: 'none', fontFamily: 'inherit' }}
              />
            </div>

            {/* BANT questions */}
            {BANT_QUESTIONS.map(q => (
              <div key={q.id} style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '0.5rem' }}>{q.label}</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  {q.options.map(opt => (
                    <button key={opt.value} onClick={() => setGateAnswers(prev => ({ ...prev, [q.id]: opt.value }))}
                      style={{
                        padding: '0.5rem', fontSize: '0.75rem', fontWeight: 500,
                        background: gateAnswers[q.id] === opt.value ? 'var(--cyan-dim)' : 'transparent',
                        border: `1px solid ${gateAnswers[q.id] === opt.value ? 'var(--cyan)' : 'var(--border)'}`,
                        borderRadius: '0.5rem', color: gateAnswers[q.id] === opt.value ? 'var(--cyan)' : 'var(--text-muted)',
                        cursor: 'pointer', transition: 'all 0.15s', fontFamily: 'inherit',
                      }}
                    >{opt.label}</button>
                  ))}
                </div>
              </div>
            ))}

            <button onClick={handleGateSubmit} disabled={!gateEmail}
              style={{
                width: '100%', padding: '0.875rem', fontSize: '1rem', fontWeight: 700,
                background: gateEmail ? 'var(--emerald)' : 'var(--border)',
                color: gateEmail ? '#0f172a' : 'var(--text-dim)',
                border: 'none', borderRadius: '0.75rem', cursor: gateEmail ? 'pointer' : 'default',
                fontFamily: 'inherit',
              }}
            >
              → Obtenir mon rapport gratuit
            </button>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', textAlign: 'center', marginTop: '0.5rem' }}>
              🔒 Conforme RGPD • Jamais revendu • Désabonnement en 1 clic
            </div>
          </div>
        </div>
      )}

      {gateSubmitted && (
        <div style={{
          maxWidth: 700, margin: '1.5rem auto 0', textAlign: 'center',
          background: 'rgba(52,211,153,0.06)', border: '1px solid rgba(52,211,153,0.2)',
          borderRadius: '0.75rem', padding: '1rem', fontSize: '0.85rem', color: 'var(--emerald)',
        }}>
          ✅ Rapport envoyé à <strong>{gateEmail}</strong> — Vérifiez votre boîte mail !
        </div>
      )}

      {/* CTA */}
      <div style={{
        maxWidth: 700, margin: '3rem auto 0', textAlign: 'center',
        background: 'linear-gradient(135deg, rgba(34,211,238,0.08), rgba(52,211,153,0.08))',
        border: '1px solid rgba(34,211,238,0.2)', borderRadius: '1rem', padding: '2.5rem',
      }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Prêt à transformer votre cabinet ?</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>Essai gratuit 7 jours. Audit offert. Aucune carte bancaire requise.</p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button onClick={() => onCta?.()} className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem', border: 'none', cursor: 'pointer' }}>
            → Essai gratuit 7 jours
          </button>
          <a href="#demo" className="btn btn-secondary" style={{ padding: '0.75rem 1.5rem', fontSize: '0.9rem', textDecoration: 'none' }}>
            Demander une démo
          </a>
        </div>
      </div>

      {/* Mobile responsive */}
      <style>{`
        @media (max-width: 768px) {
          #roi-calculator > div:first-of-type + div {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </section>
  )
}
