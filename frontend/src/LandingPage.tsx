import { useState, useEffect } from 'react'
import { MarketSection } from './components/MarketSection'
import { AgentFlowAnimation } from './components/AgentFlowAnimation'
import { VerticalDemoResult } from './components/VerticalDemoResult'
import { ROICalculator } from './components/ROICalculator'
import { ExcellenceScore } from './components/ExcellenceScore'

/* ═══════════════════════════════════════════════════════════
   CORTEX LEMAN V5 — Landing Page
   Design: Dark navy + Cyan (existants)
   Inspiré de: Aura.build SaaS patterns
   Sections: Navbar → Hero → Trust → Features → Verticals →
             Architecture → Compliance → Stats → CTA → Footer
   ═══════════════════════════════════════════════════════════ */

// ── Constants ──────────────────────────────────────────────
const VERTICALS = [
  { id: 'comptable', icon: '📊', label: 'Expert-Comptable', color: '#22d3ee', desc: 'TVA, seuils, AFC, plan comptable' },
  { id: 'avocat',    icon: '⚖️',  label: 'Avocat',          color: '#a78bfa', desc: 'Secret professionnel Art. 321 CP' },
  { id: 'sante',     icon: '🏥',  label: 'Santé',           color: '#34d399', desc: 'LPM, HDS, consentement éclairé' },
  { id: 'banque',    icon: '🏦',  label: 'Banque',          color: '#fbbf24', desc: 'Secret bancaire Art. 47 LB, KYC' },
  { id: 'startup',   icon: '🚀',  label: 'Startup',         color: '#fb923c', desc: 'DPIA, AI Act, RGPD' },
  { id: 'rh',        icon: '👥',  label: 'Ressources Humaines', color: '#fb7185', desc: 'Anti-discrimination, Art. 22 RGPD' },
]

const FEATURES = [
  { icon: '🛡️', title: 'Médiateur Déterministe', desc: '18 règles JsonLogic — 0% LLM, 100% prédictible. Gel préventif automatique.', badge: 'Jamais de LLM', badgeColor: 'cyan' },
  { icon: '📝', title: 'Journal WORM', desc: 'Hash-chain SHA-256, HMAC-signé. Append-only, vérifiable, conforme RGPD Art. 30.', badge: 'Audit Trail', badgeColor: 'emerald' },
  { icon: '⚖️', title: 'Arbitrage Humain', desc: 'Dashboard de contradictions. L\'humain est arbitre, pas validateur.', badge: 'Human-in-the-loop', badgeColor: 'violet' },
  { icon: '🔒', title: 'Chiffrement Fernet', desc: 'PII chiffrée au repos. AES-128-CBC + HMAC-SHA256. Rotation de clés.', badge: 'At-rest', badgeColor: 'amber' },
  { icon: '🔍', title: 'RAG Réglementaire', desc: '20 textes vectorisés (ChromaDB). Références RGPD, AI Act, CP 321, LB 47.', badge: 'Vector Search', badgeColor: 'cyan' },
  { icon: '🤖', title: 'Guardrails LLM', desc: 'PII detection + Topic control + Output safety. Pipeline de protection complet.', badge: '3 couches', badgeColor: 'rose' },
]

const STATS = [
  { value: '384', label: 'Tests automatisés', color: 'cyan' },
  { value: '18',  label: 'Règles JsonLogic',  color: 'emerald' },
  { value: '76',  label: 'Endpoints API',     color: 'violet' },
  { value: '6',   label: 'Verticales métier', color: 'amber' },
  { value: '16',  label: 'Docs réglementaires', color: 'rose' },
]

