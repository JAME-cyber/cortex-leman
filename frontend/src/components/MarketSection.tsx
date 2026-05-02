/**
 * Cortex Leman v5 — Market Positioning Section
 * Inspiré de l'analyse Accio Work (Alibaba International)
 */
export function MarketSection() {
  const comparisons = [
    { feature: 'Agents autonomes 24/7', generic: true, us: true },
    { feature: 'Bibliothèque de compétences', generic: true, us: true },
    { feature: 'Connexions tierces (ERP, APIs)', generic: true, us: true },
    { feature: 'Conformité RGPD native', generic: null, us: true },
    { feature: 'AI Act (risk management)', generic: null, us: true },
    { feature: 'Secret professionnel (CP 321)', generic: false, us: true },
    { feature: 'Secret bancaire (LB 47)', generic: false, us: true },
    { feature: "Journal d'audit WORM", generic: false, us: true },
    { feature: 'Médiateur déterministe (0% LLM)', generic: false, us: true },
    { feature: 'Arbitrage humain obligatoire', generic: false, us: true },
    { feature: 'Gel préventif automatique', generic: false, us: true },
    { feature: 'Mode hors-ligne (local)', generic: false, us: true },
    { feature: 'Data residency CH/EU', generic: false, us: true },
  ]

  const mark = (v: boolean | null) => {
    if (v === true) return <span style={{ color: 'var(--emerald)' }}>✓</span>
    if (v === false) return <span style={{ color: 'var(--rose)' }}>✗</span>
    return <span style={{ color: 'var(--text-dim)' }}>—</span>
  }

  return (
    <section className="section" style={{ background: 'linear-gradient(180deg, transparent, rgba(34,211,238,0.02), transparent)' }}>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <span className="badge badge-cyan" style={{ marginBottom: '1rem' }}>Positionnement</span>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
          {"L'IA agentique est l'avenir. La confiance l'est aussi."}
        </h2>
        <p style={{ color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto' }}>
          Des plateformes comme Accio Work (Alibaba) démocratisent l'IA agentique pour les PME.
          Mais aucune n'intègre la conformité réglementaire. Nous, si.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', maxWidth: 700, margin: '0 auto' }}>
        {/* Generic agents column */}
        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-dim)', marginBottom: '1rem' }}>
            🤖 Agents IA génériques
            <br />
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-dim)' }}>Accio Work, co-pilotes, chatbots</span>
          </h3>
          {comparisons.map((c, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between',
              padding: '0.375rem 0',
              borderBottom: '1px solid rgba(30,41,59,0.3)',
              fontSize: '0.75rem',
              color: c.generic ? 'var(--text-muted)' : 'var(--text-dim)',
            }}>
              <span>{c.feature}</span>
              {mark(c.generic)}
            </div>
          ))}
        </div>

        {/* Cortex Leman column */}
        <div style={{
          padding: '1.5rem', borderRadius: '1rem',
          border: '1px solid rgba(34,211,238,0.3)',
          background: 'rgba(34,211,238,0.03)',
        }}>
          <h3 style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--cyan)', marginBottom: '1rem' }}>
            🔒 Cortex Leman v5
            <br />
            <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>Graphe de Confiance — professions régulées</span>
          </h3>
          {comparisons.map((c, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between',
              padding: '0.375rem 0',
              borderBottom: '1px solid rgba(34,211,238,0.1)',
              fontSize: '0.75rem', color: 'var(--text-muted)',
            }}>
              <span>{c.feature}</span>
              <span style={{ color: 'var(--emerald)', fontWeight: 600 }}>✓</span>
            </div>
          ))}
        </div>
      </div>

      <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
        {"Là où les autres vous font gagner du temps, Cortex Leman vous évite les sanctions."}
      </p>
    </section>
  )
}
