import type { ReactNode } from 'react'
import data from '../data.json'

const icons: Record<string, ReactNode> = {
  pole_intelligence: (
    <svg className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
    </svg>
  ),
  local_vault: (
    <svg className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />
    </svg>
  ),
  pole_factory: (
    <svg className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" d="M11.42 15.17l-5.1-5.1a2.5 2.5 0 113.54-3.54l1.06 1.06 1.06-1.06a2.5 2.5 0 113.54 3.54l-5.1 5.1zM3.75 21h16.5M12 3v18" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 7.5L18 9m-6-6l1.5 1.5M4.5 7.5L6 9" />
    </svg>
  ),
}

function BentoCard({ card, large }: { card: typeof data.architecture_bento[0]; large?: boolean }) {
  const isVault = card.id === 'local_vault'

  return (
    <div
      className={`glass-card rounded-2xl p-6 flex flex-col justify-between ${
        large ? 'md:col-span-2 md:row-span-1' : ''
      }`}
    >
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`flex items-center justify-center h-9 w-9 rounded-lg ${
              isVault ? 'bg-accent-blue-dim text-accent-blue' : 'bg-accent-emerald-dim text-accent-emerald'
            }`}>
              {icons[card.id] || icons.pole_intelligence}
            </div>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className={`absolute inline-flex h-full w-full animate-ping rounded-full ${
                  isVault ? 'bg-accent-blue/40' : 'bg-accent-emerald/40'
                }`} />
                <span className={`relative inline-flex h-2 w-2 rounded-full ${
                  isVault ? 'bg-accent-blue' : 'bg-accent-emerald'
                }`} />
              </span>
              <span className="text-[11px] font-mono text-text-tertiary uppercase tracking-wider">
                {card.id.replace('_', ' ')}
              </span>
            </div>
          </div>
        </div>

        <h3 className="text-lg font-semibold text-text-primary mb-2">{card.title}</h3>
        <p className="text-sm text-text-secondary leading-relaxed">{card.description}</p>
      </div>

      <div className="mt-6 pt-4 border-t border-border-subtle">
        <div className="flex items-center justify-between">
          <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-mono font-medium ${
            isVault
              ? 'bg-accent-blue-dim text-accent-blue'
              : 'bg-accent-emerald-dim text-accent-emerald'
          }`}>
            <svg className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {card.metric}
          </span>
          <span className="text-[10px] font-mono text-text-tertiary">
            {card.id === 'pole_intelligence' ? '3 AGENTS' : card.id === 'pole_factory' ? '3 AGENTS' : 'ISOLÉ'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default function BentoGrid() {
  return (
    <section id="architecture" className="py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mb-16 max-w-2xl">
          <span className="text-xs font-mono text-accent-emerald uppercase tracking-widest mb-3 block">
            Architecture Asymétrique
          </span>
          <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight text-text-primary mb-4">
            Preuve par l'Architecture
          </h2>
          <p className="text-text-secondary leading-relaxed">
            Trois pôles isolés, une orchestration centrale. Chaque composant de l'infrastructure opère dans un périmètre défini pour éliminer toute dérive cognitive.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <BentoCard card={data.architecture_bento[0]} />
          <BentoCard card={data.architecture_bento[1]} large />
          <BentoCard card={data.architecture_bento[2]} />
        </div>

        <div className="mt-8 glass-card rounded-2xl p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-accent-emerald-dim">
                <svg className="h-4 w-4 text-accent-emerald" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                </svg>
              </div>
              <div>
                <span className="text-sm font-medium text-text-primary">Harness — Orchestrateur Central</span>
                <p className="text-xs text-text-tertiary">Coordonne les 22 agents. Aucune décision n'est prise sans validation croisée.</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-emerald/40" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-accent-emerald" />
              </span>
              <span className="text-xs font-mono text-accent-emerald">OPÉRATIONNEL</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
