import data from '../data.json'

function NodalGraph() {
  return (
    <div className="absolute inset-0 overflow-hidden opacity-20 pointer-events-none">
      <svg
        viewBox="0 0 800 500"
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] max-w-[900px]"
        fill="none"
      >
        <line
          x1="400" y1="120" x2="200" y2="320"
          stroke="#10b981"
          strokeWidth="1"
          strokeDasharray="6 4"
          className="animate-dash-flow"
        />
        <line
          x1="400" y1="120" x2="600" y2="320"
          stroke="#3b82f6"
          strokeWidth="1"
          strokeDasharray="6 4"
          className="animate-dash-flow"
        />
        <line
          x1="200" y1="320" x2="600" y2="320"
          stroke="#64748b"
          strokeWidth="0.5"
          strokeDasharray="4 4"
          className="animate-dash-flow"
        />

        <g className="animate-float-node">
          <circle cx="400" cy="120" r="28" fill="rgba(16,185,129,0.08)" stroke="#10b981" strokeWidth="1" />
          <text x="400" y="124" textAnchor="middle" fill="#10b981" fontSize="11" fontFamily="monospace">HARNESS</text>
          <circle cx="400" cy="120" r="3" fill="#10b981" className="animate-pulse-dot" />
        </g>

        <g className="animate-float-node" style={{ animationDelay: '1.3s' }}>
          <circle cx="200" cy="320" r="28" fill="rgba(59,130,246,0.08)" stroke="#3b82f6" strokeWidth="1" />
          <text x="200" y="324" textAnchor="middle" fill="#3b82f6" fontSize="9" fontFamily="monospace">INTEL</text>
          <circle cx="200" cy="320" r="3" fill="#3b82f6" className="animate-pulse-dot" style={{ animationDelay: '0.7s' }} />
        </g>

        <g className="animate-float-node" style={{ animationDelay: '2.6s' }}>
          <circle cx="600" cy="320" r="28" fill="rgba(16,185,129,0.08)" stroke="#10b981" strokeWidth="1" />
          <text x="600" y="324" textAnchor="middle" fill="#10b981" fontSize="9" fontFamily="monospace">FACTORY</text>
          <circle cx="600" cy="320" r="3" fill="#10b981" className="animate-pulse-dot" style={{ animationDelay: '1.4s' }} />
        </g>

        <circle cx="140" cy="200" r="2" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '0.3s' }} />
        <circle cx="660" cy="180" r="2" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '1.1s' }} />
        <circle cx="350" cy="420" r="2" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '0.8s' }} />
        <circle cx="500" cy="80" r="1.5" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '1.7s' }} />
        <circle cx="300" cy="80" r="1.5" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '2.1s' }} />
        <circle cx="700" cy="260" r="1.5" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '0.5s' }} />
        <circle cx="100" cy="300" r="1.5" fill="#64748b" className="animate-pulse-dot" style={{ animationDelay: '1.9s' }} />
      </svg>
    </div>
  )
}

function AgentStatusBar() {
  const agents = [
    { name: 'HARNESS', active: true },
    { name: 'INTEL-R01', active: true },
    { name: 'FACTORY-E01', active: true },
  ]

  return (
    <div className="flex items-center gap-4 text-[11px] font-mono text-text-tertiary">
      <span className="flex items-center gap-1.5">
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-emerald/60" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-accent-emerald" />
        </span>
        22 AGENTS ACTIFS
      </span>
      <span className="text-text-tertiary/30">|</span>
      {agents.map((a) => (
        <span key={a.name} className="flex items-center gap-1">
          <span className="h-1 w-1 rounded-full bg-accent-emerald animate-pulse-dot" />
          {a.name}
        </span>
      ))}
    </div>
  )
}

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      <NodalGraph />

      <div className="relative z-10 mx-auto max-w-4xl px-6 text-center">
        <div className="mb-8 flex justify-center">
          <AgentStatusBar />
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight leading-[1.1] text-text-primary mb-6 animate-fade-in-up">
          {data.hero.headline}
        </h1>

        <p className="mx-auto max-w-2xl text-lg text-text-secondary leading-relaxed mb-10 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
          {data.hero.subheadline}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <a
            href="#contact"
            className="inline-flex items-center gap-2 rounded-lg bg-accent-emerald px-6 py-3 text-sm font-medium text-surface hover:bg-accent-emerald/90 transition-all duration-200 shadow-lg shadow-accent-emerald/20"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {data.hero.primaryCTA}
          </a>
          <a
            href="#architecture"
            className="inline-flex items-center gap-2 rounded-lg border border-border-subtle px-6 py-3 text-sm font-medium text-text-secondary hover:text-text-primary hover:border-border-accent transition-all duration-200"
          >
            {data.hero.secondaryCTA}
            <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" />
            </svg>
          </a>
        </div>

        <div className="mt-16 flex items-center justify-center gap-8 text-text-tertiary text-xs font-mono animate-fade-in-up" style={{ animationDelay: '0.45s' }}>
          <span>SCORE QUANTITATIF</span>
          <span className="text-text-tertiary/30">|</span>
          <span>MÉTHODE SKILL</span>
          <span className="text-text-tertiary/30">|</span>
          <span>RGPD COMPLIANT</span>
        </div>
      </div>
    </section>
  )
}
