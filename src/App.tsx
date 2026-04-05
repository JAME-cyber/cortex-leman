import { useState, useEffect, useRef } from 'react'

// ─── Types ────────────────────────────────────────────────────────────────────
interface NavItem { label: string; href: string }
interface Service { id: string; title: string; sub: string; tags: string[] }
interface Offer { name: string; price: string; delay: string; items: string[]; accent: boolean }
interface Pole { label: string; agents: string[]; color: string }

// ─── Data ─────────────────────────────────────────────────────────────────────
const NAV: NavItem[] = [
  { label: 'Services', href: '#services' },
  { label: 'Architecture', href: '#architecture' },
  { label: 'Tarifs', href: '#tarifs' },
  { label: 'Contact', href: '#contact' },
]

const SERVICES: Service[] = [
  {
    id: '01',
    title: 'Audit de Conformité',
    sub: 'Transfrontalier France · Suisse',
    tags: ['nLPD', 'RGPD', 'TVA CH/FR', 'Établissement stable'],
  },
  {
    id: '02',
    title: 'Évaluation Business',
    sub: 'Décision d\'investissement',
    tags: ['Score pondéré', 'TAM/SAM/SOM', 'Plan 90j', 'Go/No-Go'],
  },
  {
    id: '03',
    title: 'Veille Stratégique',
    sub: 'Intelligence de marché',
    tags: ['Grand Genève', 'Concurrence', 'Tendances', 'Signaux faibles'],
  },
  {
    id: '04',
    title: 'Agents 24/7',
    sub: 'Opérations autonomes',
    tags: ['Marketing', 'Service client', 'Sécurité', 'Reporting'],
  },
]

const POLES: Pole[] = [
  { label: 'Intelligence', agents: ['Researcher', 'Archivist', 'Scraper', 'Analyst'], color: '#3b82f6' },
  { label: 'Compliance', agents: ['Auditor', 'Risk Analyzer', 'Cost Optimizer', 'Quality Gate'], color: '#10b981' },
  { label: 'Factory', agents: ['Doc Builder', 'Code Gen', 'QA Tester', 'Deployer'], color: '#F59E0B' },
  { label: 'Creative', agents: ['Designer', 'Writer', 'Video', 'Audio'], color: '#A78BFA' },
  { label: 'Business', agents: ['Evaluator', 'Forecaster', 'Negotiator', 'Growth'], color: '#FB7185' },
]

const OFFERS: Offer[] = [
  {
    name: 'Audit Express',
    price: '490',
    delay: '< 48h',
    items: ['1 cas simple', 'Rapport structuré JSON', 'Règles TAX + DATA', 'Truth Node validé'],
    accent: false,
  },
  {
    name: 'Audit Standard',
    price: '990',
    delay: '3–5 jours',
    items: ['Cas complexe multi-entités', 'Rapport PDF complet', 'Recommandations priorisées', 'Call de restitution 30 min'],
    accent: true,
  },
  {
    name: 'Audit Stratégique',
    price: '2 490',
    delay: '1–2 semaines',
    items: ['Structures multi-entités', 'Plan d\'action 90 jours', 'Monitoring mensuel', 'Accès agents 24/7'],
    accent: false,
  },
]

const STACK = ['CrewAI', 'LangGraph', 'FastAPI', 'OpenRouter', 'GLM-4V', 'n8n', 'PostgreSQL', 'Langfuse']

// ─── Hooks ────────────────────────────────────────────────────────────────────
function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true) }, { threshold })
    if (ref.current) obs.observe(ref.current)
    return () => obs.disconnect()
  }, [threshold])
  return { ref, visible }
}

