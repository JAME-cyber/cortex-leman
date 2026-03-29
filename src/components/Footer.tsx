import data from '../data.json'

export default function Footer() {
  return (
    <footer id="contact" className="border-t border-border-subtle">
      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="relative flex h-8 w-8 items-center justify-center">
                <div className="absolute h-8 w-8 rounded-lg bg-accent-emerald/20" />
                <svg
                  viewBox="0 0 24 24"
                  className="relative h-5 w-5 text-accent-emerald"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                >
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-text-primary">{data.brand.name}</span>
            </div>
            <p className="text-sm text-text-tertiary leading-relaxed">
              {data.brand.baseline}
            </p>
          </div>

          <div>
            <h4 className="text-xs font-mono text-text-tertiary uppercase tracking-widest mb-4">Navigation</h4>
            <div className="space-y-2">
              {[
                { label: 'Architecture', href: '#architecture' },
                { label: 'Méthodologie', href: '#methodology' },
                { label: 'Sécurité', href: '#security' },
              ].map((l) => (
                <a
                  key={l.href}
                  href={l.href}
                  className="block text-sm text-text-secondary hover:text-text-primary transition-colors duration-200"
                >
                  {l.label}
                </a>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-xs font-mono text-text-tertiary uppercase tracking-widest mb-4">Contact</h4>
            <div className="space-y-3">
              <a
                href={`mailto:${data.brand.contactEmail}`}
                className="flex items-center gap-2 text-sm text-text-secondary hover:text-accent-emerald transition-colors duration-200"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
                {data.brand.contactEmail}
              </a>
              <div className="flex items-center gap-2 text-sm text-text-secondary">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                </svg>
                {data.brand.location}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border-subtle flex flex-col sm:flex-row items-center justify-between gap-4">
          <span className="text-xs text-text-tertiary font-mono">
            &copy; {new Date().getFullYear()} {data.brand.name}. Infrastructure d'orchestration asymétrique.
          </span>
          <div className="flex items-center gap-2">
            <span className="relative flex h-1.5 w-1.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-emerald/40" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-accent-emerald" />
            </span>
            <span className="text-xs font-mono text-text-tertiary">SYSTÈME OPÉRATIONNEL</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
