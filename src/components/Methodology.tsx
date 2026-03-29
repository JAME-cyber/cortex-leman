import data from '../data.json'

const stepIcons = [
  <svg key="1" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
  </svg>,
  <svg key="2" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
  </svg>,
  <svg key="3" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
  </svg>,
  <svg key="4" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6a7.5 7.5 0 107.5 7.5h-7.5V6z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0013.5 3v7.5z" />
  </svg>,
]

export default function Methodology() {
  return (
    <section id="methodology" className="py-24 lg:py-32 border-t border-border-subtle">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mb-16 max-w-2xl">
          <span className="text-xs font-mono text-accent-emerald uppercase tracking-widest mb-3 block">
            Méthodologie SKILL
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-text-primary mb-4">
            De l'Intuition au Plan Quantifié
          </h2>
          <p className="text-text-secondary leading-relaxed">
            Quatre phases d'exécution. Chaque transition est validée par un seuil de confiance algorithmique avant de progresser.
          </p>
        </div>

        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-accent-emerald/40 via-accent-blue/20 to-transparent hidden lg:block" />

          <div className="space-y-6">
            {data.methodology_steps.map((step, i) => (
              <div
                key={step.step}
                className="relative glass-card rounded-2xl p-6 lg:pl-16"
              >
                <div className="absolute left-4 top-8 hidden lg:flex items-center justify-center">
                  <div className="relative">
                    <div className="h-4 w-4 rounded-full border-2 border-accent-emerald bg-surface" />
                    <div className="absolute inset-0 h-4 w-4 rounded-full bg-accent-emerald/20 animate-pulse-dot" style={{ animationDelay: `${i * 0.5}s` }} />
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-lg bg-accent-emerald-dim text-accent-emerald lg:hidden">
                    {stepIcons[i]}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-xs font-mono text-accent-emerald uppercase tracking-wider">
                        Étape {step.step}
                      </span>
                      <span className="h-px flex-1 bg-border-subtle" />
                    </div>
                    <h3 className="text-lg font-semibold text-text-primary mb-2">
                      {step.title}
                    </h3>
                    <p className="text-sm text-text-secondary leading-relaxed max-w-2xl">
                      {step.description}
                    </p>
                  </div>

                  <div className="hidden lg:flex flex-shrink-0 items-center justify-center h-10 w-10 rounded-lg bg-accent-emerald-dim text-accent-emerald">
                    {stepIcons[i]}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-3 glass-card rounded-full px-6 py-3">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-emerald/40" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent-emerald" />
            </span>
            <span className="text-sm font-mono text-text-secondary">
              Durée moyenne : <span className="text-text-primary font-medium">72h</span> pour un audit complet
            </span>
          </div>
        </div>
      </div>
    </section>
  )
}