// ─── Components ───────────────────────────────────────────────────────────────
function Nav() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)
  useEffect(() => {
    const h = () => setScrolled(window.scrollY > 40)
    window.addEventListener('scroll', h)
    return () => window.removeEventListener('scroll', h)
  }, [])
  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: scrolled ? 'rgba(13,17,23,0.92)' : 'transparent',
      backdropFilter: scrolled ? 'blur(12px)' : 'none',
      borderBottom: scrolled ? '1px solid rgba(255,255,255,0.06)' : 'none',
      transition: 'all 0.3s ease',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <a href="#" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, background: 'linear-gradient(135deg, #3b82f6, #10b981)',
            borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 14, fontWeight: 700, color: '#0d1117',
          }}>CL</div>
          <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: 18, color: '#f0f2f5', letterSpacing: '-0.3px' }}>
            Cortex <span style={{ color: '#3b82f6' }}>Léman</span>
          </span>
        </a>
        <div style={{ display: 'flex', gap: 32, alignItems: 'center' }} className="nav-desktop">
          {NAV.map(n => (
            <a key={n.href} href={n.href} style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 14, color: 'rgba(240,242,245,0.6)', textDecoration: 'none', transition: 'color 0.2s' }}
              onMouseEnter={e => (e.currentTarget.style.color = '#f0f2f5')}
              onMouseLeave={e => (e.currentTarget.style.color = 'rgba(240,242,245,0.6)')}>
              {n.label}
            </a>
          ))}
          <a href="#contact" style={{
            fontFamily: 'DM Sans, sans-serif', fontSize: 13, fontWeight: 500,
            padding: '8px 18px', borderRadius: 8, textDecoration: 'none',
            background: 'rgba(75,158,255,0.12)', color: '#3b82f6',
            border: '1px solid rgba(75,158,255,0.3)', transition: 'all 0.2s',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(75,158,255,0.2)'; e.currentTarget.style.borderColor = '#3b82f6' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(75,158,255,0.12)'; e.currentTarget.style.borderColor = 'rgba(75,158,255,0.3)' }}>
            Démarrer un audit
          </a>
        </div>
        <button onClick={() => setOpen(!open)} style={{ display: 'none', background: 'none', border: 'none', color: '#f0f2f5', cursor: 'pointer', fontSize: 22 }} className="nav-burger">☰</button>
      </div>
      {open && (
        <div style={{ background: '#0f1014', borderTop: '1px solid rgba(255,255,255,0.06)', padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {NAV.map(n => <a key={n.href} href={n.href} onClick={() => setOpen(false)} style={{ color: 'rgba(240,242,245,0.7)', textDecoration: 'none', fontFamily: 'DM Sans, sans-serif', fontSize: 15 }}>{n.label}</a>)}
        </div>
      )}
    </nav>
  )
}

function Hero() {
  return (
    <section style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '120px 24px 80px', position: 'relative', overflow: 'hidden' }}>
      {/* Grid background */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 0,
        backgroundImage: 'linear-gradient(rgba(75,158,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(75,158,255,0.04) 1px, transparent 1px)',
        backgroundSize: '48px 48px',
      }} />
      {/* Glow */}
      <div style={{ position: 'absolute', top: '20%', left: '50%', transform: 'translate(-50%,-50%)', width: 600, height: 600, background: 'radial-gradient(circle, rgba(75,158,255,0.08) 0%, transparent 70%)', zIndex: 0 }} />

      <div style={{ maxWidth: 1200, margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 14px', borderRadius: 100, background: 'rgba(75,158,255,0.08)', border: '1px solid rgba(75,158,255,0.2)', marginBottom: 32 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981', animation: 'pulse 2s infinite' }} />
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 12, color: 'rgba(75,158,255,0.9)', letterSpacing: '0.08em' }}>22 agents · Grand Genève</span>
        </div>

        <h1 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(42px, 7vw, 88px)', fontWeight: 800, lineHeight: 1.0, color: '#f0f2f5', margin: '0 0 24px', letterSpacing: '-2px' }}>
          L'intelligence<br />
          <span style={{ color: '#3b82f6' }}>asymétrique</span><br />
          au service de<br />
          <span style={{ WebkitTextStroke: '1px rgba(240,242,245,0.3)', color: 'transparent' }}>vos décisions.</span>
        </h1>

        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 18, color: 'rgba(240,242,245,0.55)', maxWidth: 520, lineHeight: 1.7, margin: '0 0 48px' }}>
          Audits de conformité France–Suisse, évaluation business et orchestration de 22 agents IA. Résultats en 48h. Responsabilité humaine garantie.
        </p>

        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <a href="#contact" style={{
            fontFamily: 'DM Sans, sans-serif', fontWeight: 600, fontSize: 15,
            padding: '14px 28px', borderRadius: 10, textDecoration: 'none',
            background: '#3b82f6', color: '#0d1117', transition: 'all 0.2s',
          }}
            onMouseEnter={e => e.currentTarget.style.background = '#6DB3FF'}
            onMouseLeave={e => e.currentTarget.style.background = '#3b82f6'}>
            Démarrer un audit →
          </a>
          <a href="#architecture" style={{
            fontFamily: 'DM Sans, sans-serif', fontSize: 15,
            padding: '14px 28px', borderRadius: 10, textDecoration: 'none',
            background: 'rgba(255,255,255,0.05)', color: 'rgba(240,242,245,0.8)',
            border: '1px solid rgba(255,255,255,0.08)', transition: 'all 0.2s',
          }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.08)'}
            onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}>
            Voir l'architecture
          </a>
        </div>

        {/* Stats row */}
        <div style={{ display: 'flex', gap: 48, marginTop: 80, paddingTop: 48, borderTop: '1px solid rgba(255,255,255,0.06)', flexWrap: 'wrap' }}>
          {[['< 0.10 €', 'coût par audit IA'], ['> 99 %', 'marge brute'], ['48 h', 'délai Express'], ['22', 'agents actifs']].map(([val, lbl]) => (
            <div key={lbl}>
              <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 28, fontWeight: 800, color: '#3b82f6', letterSpacing: '-1px' }}>{val}</div>
              <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 13, color: 'rgba(240,242,245,0.4)', marginTop: 4 }}>{lbl}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Services() {
  const { ref, visible } = useInView()
  return (
    <section id="services" ref={ref} style={{ padding: '120px 24px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ marginBottom: 64 }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, letterSpacing: '0.15em', color: '#3b82f6', textTransform: 'uppercase' }}>Services</span>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(32px, 4vw, 52px)', fontWeight: 800, color: '#f0f2f5', margin: '16px 0 0', letterSpacing: '-1.5px', lineHeight: 1.1 }}>
            Quatre missions.<br />Une infrastructure.
          </h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 1, background: 'rgba(255,255,255,0.05)', borderRadius: 16, overflow: 'hidden' }}>
          {SERVICES.map((s, i) => (
            <div key={s.id} style={{
              background: '#0d1117', padding: '36px 32px',
              opacity: visible ? 1 : 0, transform: visible ? 'none' : 'translateY(20px)',
              transition: `opacity 0.5s ease ${i * 0.1}s, transform 0.5s ease ${i * 0.1}s`,
              cursor: 'default',
            }}
              onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.background = '#0d0f14' }}
              onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.background = '#0d1117' }}>
              <div style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(75,158,255,0.5)', letterSpacing: '0.1em', marginBottom: 20 }}>{s.id}</div>
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 700, color: '#f0f2f5', margin: '0 0 8px', letterSpacing: '-0.5px' }}>{s.title}</h3>
              <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 14, color: 'rgba(240,242,245,0.4)', margin: '0 0 24px' }}>{s.sub}</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {s.tags.map(t => (
                  <span key={t} style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, padding: '4px 10px', borderRadius: 6, background: 'rgba(75,158,255,0.06)', color: 'rgba(75,158,255,0.7)', border: '1px solid rgba(75,158,255,0.12)' }}>{t}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Architecture() {
  const { ref, visible } = useInView(0.1)
  const [active, setActive] = useState<string | null>(null)
  return (
    <section id="architecture" ref={ref} style={{ padding: '120px 24px', borderTop: '1px solid rgba(255,255,255,0.05)', background: 'rgba(75,158,255,0.02)' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ marginBottom: 64 }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, letterSpacing: '0.15em', color: '#10b981', textTransform: 'uppercase' }}>Architecture</span>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(32px, 4vw, 52px)', fontWeight: 800, color: '#f0f2f5', margin: '16px 0 0', letterSpacing: '-1.5px', lineHeight: 1.1 }}>
            22 agents.<br />5 pôles. 1 Truth Node.
          </h2>
          <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 16, color: 'rgba(240,242,245,0.45)', marginTop: 16, maxWidth: 520 }}>
            Chaque affirmation est validée contre la source de vérité officielle avant tout envoi externe. Aucune hallucination ne peut quitter le système.
          </p>
        </div>

        {/* Truth Node center */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 40, opacity: visible ? 1 : 0, transition: 'opacity 0.6s ease 0.2s' }}>
          <div style={{
            padding: '20px 32px', borderRadius: 12,
            background: 'rgba(52,211,153,0.06)', border: '1px solid rgba(52,211,153,0.2)',
            textAlign: 'center',
          }}>
            <div style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: '#10b981', letterSpacing: '0.12em', marginBottom: 6 }}>TRUTH NODE — RAG CENTRAL</div>
            <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 14, color: 'rgba(240,242,245,0.5)' }}>Compliance Matrix · Tarifs officiels · CGV · Règles interdites</div>
          </div>
        </div>

        {/* Poles grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
          {POLES.map((pole, i) => (
            <div key={pole.label}
              onClick={() => setActive(active === pole.label ? null : pole.label)}
              style={{
                borderRadius: 12, border: `1px solid ${active === pole.label ? pole.color + '50' : 'rgba(255,255,255,0.06)'}`,
                background: active === pole.label ? pole.color + '08' : 'rgba(255,255,255,0.02)',
                padding: '20px', cursor: 'pointer', transition: 'all 0.25s ease',
                opacity: visible ? 1 : 0, transform: visible ? 'none' : 'translateY(24px)',
                transitionDelay: `${0.1 + i * 0.08}s`,
              }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: pole.color }} />
                <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 15, fontWeight: 700, color: '#f0f2f5' }}>{pole.label}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {pole.agents.map(a => (
                  <div key={a} style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(240,242,245,0.35)', padding: '4px 8px', borderRadius: 4, background: 'rgba(255,255,255,0.03)' }}>{a}</div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Stack badges */}
        <div style={{ marginTop: 48, padding: '24px 0', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(240,242,245,0.3)', letterSpacing: '0.1em', marginBottom: 16 }}>STACK DE PRODUCTION</div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {STACK.map(s => (
              <span key={s} style={{ fontFamily: 'DM Mono, monospace', fontSize: 12, padding: '6px 12px', borderRadius: 6, background: 'rgba(255,255,255,0.04)', color: 'rgba(240,242,245,0.5)', border: '1px solid rgba(255,255,255,0.06)' }}>{s}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

function HowItWorks() {
  const { ref, visible } = useInView()
  const steps = [
    { n: '01', title: 'Soumission', desc: 'Formulaire ou API. Vous décrivez votre situation transfrontalière en langage naturel.' },
    { n: '02', title: 'Orchestration', desc: 'Le Harness active les agents Compliance et Research. Chaque output passe par le Truth Node.' },
    { n: '03', title: 'Validation humaine', desc: 'Un expert humain valide le rapport avant livraison. Sa signature, votre décision.' },
    { n: '04', title: 'Livrable PDF', desc: 'Rapport structuré avec ID règles, statuts, preuves et recommandations priorisées.' },
  ]
  return (
    <section style={{ padding: '120px 24px', borderTop: '1px solid rgba(255,255,255,0.05)' }} ref={ref}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ marginBottom: 64 }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, letterSpacing: '0.15em', color: '#F59E0B', textTransform: 'uppercase' }}>Processus</span>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(32px, 4vw, 52px)', fontWeight: 800, color: '#f0f2f5', margin: '16px 0 0', letterSpacing: '-1.5px' }}>
            De la question<br />à la décision.
          </h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 32 }}>
          {steps.map((s, i) => (
            <div key={s.n} style={{ opacity: visible ? 1 : 0, transform: visible ? 'none' : 'translateY(20px)', transition: `all 0.5s ease ${i * 0.12}s` }}>
              <div style={{ fontFamily: 'Syne, sans-serif', fontSize: 42, fontWeight: 800, color: 'rgba(240,242,245,0.06)', letterSpacing: '-2px', marginBottom: 16 }}>{s.n}</div>
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 20, fontWeight: 700, color: '#f0f2f5', margin: '0 0 12px' }}>{s.title}</h3>
              <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 15, color: 'rgba(240,242,245,0.45)', lineHeight: 1.7, margin: 0 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Pricing() {
  const { ref, visible } = useInView()
  return (
    <section id="tarifs" ref={ref} style={{ padding: '120px 24px', borderTop: '1px solid rgba(255,255,255,0.05)', background: 'rgba(75,158,255,0.02)' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ marginBottom: 64 }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, letterSpacing: '0.15em', color: '#A78BFA', textTransform: 'uppercase' }}>Tarifs</span>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(32px, 4vw, 52px)', fontWeight: 800, color: '#f0f2f5', margin: '16px 0 0', letterSpacing: '-1.5px' }}>
            Prix fixe.<br />Transparence totale.
          </h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          {OFFERS.map((o, i) => (
            <div key={o.name} style={{
              borderRadius: 16,
              border: o.accent ? '1px solid rgba(75,158,255,0.4)' : '1px solid rgba(255,255,255,0.06)',
              background: o.accent ? 'rgba(75,158,255,0.05)' : 'rgba(255,255,255,0.02)',
              padding: '36px 32px', position: 'relative', overflow: 'hidden',
              opacity: visible ? 1 : 0, transform: visible ? 'none' : 'translateY(24px)',
              transition: `all 0.5s ease ${i * 0.12}s`,
            }}>
              {o.accent && (
                <div style={{ position: 'absolute', top: 16, right: 16, fontFamily: 'DM Mono, monospace', fontSize: 10, padding: '4px 10px', borderRadius: 100, background: '#3b82f6', color: '#0d1117', letterSpacing: '0.08em' }}>POPULAIRE</div>
              )}
              <div style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(240,242,245,0.4)', letterSpacing: '0.1em', marginBottom: 16 }}>{o.delay}</div>
              <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, fontWeight: 700, color: '#f0f2f5', margin: '0 0 8px' }}>{o.name}</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, margin: '20px 0 28px' }}>
                <span style={{ fontFamily: 'Syne, sans-serif', fontSize: 44, fontWeight: 800, color: o.accent ? '#3b82f6' : '#f0f2f5', letterSpacing: '-2px' }}>{o.price}</span>
                <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 16, color: 'rgba(240,242,245,0.4)' }}>€ HT</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 32 }}>
                {o.items.map(it => (
                  <div key={it} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                    <span style={{ color: o.accent ? '#3b82f6' : '#10b981', flexShrink: 0, marginTop: 2 }}>✓</span>
                    <span style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 14, color: 'rgba(240,242,245,0.6)' }}>{it}</span>
                  </div>
                ))}
              </div>
              <a href="#contact" style={{
                display: 'block', textAlign: 'center', padding: '12px',
                borderRadius: 8, textDecoration: 'none', fontFamily: 'DM Sans, sans-serif', fontSize: 14, fontWeight: 600,
                background: o.accent ? '#3b82f6' : 'rgba(255,255,255,0.06)',
                color: o.accent ? '#0d1117' : '#f0f2f5',
                border: o.accent ? 'none' : '1px solid rgba(255,255,255,0.08)',
                transition: 'all 0.2s',
              }}>Démarrer →</a>
            </div>
          ))}
        </div>
        <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 13, color: 'rgba(240,242,245,0.3)', textAlign: 'center', marginTop: 32 }}>
          Aide à la décision uniquement · Validation humaine incluse · Non substituable à un conseil juridique certifié
        </p>
      </div>
    </section>
  )
}