// ── Navbar ─────────────────────────────────────────────────
function Navbar({ onLogin, onStartOnboarding }: { onLogin?: () => void; onStartOnboarding?: () => void }) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
      background: scrolled ? 'rgba(2,6,23,0.92)' : 'transparent',
      backdropFilter: scrolled ? 'blur(12px)' : 'none',
      borderBottom: scrolled ? '1px solid var(--border)' : '1px solid transparent',
      transition: 'all 0.3s ease',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0.875rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 32, height: 32, borderRadius: '0.5rem', background: 'linear-gradient(135deg, var(--cyan), var(--emerald))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', fontWeight: 700 }}>CL</div>
          <span className="mono" style={{ fontSize: '0.875rem', fontWeight: 700, letterSpacing: '-0.025em' }}>Cortex Leman</span>
          <span className="badge badge-cyan" style={{ fontSize: '0.625rem' }}>v5</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <a href="#roi-calculator" onClick={e => { e.preventDefault(); document.getElementById('roi-calculator')?.scrollIntoView({ behavior: 'smooth' }) }} style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500, textDecoration: 'none' }}>ROI</a>
          <a href="#excellence-score" onClick={e => { e.preventDefault(); document.getElementById('excellence-score')?.scrollIntoView({ behavior: 'smooth' }) }} style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500, textDecoration: 'none' }}>Score</a>
          <a href="#features" onClick={e => { e.preventDefault(); document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' }) }} style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500, textDecoration: 'none' }}>Fonctionnalités</a>
          <a href="#verticals" onClick={e => { e.preventDefault(); document.getElementById('verticals')?.scrollIntoView({ behavior: 'smooth' }) }} style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500, textDecoration: 'none' }}>Verticales</a>
          <a href="#compliance" onClick={e => { e.preventDefault(); document.getElementById('compliance')?.scrollIntoView({ behavior: 'smooth' }) }} style={{ color: 'var(--text-muted)', fontSize: '0.8125rem', fontWeight: 500, textDecoration: 'none' }}>Conformité</a>
          <button onClick={() => onLogin?.()} style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-muted)', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: 500 }}>Se connecter</button>
          <button onClick={() => onStartOnboarding?.()} className="btn btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem', border: 'none', cursor: 'pointer' }}>Essai gratuit →</button>
        </div>
      </div>
    </nav>
  )
}

