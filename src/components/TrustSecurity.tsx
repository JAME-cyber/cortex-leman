import data from '../data.json'

const shieldIcon = (
  <svg className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
  </svg>
)

const featureIcons = [
  <svg key="1" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3H21m-3.75 3H21" />
  </svg>,
  <svg key="2" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z" />
  </svg>,
  <svg key="3" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
  </svg>,
]

export default function TrustSecurity() {
  return (
    <section id="security" className="py-24 lg:py-32 border-t border-border-subtle">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <span className="text-xs font-mono text-accent-emerald uppercase tracking-widest mb-3 block">
              Conformité & Souveraineté
            </span>
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-text-primary mb-4">
              {data.trust_and_security.title}
            </h2>
            <p className="text-text-secondary leading-relaxed mb-8">
              L'infrastructure est conçue pour garantir que chaque donnée confidentielle reste dans un périmètre contrôlé. Aucune requête n'est transmise à des services externes non audités.
            </p>

            <div className="space-y-4">
              {data.trust_and_security.features.map((feature, i) => (
                <div
                  key={feature}
                  className="flex items-start gap-4 glass-card rounded-xl p-4"
                >
                  <div className="flex-shrink-0 flex items-center justify-center h-9 w-9 rounded-lg bg-accent-emerald-dim text-accent-emerald">
                    {featureIcons[i]}
                  </div>
                  <div>
                    <span className="text-sm font-medium text-text-primary">{feature}</span>
                    <p className="text-xs text-text-tertiary mt-1">
                      {i === 0 && 'Infrastructure hébergée sur le territoire franco-suisse. Aucune dépendance cloud extraterritoriale.'}
                      {i === 1 && 'L\'agent Compliance Enforcer vérifie en continu la conformité au RGPD et aux directives locales.'}
                      {i === 2 && 'Les modèles de traitement opèrent en environnement fermé. Vos données ne quittent jamais le nœud de calcul.'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-center">
            <div className="relative w-full max-w-md">
              <div className="glass-card rounded-2xl p-8 text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-2xl bg-accent-emerald-dim text-accent-emerald mb-6">
                  {shieldIcon}
                </div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Certification RGPD
                </h3>
                <p className="text-sm text-text-secondary mb-6">
                  Traitement local exclusif. Conformité vérifiée par l'agent Compliance Enforcer.
                </p>
                <div className="space-y-3">
                  {['Données chiffrées au repos', 'Accès traçabilité complète', 'Pas de transfert hors-UE'].map((item) => (
                    <div key={item} className="flex items-center gap-2 text-sm text-text-secondary">
                      <svg className="h-4 w-4 text-accent-emerald flex-shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                      </svg>
                      {item}
                    </div>
                  ))}
                </div>

                <div className="mt-6 pt-4 border-t border-border-subtle">
                  <div className="flex items-center justify-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-emerald/40" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-accent-emerald" />
                    </span>
                    <span className="text-xs font-mono text-accent-emerald">CONFORMITÉ ACTIVE</span>
                  </div>
                </div>
              </div>

              <div className="absolute -top-4 -right-4 h-24 w-24 rounded-full bg-accent-emerald/5 blur-2xl" />
              <div className="absolute -bottom-4 -left-4 h-24 w-24 rounded-full bg-accent-blue/5 blur-2xl" />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