function Contact() {
  const [form, setForm] = useState({ name: '', email: '', situation: '', budget: 'express' })
  const [sent, setSent] = useState(false)
  const handle = (e: React.FormEvent) => {
    e.preventDefault()
    setSent(true)
  }
  return (
    <section id="contact" style={{ padding: '120px 24px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
      <div style={{ maxWidth: 640, margin: '0 auto' }}>
        <div style={{ marginBottom: 48 }}>
          <span style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, letterSpacing: '0.15em', color: '#FB7185', textTransform: 'uppercase' }}>Contact</span>
          <h2 style={{ fontFamily: 'Syne, sans-serif', fontSize: 'clamp(32px, 4vw, 48px)', fontWeight: 800, color: '#f0f2f5', margin: '16px 0 0', letterSpacing: '-1.5px' }}>
            Démarrer un audit.
          </h2>
        </div>
        {sent ? (
          <div style={{ padding: 40, borderRadius: 16, background: 'rgba(52,211,153,0.06)', border: '1px solid rgba(52,211,153,0.2)', textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 16 }}>✓</div>
            <h3 style={{ fontFamily: 'Syne, sans-serif', fontSize: 22, color: '#10b981', margin: '0 0 8px' }}>Demande reçue</h3>
            <p style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 15, color: 'rgba(240,242,245,0.5)', margin: 0 }}>Vous recevrez une réponse sous 4h ouvrées.</p>
          </div>
        ) : (
          <form onSubmit={handle} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {[
              { key: 'name', label: 'Nom / Entreprise', type: 'text', placeholder: 'TechSolutions Annemasse' },
              { key: 'email', label: 'Email', type: 'email', placeholder: 'contact@votre-entreprise.fr' },
            ].map(f => (
              <div key={f.key}>
                <label style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(240,242,245,0.4)', letterSpacing: '0.1em', display: 'block', marginBottom: 8 }}>{f.label.toUpperCase()}</label>
                <input type={f.type} required placeholder={f.placeholder}
                  value={form[f.key as keyof typeof form]}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  style={{ width: '100%', padding: '12px 16px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.03)', color: '#f0f2f5', fontFamily: 'DM Sans, sans-serif', fontSize: 14, outline: 'none', boxSizing: 'border-box' }} />
              </div>
            ))}
            <div>
              <label style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(240,242,245,0.4)', letterSpacing: '0.1em', display: 'block', marginBottom: 8 }}>VOTRE SITUATION</label>
              <textarea required placeholder="Entreprise à Annemasse, client à Genève. Serveurs OVH France. Question de TVA et nLPD..."
                value={form.situation} onChange={e => setForm({ ...form, situation: e.target.value })}
                rows={4}
                style={{ width: '100%', padding: '12px 16px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(255,255,255,0.03)', color: '#f0f2f5', fontFamily: 'DM Sans, sans-serif', fontSize: 14, resize: 'vertical', outline: 'none', boxSizing: 'border-box' }} />
            </div>
            <div>
              <label style={{ fontFamily: 'DM Mono, monospace', fontSize: 11, color: 'rgba(240,242,245,0.4)', letterSpacing: '0.1em', display: 'block', marginBottom: 8 }}>FORMULE</label>
              <select value={form.budget} onChange={e => setForm({ ...form, budget: e.target.value })}
                style={{ width: '100%', padding: '12px 16px', borderRadius: 8, border: '1px solid rgba(255,255,255,0.08)', background: '#0f1014', color: '#f0f2f5', fontFamily: 'DM Sans, sans-serif', fontSize: 14, outline: 'none', boxSizing: 'border-box' }}>
                <option value="express">Audit Express — 490 € / 48h</option>
                <option value="standard">Audit Standard — 990 € / 3-5j</option>
                <option value="strategique">Audit Stratégique — 2 490 €</option>
              </select>
            </div>
            <button type="submit" style={{
              padding: '14px', borderRadius: 10, border: 'none', cursor: 'pointer',
              background: '#3b82f6', color: '#0d1117', fontFamily: 'DM Sans, sans-serif', fontSize: 15, fontWeight: 700, marginTop: 8, transition: 'background 0.2s',
            }}
              onMouseEnter={e => e.currentTarget.style.background = '#6DB3FF'}
              onMouseLeave={e => e.currentTarget.style.background = '#3b82f6'}>
              Envoyer la demande d'audit →
            </button>
          </form>
        )}
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer style={{ borderTop: '1px solid rgba(255,255,255,0.05)', padding: '40px 24px' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
        <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: 16, color: '#3b82f6' }}>Cortex Léman</div>
        <div style={{ fontFamily: 'DM Sans, sans-serif', fontSize: 13, color: 'rgba(240,242,245,0.25)' }}>
          Aide à la décision · Non substituable à un conseil certifié · Grand Genève © 2026
        </div>
      </div>
    </footer>
  )
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body { background: #0d1117; color: #f1f5f9; }
        ::selection { background: rgba(75,158,255,0.3); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0d1117; }
        ::-webkit-scrollbar-thumb { background: rgba(75,158,255,0.3); border-radius: 3px; }
        input::placeholder, textarea::placeholder { color: rgba(240,242,245,0.2); }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.3; } }
        @media (max-width: 768px) {
          .nav-desktop { display: none !important; }
          .nav-burger { display: block !important; }
        }
      `}</style>
      <Nav />
      <main>
        <Hero />
        <Services />
        <Architecture />
        <HowItWorks />
        <Pricing />
        <Contact />
      </main>
      <Footer />
    </>
  )
}