// ── Hero Section (Aura-inspired centered with glow) ────────
function HeroSection({ onStartOnboarding }: { onStartOnboarding?: () => void }) {
  return (
    <section style={{ position: 'relative', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
      {/* Glow orbs */}
      <div className="glow-orb cyan" style={{ top: '10%', left: '20%' }} />
      <div className="glow-orb violet" style={{ top: '30%', right: '15%' }} />
      <div className="glow-orb emerald" style={{ bottom: '10%', left: '40%' }} />

      <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', maxWidth: 800, padding: '0 1.5rem' }}>
        {/* Badge */}
        <div style={{ marginBottom: '1.5rem' }}>
          <span className="badge badge-cyan"> AI Compliance Infrastructure — Professions Régulées FR-CH </span>
        </div>

        {/* Title */}
        <h1 className="hero-title" style={{ fontSize: '3.5rem', fontWeight: 800, lineHeight: 1.1, letterSpacing: '-0.035em', marginBottom: '1.5rem' }}>
          Infrastructure de
          <br />
          <span style={{ background: 'linear-gradient(135deg, var(--cyan), var(--emerald))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Conformité IA
          </span>
        </h1>

        {/* Subtitle */}
        <p style={{ fontSize: '1.125rem', color: 'var(--text-muted)', maxWidth: 620, margin: '0 auto 2rem', lineHeight: 1.7 }}>
          Conformité RGPD, AI Act, secret professionnel FR-CH.
          6 agents spécialisés, 18 règles réglementaires, journal d'audit inviolable.
        </p>

        {/* CTA Buttons */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button onClick={() => onStartOnboarding?.()} className="btn btn-primary" style={{ padding: '0.875rem 2rem', fontSize: '0.9375rem' }}>
            Audit gratuit 5 min →
          </button>
          <a href="#architecture" className="btn btn-secondary" style={{ padding: '0.875rem 2rem', fontSize: '0.9375rem' }}>
            Voir l'architecture
          </a>
        </div>

        {/* Trust line */}
        <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '1.5rem' }}>
          Gratuit · Sans carte bancaire · Déployé en 5 minutes
        </p>

        {/* Mini stats */}
        <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', marginTop: '3rem', flexWrap: 'wrap' }}>
          {STATS.map((s, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{ fontSize: '1.5rem', color: `var(--${s.color})` }}>{s.value}</div>
              <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ── Trust Marquee (Aura-inspired logos bar) ─────────────────
function TrustMarquee() {
  const items = ['RGPD ✓', 'AI Act ✓', 'Art. 321 CP ✓', 'Art. 47 LB ✓', 'LPM ✓', 'nLPD ✓', 'Bâle III ✓', 'HDS ✓', 'RGAA ✓', 'FINMA ✓']
  return (
    <div style={{ borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', padding: '1rem 0', overflow: 'hidden' }}>
      <div className="marquee-mask">
        <div className="animate-marquee" style={{ display: 'flex', gap: '3rem', width: 'max-content' }}>
          {[...items, ...items].map((item, i) => (
            <span key={i} className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: 500, whiteSpace: 'nowrap' }}>
              {item}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Features Grid (Aura-inspired bento cards) ──────────────
function FeaturesSection() {
  return (
    <section id="features" className="section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-emerald" style={{ marginBottom: '1rem' }}>Fonctionnalités</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Conçu pour les professions régulées
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 550, margin: '0 auto' }}>
          Chaque composant est pensé pour la conformité, la traçabilité et l'auditabilité.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem' }}>
        {FEATURES.map((f, i) => (
          <div key={i} className="glass feature-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
              <span style={{ fontSize: '1.5rem' }}>{f.icon}</span>
              <span className={`badge badge-${f.badgeColor}`}>{f.badge}</span>
            </div>
            <h3 className="mono" style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.5rem' }}>{f.title}</h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── Verticals (Aura-inspired card grid with icons) ─────────
function VerticalsSection() {
  return (
    <section id="verticals" className="section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-violet" style={{ marginBottom: '1rem' }}>6 Verticales</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Une réglementation par vertical
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 550, margin: '0 auto' }}>
          Chaque métier a ses règles. Cortex Leman les encode en JsonLogic déterministe.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
        {VERTICALS.map((v, i) => (
          <div key={i} className="glass" style={{ padding: '1.25rem', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s' }}
               onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.borderColor = v.color + '40'; (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-2px)' }}
               onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.borderColor = ''; (e.currentTarget as HTMLDivElement).style.transform = '' }}>
            <div className="vertical-icon" style={{ margin: '0 auto 0.75rem', background: v.color + '15', border: `1px solid ${v.color}25` }}>
              <span>{v.icon}</span>
            </div>
            <h3 className="mono" style={{ fontSize: '0.8125rem', fontWeight: 600, marginBottom: '0.375rem' }}>{v.label}</h3>
            <p style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>{v.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── Architecture Section with Interactive Animation ────────
function ArchitectureSection() {
  return (
    <section id="architecture" className="section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-cyan" style={{ marginBottom: '1rem' }}>Architecture</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Du pipeline au graphe de confiance
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto' }}>
          3 agents LLM pour l'intelligence + 3 agents programmatiques pour la sécurité.
          Jamais de non-déterminisme dans les décisions critiques.
        </p>
      </div>

      {/* Interactive Agent Flow Animation */}
      <AgentFlowAnimation />
    </section>
  )
}

// ── Vertical Demo Result (tangible output) ─────────────────
function VerticalDemoSection() {
  return (
    <section className="section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-emerald" style={{ marginBottom: '1rem' }}>Résultat tangible</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Ce que Cortex Leman produit concrètement
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto' }}>
          Audit TVA en temps réel — Vertical <strong style={{ color: 'var(--cyan)' }}>Comptable</strong> — 7 règles JsonLogic évaluées en 2.3 secondes.
        </p>
      </div>

      <VerticalDemoResult />
    </section>
  )
}

// ── Compliance (Aura-inspired comparison table) ─────────────
function ComplianceSection() {
  const rows = [
    { feature: 'Journal d\'audit WORM', us: '✓', others: '✗' },
    { feature: 'Médiateur déterministe (0% LLM)', us: '✓', others: '✗' },
    { feature: 'Arbitrage humain', us: '✓', others: '✗' },
    { feature: 'Gel préventif automatique', us: '✓', others: '✗' },
    { feature: 'Chiffrement PII au repos', us: '✓', others: '—' },
    { feature: 'RAG réglementaire vectorisé', us: '✓', others: '✗' },
    { feature: 'Guardrails LLM (3 couches)', us: '✓', others: '—' },
    { feature: 'Mode Haute Protection (local)', us: '✓', others: '✗' },
    { feature: 'RGPD + AI Act natifs', us: '✓', others: '—' },
    { feature: 'Secret professionnel (CP 321)', us: '✓', others: '✗' },
  ]

  return (
    <section id="compliance" className="section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-amber" style={{ marginBottom: '1rem' }}>Conformité</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Pourquoi Cortex Leman est différent
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 550, margin: '0 auto' }}>
          Les agents IA génériques ne sont pas conçus pour le réglementaire. Nous, si.
        </p>
      </div>

      <div className="glass" style={{ overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '0.75rem 1rem', background: 'rgba(30,41,59,0.5)', color: 'var(--text-muted)', fontWeight: 600, borderBottom: '1px solid var(--border)' }}>Fonctionnalité</th>
              <th style={{ padding: '0.75rem 1rem', background: 'rgba(34,211,238,0.05)', color: 'var(--cyan)', fontWeight: 700, borderBottom: '1px solid var(--border)', textAlign: 'center' }}>Cortex Leman</th>
              <th style={{ padding: '0.75rem 1rem', background: 'rgba(30,41,59,0.5)', color: 'var(--text-dim)', fontWeight: 600, borderBottom: '1px solid var(--border)', textAlign: 'center' }}>Agents génériques</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                <td className="mono" style={{ padding: '0.625rem 1rem', borderBottom: '1px solid rgba(30,41,59,0.3)', color: 'var(--text)', fontSize: '0.75rem' }}>{r.feature}</td>
                <td style={{ padding: '0.625rem 1rem', borderBottom: '1px solid rgba(30,41,59,0.3)', textAlign: 'center', color: 'var(--emerald)', fontWeight: 700, background: 'rgba(34,211,238,0.02)' }}>{r.us}</td>
                <td style={{ padding: '0.625rem 1rem', borderBottom: '1px solid rgba(30,41,59,0.3)', textAlign: 'center', color: r.others === '✗' ? 'var(--rose)' : 'var(--text-dim)' }}>{r.others}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

// ── Stats Section (Aura-inspired metric grid) ──────────────
function StatsSection() {
  const allStats = [
    { value: '384', label: 'Tests automatisés', sub: '0 échec, CI ready', color: 'cyan' },
    { value: '18', label: 'Règles JsonLogic', sub: '6 verticales × 3 règles', color: 'emerald' },
    { value: '58', label: 'Endpoints API', sub: 'REST + JWT + MCP', color: 'violet' },
    { value: '51', label: 'Docs réglementaires', sub: 'Vectorisés ChromaDB RAG', color: 'amber' },
    { value: '6', label: 'Verticales métier', sub: '+ ajout en 1 commande', color: 'rose' },
    { value: '28K+', label: 'Lignes de code', sub: 'Python + TypeScript', color: 'blue' },
  ]

  return (
    <section className="section" style={{ borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '2rem' }}>
        {allStats.map((s, i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <div className="stat-number" style={{ color: `var(--${s.color})` }}>{s.value}</div>
            <div style={{ fontSize: '0.8125rem', fontWeight: 600, marginTop: '0.25rem' }}>{s.label}</div>
            <div style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', marginTop: '0.125rem' }}>{s.sub}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── Pricing Section (Aura-inspired) ────────────────────────
function PricingSection({ onStartOnboarding }: { onStartOnboarding?: () => void }) {
  const plans = [
    {
      name: 'Starter',
      price: '0€',
      period: '/mois',
      desc: 'Développement & test',
      features: ['SQLite local', 'OpenRouter LLM', '5 utilisateurs', '3 verticals', 'Guardrails LLM', 'Journal WORM', 'MCP Tools'],
      color: 'var(--text-muted)',
      cta: 'Démarrer gratuitement',
      ctaStyle: 'btn-secondary' as const,
    },
    {
      name: 'Cabinet',
      price: '99€',
      period: '/mois',
      desc: 'Pour votre cabinet',
      features: ['PostgreSQL', 'Tous modèles LLM', 'Utilisateurs illimités', '6 verticals', 'RAG vectorisé ChromaDB', 'API Keys + MCP', 'Arbitrage humain', 'Journal WORM signé', 'Support email'],
      color: 'var(--cyan)',
      cta: 'Essai 14 jours →',
      ctaStyle: 'btn-primary' as const,
      popular: true,
    },
    {
      name: 'Haute Protection',
      price: '299€',
      period: '/mois',
      desc: 'Avocats, banques, santé',
      features: ['Ollama local (K3s)', 'Zero fuite données', 'Chiffrement Fernet', 'Data residency CH', 'Art. 321 CP / LB 47', 'FINMA ready', 'Serment numérique', 'Support prioritaire'],
      color: 'var(--violet)',
      cta: 'Nous contacter',
      ctaStyle: 'btn-secondary' as const,
    },
  ]

  return (
    <section className="section">
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-cyan" style={{ marginBottom: '1rem' }}>Tarifs</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          Gratuit pour développer, payant pour produire
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 500, margin: '0 auto' }}>
          Pas de surprise. Starter à 0€, Cabinet à 99€/mois, Haute Protection pour les sensibles.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', alignItems: 'start' }}>
        {plans.map((p, i) => (
          <div key={i} className="glass" style={{
            padding: '2rem',
            position: 'relative',
            borderColor: p.popular ? 'rgba(34,211,238,0.3)' : undefined,
          }}>
            {p.popular && (
              <div style={{ position: 'absolute', top: '-0.75rem', left: '50%', transform: 'translateX(-50%)' }}>
                <span className="badge badge-cyan">Le plus demandé</span>
              </div>
            )}
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: p.color, marginBottom: '0.5rem' }}>{p.name}</h3>
            <div style={{ marginBottom: '0.5rem' }}>
              <span className="stat-number" style={{ fontSize: '2rem' }}>{p.price}</span>
              <span style={{ color: 'var(--text-dim)', fontSize: '0.8125rem' }}>{p.period}</span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>{p.desc}</p>
            <ul style={{ listStyle: 'none', marginBottom: '1.5rem' }}>
              {p.features.map((f, j) => (
                <li key={j} style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', padding: '0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ color: 'var(--emerald)', fontSize: '0.75rem' }}>✓</span> {f}
                </li>
              ))}
            </ul>
            <button onClick={() => onStartOnboarding?.()} className={`btn ${p.ctaStyle}`} style={{ width: '100%', justifyContent: 'center' }}>
              {p.cta}
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── CTA Section ────────────────────────────────────────────
function CTASection({ onStartOnboarding }: { onStartOnboarding?: () => void }) {
  return (
    <section className="section" style={{ textAlign: 'center' }}>
      <div className="glass" style={{ padding: '3rem 2rem', position: 'relative', overflow: 'hidden' }}>
        <div className="glow-orb cyan" style={{ top: '-50%', left: '-10%' }} />
        <div className="glow-orb violet" style={{ bottom: '-50%', right: '-10%' }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
            Votre conformité IA commence maintenant
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: 500, margin: '0 auto 2rem' }}>
            Cabinet comptable, cabinet d'avocats, banque, hôpital. Démarrez en 5 minutes.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button onClick={() => onStartOnboarding?.()} className="btn btn-primary" style={{ padding: '0.875rem 2rem' }}>
              Audit gratuit 5 min →
            </button>
            <a href="/docs" className="btn btn-secondary" style={{ padding: '0.875rem 2rem' }}>
              Lire la documentation
            </a>
          </div>
        </div>
      </div>
    </section>
  )
}

// ── Footer ─────────────────────────────────────────────────
function Footer() {
  return (
    <footer style={{ borderTop: '1px solid var(--border)', padding: '3rem 1.5rem 2rem' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
          {/* Brand */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <div style={{ width: 28, height: 28, borderRadius: '0.375rem', background: 'linear-gradient(135deg, var(--cyan), var(--emerald))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700 }}>CL</div>
              <span className="mono" style={{ fontSize: '0.8125rem', fontWeight: 700 }}>Cortex Leman</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.6 }}>
              Infrastructure de confiance IA<br />pour professions régulées FR-CH
            </p>
          </div>

          {/* Produit */}
          <div>
            <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Produit</h4>
            {['Fonctionnalités', 'Verticales', 'Tarifs', 'API', 'Architecture'].map((link, i) => (
              <a key={i} href="#" style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-dim)', padding: '0.25rem 0', textDecoration: 'none' }}>{link}</a>
            ))}
          </div>

          {/* Ressources */}
          <div>
            <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Ressources</h4>
            {['Documentation', 'Guide certification', 'Guide déploiement', 'Guide produit MVP', 'Changelog'].map((link, i) => (
              <a key={i} href="#" style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-dim)', padding: '0.25rem 0', textDecoration: 'none' }}>{link}</a>
            ))}
          </div>

          {/* Conformité */}
          <div>
            <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Conformité</h4>
            {['RGPD', 'AI Act', 'Secret professionnel', 'Data residency', 'Audit WORM'].map((link, i) => (
              <a key={i} href="#" style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-dim)', padding: '0.25rem 0', textDecoration: 'none' }}>{link}</a>
            ))}
          </div>
        </div>

        <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>© 2026 Cortex Leman SA — Tous droits réservés</span>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <a href="#" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', textDecoration: 'none' }}>Mentions légales</a>
            <a href="#" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', textDecoration: 'none' }}>Politique de confidentialité</a>
            <a href="#" style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', textDecoration: 'none' }}>CGU</a>
          </div>
        </div>
      </div>
    </footer>
  )
}

// ── Main Landing Page ──────────────────────────────────────
export function LandingPage({ onLogin, onStartOnboarding }: { onLogin?: () => void; onStartOnboarding?: () => void }) {
  return (
    <>
      <div className="grid-bg" />
      <Navbar onLogin={onLogin} onStartOnboarding={onStartOnboarding} />
      <main style={{ position: 'relative', zIndex: 1 }}>
        <HeroSection onStartOnboarding={onStartOnboarding} />
        <TrustMarquee />
        <FeaturesSection />
        <VerticalsSection />
        <ArchitectureSection />
        <VerticalDemoSection />
        <ROICalculator onCta={onStartOnboarding} />
        <ExcellenceScore onCta={onStartOnboarding} />
        <ComplianceSection />
        <StatsSection />
        <MarketSection />
        <PricingSection onStartOnboarding={onStartOnboarding} />
        <CTASection onStartOnboarding={onStartOnboarding} />
      </main>
      <Footer />
    </>
  )
}
