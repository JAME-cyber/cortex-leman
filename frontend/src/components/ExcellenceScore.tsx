import { useState, useMemo } from 'react'

/* ═══════════════════════════════════════════════════════════
   CORTEX LEMAN V5 — Score d'Excellence by Design
   Web version of score_excellence.py
   Lead magnet #1 : "L'outil qui vend tout seul"
   Inspiré de: Isabella Badoia ($180K en 6 semaines via quizzes)
   Framework: Excellence by Design Partie 5
   ═══════════════════════════════════════════════════════════ */

// ── Types ──────────────────────────────────────────────────
interface Question {
  text: string
  dimension: string
}

interface Dimension {
  label: string
  icon: string
  weight: number
  questions: Question[]
}

interface VerticalGrid {
  label: string
  icon: string
  dimensions: Dimension[]
  priorities: string[]
  hook: string       // Message d'ouverture (Vérité 1)
  promise: string    // Promesse 90 jours
  myths: [string, string]  // Mythe → Vérité
}

// ── Data: Grilles par vertical (inspiré du FRAMEWORK.md) ──
const GRIDS: Record<string, VerticalGrid> = {
  avocat: {
    label: 'Cabinet d\'Avocats',
    icon: '⚖️',
    hook: 'Vos collaborateurs utilisent ChatGPT en cachette avec des données client. Je peux vous le prouver en 15 minutes.',
    promise: 'En 90 jours, votre cabinet produit 2× plus de conclusions avec la même équipe — en totale conformité déontologique.',
    myths: ['"L\'IA va violer le secret professionnel"', '"Attendre que ça murisse est plus prudent"'],
    priorities: [
      'Souveraineté des données (risque déontologique immédiat)',
      'Productivité documentaire avec IA (gain de temps mesurable)',
      'Veille juridique automatisée (différenciant concurrentiel)',
    ],
    dimensions: [
      { label: 'Souveraineté numérique', icon: '🔐', weight: 20, questions: [
        { text: 'Vos collaborateurs utilisent-ils ChatGPT avec des données client ?', dimension: 'Souveraineté numérique' },
        { text: 'Vos données sont-elles hébergées en France/Europe ?', dimension: 'Souveraineté numérique' },
        { text: 'Avez-vous une politique de confidentialité IA ?', dimension: 'Souveraineté numérique' },
        { text: 'Vos outils cloud respectent-ils le secret professionnel ?', dimension: 'Souveraineté numérique' },
      ]},
      { label: 'Productivité documentaire', icon: '📄', weight: 18, questions: [
        { text: 'Utilisez-vous des modèles de documents automatisés ?', dimension: 'Productivité documentaire' },
        { text: 'Générez-vous vos conclusions avec l\'aide de l\'IA ?', dimension: 'Productivité documentaire' },
        { text: 'Votre gestion de dossier est-elle digitalisée ?', dimension: 'Productivité documentaire' },
        { text: 'Le temps moyen de rédaction d\'un acte est-il < 2h ?', dimension: 'Productivité documentaire' },
      ]},
      { label: 'Outils IA', icon: '🤖', weight: 16, questions: [
        { text: 'Utilisez-vous un outil IA conforme au secret professionnel ?', dimension: 'Outils IA' },
        { text: 'Avez-vous testé Harvey, Rebecca ou équivalent ?', dimension: 'Outils IA' },
        { text: 'Vos prompts juridiques sont-ils optimisés ?', dimension: 'Outils IA' },
      ]},
      { label: 'Présence web', icon: '🌐', weight: 14, questions: [
        { text: 'Avez-vous un site web professionnel ?', dimension: 'Présence web' },
        { text: 'Vos domaines d\'expertise sont-ils clairement listés ?', dimension: 'Présence web' },
        { text: 'Publiez-vous des articles juridiques régulièrement ?', dimension: 'Présence web' },
      ]},
      { label: 'Veille juridique', icon: '📚', weight: 12, questions: [
        { text: 'Avez-vous un système de veille jurisprudentielle ?', dimension: 'Veille juridique' },
        { text: 'Êtes-vous alerté des nouvelles lois dans vos spécialités ?', dimension: 'Veille juridique' },
        { text: 'Partagez-vous la veille avec votre équipe ?', dimension: 'Veille juridique' },
      ]},
      { label: 'Formation continue', icon: '🎓', weight: 10, questions: [
        { text: 'Êtes-vous à jour sur les réglementations IA / AI Act ?', dimension: 'Formation continue' },
        { text: 'Formez-vous vos collaborateurs aux outils numériques ?', dimension: 'Formation continue' },
      ]},
      { label: 'Réputation & Avis', icon: '⭐', weight: 5, questions: [
        { text: 'Avez-vous des avis clients sur Google ?', dimension: 'Réputation & Avis' },
        { text: 'Votre rating est-il > 4.5 ?', dimension: 'Réputation & Avis' },
      ]},
      { label: 'Communication', icon: '💼', weight: 5, questions: [
        { text: 'Avez-vous un LinkedIn professionnel actif ?', dimension: 'Communication' },
        { text: 'Publiez-vous des insights juridiques régulièrement ?', dimension: 'Communication' },
      ]},
    ],
  },
  comptable: {
    label: 'Cabinet Comptable',
    icon: '📊',
    hook: 'Vos clients vont bientôt faire leur propre comptabilité avec l\'IA. La question n\'est pas "si" — c\'est "quand".',
    promise: 'En 90 jours, votre cabinet passe de la saisie comptable au conseil stratégique augmenté — sans perdre une seule mission.',
    myths: ['"L\'IA va remplacer les comptables"', '"Mes clients ne sont pas prêts"'],
    priorities: [
      'Automatisation saisie + OCR (gain de temps immédiat)',
      'Dashboard client temps réel (de comptable → conseiller financier)',
      'Facturation électronique conforme 2026 (obligation légale)',
    ],
    dimensions: [
      { label: 'Automatisation saisie', icon: '⚡', weight: 20, questions: [
        { text: 'Utilisez-vous la facturation électronique ?', dimension: 'Automatisation saisie' },
        { text: 'Vos rapprochements bancaires sont-ils automatisés ?', dimension: 'Automatisation saisie' },
        { text: 'Utilisez-vous l\'OCR pour les pièces comptables ?', dimension: 'Automatisation saisie' },
        { text: 'Avez-vous un outil de déclaration fiscale automatisé ?', dimension: 'Automatisation saisie' },
      ]},
      { label: 'Conseil augmenté', icon: '🎯', weight: 20, questions: [
        { text: 'Proposez-vous un tableau de bord temps réel à vos clients ?', dimension: 'Conseil augmenté' },
        { text: 'Utilisez-vous l\'IA pour détecter des optimisations fiscales ?', dimension: 'Conseil augmenté' },
        { text: 'Avez-vous un outil de prévision de trésorerie ?', dimension: 'Conseil augmenté' },
        { text: 'Fournissez-vous des conseils stratégiques (pas juste de la saisie) ?', dimension: 'Conseil augmenté' },
      ]},
      { label: 'Outils IA', icon: '🤖', weight: 16, questions: [
        { text: 'Utilisez-vous l\'IA pour la rédaction de rapports ?', dimension: 'Outils IA' },
        { text: 'Testez-vous des outils IA de détection d\'anomalies ?', dimension: 'Outils IA' },
        { text: 'Vos prompts comptables sont-ils optimisés ?', dimension: 'Outils IA' },
      ]},
      { label: 'Souveraineté numérique', icon: '🔐', weight: 14, questions: [
        { text: 'Vos outils cloud sont-ils conformes RGPD ?', dimension: 'Souveraineté numérique' },
        { text: 'Vos données clients sont-elles hébergées en France ?', dimension: 'Souveraineté numérique' },
        { text: 'Avez-vous une politique de sécurité informatique ?', dimension: 'Souveraineté numérique' },
      ]},
      { label: 'Formation continue', icon: '🎓', weight: 12, questions: [
        { text: 'Êtes-vous à jour sur la facturation électronique obligatoire ?', dimension: 'Formation continue' },
        { text: 'Formez-vous vos clients aux outils numériques ?', dimension: 'Formation continue' },
      ]},
      { label: 'Présence web', icon: '🌐', weight: 10, questions: [
        { text: 'Avez-vous un site web professionnel ?', dimension: 'Présence web' },
        { text: 'Vos services et tarifs sont-ils clairement affichés ?', dimension: 'Présence web' },
      ]},
      { label: 'Réputation', icon: '⭐', weight: 8, questions: [
        { text: 'Avez-vous des avis clients Google ?', dimension: 'Réputation' },
        { text: 'Êtes-vous recommandé par d\'autres professionnels ?', dimension: 'Réputation' },
      ]},
    ],
  },
  sante: {
    label: 'Cabinet Médical',
    icon: '🏥',
    hook: 'Un médecin passe 50% de son temps sur de l\'administratif. L\'IA peut réduire ça à 10%. Mais 95% des cabinets n\'ont rien fait.',
    promise: 'En 90 jours, vos médecins retrouvent 2h par jour de temps patient — sans toucher à un seul dossier médical non conforme.',
    myths: ['"L\'IA va remplacer les médecins"', '"Le secret médical empêche toute IA"'],
    priorities: [
      'Prise de RDV en ligne (Doctolib = réflexe patient)',
      'Google My Business optimisé (premier point de contact)',
      'Souveraineté des données de santé (obligation légale)',
    ],
    dimensions: [
      { label: 'Prise de RDV en ligne', icon: '📅', weight: 20, questions: [
        { text: 'Vos patients peuvent-ils prendre RDV en ligne ?', dimension: 'Prise de RDV en ligne' },
        { text: 'Utilisez-vous Doctolib ou équivalent ?', dimension: 'Prise de RDV en ligne' },
        { text: 'Le lien de prise de RDV est-il sur votre Google My Business ?', dimension: 'Prise de RDV en ligne' },
        { text: 'Envoyez-vous des rappels de RDV automatiques ?', dimension: 'Prise de RDV en ligne' },
      ]},
      { label: 'Souveraineté données', icon: '🔐', weight: 20, questions: [
        { text: 'Vos données patients sont-elles sur des serveurs certifiés HDS ?', dimension: 'Souveraineté données' },
        { text: 'Avez-vous une politique de protection des données ?', dimension: 'Souveraineté données' },
        { text: 'Vos outils sont-ils conformes au secret médical ?', dimension: 'Souveraineté données' },
      ]},
      { label: 'Outils IA', icon: '🤖', weight: 16, questions: [
        { text: 'Utilisez-vous un assistant IA pour les comptes-rendus ?', dimension: 'Outils IA' },
        { text: 'Avez-vous automatisé le secrétariat (messages, rappels) ?', dimension: 'Outils IA' },
        { text: 'Testez-vous des outils IA d\'aide au diagnostic ?', dimension: 'Outils IA' },
      ]},
      { label: 'Google My Business', icon: '📍', weight: 15, questions: [
        { text: 'Avez-vous une fiche GMB complète et vérifiée ?', dimension: 'Google My Business' },
        { text: 'Avez-vous des photos professionnelles du cabinet ?', dimension: 'Google My Business' },
        { text: 'Répondez-vous aux avis patients ?', dimension: 'Google My Business' },
        { text: 'Avez-vous plus de 30 avis Google ?', dimension: 'Google My Business' },
      ]},
      { label: 'Présence web', icon: '🌐', weight: 12, questions: [
        { text: 'Avez-vous un site web professionnel ?', dimension: 'Présence web' },
        { text: 'Vos spécialités et tarifs sont-ils visibles ?', dimension: 'Présence web' },
        { text: 'Votre site est-il mobile-friendly ?', dimension: 'Présence web' },
      ]},
      { label: 'Réputation', icon: '⭐', weight: 10, questions: [
        { text: 'Votre rating Google est-il > 4.5 ?', dimension: 'Réputation' },
        { text: 'Avez-vous des témoignages patients ?', dimension: 'Réputation' },
      ]},
      { label: 'Communication', icon: '💼', weight: 7, questions: [
        { text: 'Avez-vous une page Facebook/Instagram professionnelle ?', dimension: 'Communication' },
        { text: 'Publiez-vous du contenu éducatif santé ?', dimension: 'Communication' },
      ]},
    ],
  },
  immobilier: {
    label: 'Agence Immobilière',
    icon: '🏠',
    hook: 'Votre client sait déjà tout sur le bien grâce à Internet. Si vous ne vendez plus l\'information, que vendez-vous ?',
    promise: 'En 90 jours, vos agents deviennent des conseillers augmentés qui ferment 2× plus de mandats — parce qu\'ils apportent ce qu\'Internet ne peut pas.',
    myths: ['"Les portails immobiliers vont nous tuer"', '"L\'IA ne peut pas remplacer la relation humaine"'],
    priorities: [
      'Google My Business optimisé (impact immédiat sur la visibilité)',
      'Photos professionnelles + visites virtuelles (différenciant fort)',
      'Prise de RDV en ligne (conversion visiteur → client)',
    ],
    dimensions: [
      { label: 'Présence web', icon: '🌐', weight: 15, questions: [
        { text: 'Avez-vous un site web professionnel ?', dimension: 'Présence web' },
        { text: 'Votre site est-il mobile-friendly ?', dimension: 'Présence web' },
        { text: 'Vos biens sont-ils visibles sur votre site ?', dimension: 'Présence web' },
        { text: 'Avez-vous une page "À propos" avec votre photo ?', dimension: 'Présence web' },
      ]},
      { label: 'Google My Business', icon: '📍', weight: 15, questions: [
        { text: 'Avez-vous une fiche Google My Business ?', dimension: 'Google My Business' },
        { text: 'Votre fiche est-elle vérifiée et complète ?', dimension: 'Google My Business' },
        { text: 'Avez-vous plus de 20 avis Google ?', dimension: 'Google My Business' },
        { text: 'Répondez-vous aux avis Google ?', dimension: 'Google My Business' },
      ]},
      { label: 'Photos & Visuels', icon: '📸', weight: 14, questions: [
        { text: 'Utilisez-vous des photos professionnelles pour vos biens ?', dimension: 'Photos & Visuels' },
        { text: 'Faites-vous des visites virtuelles (360°) ?', dimension: 'Photos & Visuels' },
        { text: 'Avez-vous des vidéos de présentation de biens ?', dimension: 'Photos & Visuels' },
      ]},
      { label: 'Prise de RDV en ligne', icon: '📅', weight: 14, questions: [
        { text: 'Peut-on prendre RDV en ligne avec vous ?', dimension: 'Prise de RDV en ligne' },
        { text: 'Votre lien de RDV est-il visible sur votre site et réseaux ?', dimension: 'Prise de RDV en ligne' },
        { text: 'Répondez-vous aux demandes de RDV en moins de 2h ?', dimension: 'Prise de RDV en ligne' },
      ]},
      { label: 'Outils IA', icon: '🤖', weight: 14, questions: [
        { text: 'Utilisez-vous un outil IA pour l\'estimation automatique ?', dimension: 'Outils IA' },
        { text: 'Utilisez-vous ChatGPT ou Claude pour vos annonces ?', dimension: 'Outils IA' },
        { text: 'Avez-vous automatisé une partie de votre prospection ?', dimension: 'Outils IA' },
      ]},
      { label: 'Réseaux sociaux', icon: '📱', weight: 10, questions: [
        { text: 'Publiez-vous du contenu immobilier régulièrement ?', dimension: 'Réseaux sociaux' },
        { text: 'Avez-vous une page Instagram avec des photos de biens ?', dimension: 'Réseaux sociaux' },
        { text: 'Utilisez-vous Facebook pour des annonces de biens ?', dimension: 'Réseaux sociaux' },
      ]},
      { label: 'Réputation', icon: '⭐', weight: 10, questions: [
        { text: 'Avez-vous plus de 4.5 étoiles sur Google ?', dimension: 'Réputation' },
        { text: 'Demandez-vous systématiquement des avis à vos clients ?', dimension: 'Réputation' },
        { text: 'Avez-vous des témoignages vidéo clients ?', dimension: 'Réputation' },
      ]},
      { label: 'SEO Local', icon: '🔍', weight: 8, questions: [
        { text: 'Apparaissez-vous dans les 3 premiers résultats Google Maps ?', dimension: 'SEO Local' },
        { text: 'Vos annonces contiennent-elles les bons mots-clés locaux ?', dimension: 'SEO Local' },
      ]},
    ],
  },
}

// ── Helpers ────────────────────────────────────────────────
type Step = 'intro' | 'quiz' | 'gate' | 'results'

function scoreColor(score: number): string {
  if (score >= 80) return 'var(--emerald)'
  if (score >= 60) return 'var(--cyan)'
  if (score >= 40) return 'var(--amber)'
  return '#ef4444'
}

function scoreLabel(score: number): string {
  if (score >= 80) return 'Excellent'
  if (score >= 60) return 'Correct'
  if (score >= 40) return 'Insuffisant'
  return 'Critique'
}

function scoreEmoji(score: number): string {
  if (score >= 80) return '🏆'
  if (score >= 60) return '👍'
  if (score >= 40) return '⚠️'
  return '🚨'
}

// ── Component ──────────────────────────────────────────────
export function ExcellenceScore({ onCta }: { onCta?: () => void }) {
  const [vertical, setVertical] = useState<string | null>(null)
  const [step, setStep] = useState<Step>('intro')
  const [questionIdx, setQuestionIdx] = useState(0)
  const [answers, setAnswers] = useState<Record<string, boolean[]>>({})
  const [email, setEmail] = useState('')
  const [companyName, setCompanyName] = useState('')

  // Flatten all questions for current vertical
  const grid = vertical ? GRIDS[vertical] : null
  const allQuestions = useMemo(() => {
    if (!grid) return []
    return grid.dimensions.flatMap(d => d.questions)
  }, [grid])

  // Calculate scores
  const scores = useMemo(() => {
    if (!grid) return { global: 0, dimensions: [], sorted: [] }
    let totalWeighted = 0
    let totalWeight = 0
    const dimScores: { label: string; icon: string; score: number; weight: number }[] = []

    for (const dim of grid.dimensions) {
      const dimAnswers = answers[dim.label] || []
      const yesCount = dimAnswers.filter(Boolean).length
      const score = dim.questions.length > 0 ? (yesCount / dim.questions.length) * 100 : 0
      dimScores.push({ label: dim.label, icon: dim.icon, score: Math.round(score), weight: dim.weight })
      totalWeighted += score * dim.weight
      totalWeight += dim.weight
    }
    const global = totalWeight > 0 ? Math.round(totalWeighted / totalWeight) : 0
    return { global, dimensions: dimScores, sorted: [...dimScores].sort((a, b) => a.score - b.score) }
  }, [grid, answers])

  function handleAnswer(yes: boolean) {
    if (!grid || questionIdx >= allQuestions.length) return
    const q = allQuestions[questionIdx]
    const dim = q.dimension
    const current = answers[dim] || []
    const newAnswers = { ...answers, [dim]: [...current, yes] }
    setAnswers(newAnswers)

    if (questionIdx + 1 < allQuestions.length) {
      setQuestionIdx(questionIdx + 1)
    } else {
      setStep('gate')
    }
  }

  function handleGateSubmit() {
    if (!email) return
    // In production: POST to /api/v1/lead/score with { email, company, vertical, scores, answers }
    setStep('results')
  }

  function reset() {
    setVertical(null)
    setStep('intro')
    setQuestionIdx(0)
    setAnswers({})
    setEmail('')
    setCompanyName('')
  }

  const progress = allQuestions.length > 0 ? Math.round(((questionIdx) / allQuestions.length) * 100) : 0

  // ── INTRO ──
  if (step === 'intro' || !vertical) {
    return (
      <section id="excellence-score" className="section">
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <span className="badge badge-emerald" style={{ marginBottom: '1rem' }}>🎯 Score d'Excellence</span>
          <h2 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.025em', marginBottom: '0.75rem' }}>
            Où en est votre <span style={{ color: 'var(--emerald)' }}>cabinet</span> ?
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto', lineHeight: 1.6 }}>
            10 questions. 2 minutes. Un score personnalisé sur 100.
            <br />
            <strong style={{ color: 'var(--text)' }}>L'audit que votre régulateur approuverait.</strong>
          </p>
        </div>

        {/* 7e vérité: l'Europe est en retard = opportunité */}
        <div style={{
          maxWidth: 700, margin: '0 auto 2.5rem', padding: '1.25rem 1.5rem',
          background: 'rgba(251,191,36,0.06)', border: '1px solid rgba(251,191,36,0.2)',
          borderRadius: '0.75rem', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6,
        }}>
          <strong style={{ color: 'var(--amber)' }}>📊 90% des professions régulées n'ont rien fait avec l'IA.</strong>
          {' '}Pas parce qu'elles ne veulent pas. Parce qu'elles ne savent pas par où commencer. Les 10% qui bougent produisent 2× plus, facturent plus cher, attirent les meilleurs talents.
        </div>

        {/* Vertical selector */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', maxWidth: 900, margin: '0 auto' }}>
          {Object.entries(GRIDS).map(([key, g]) => (
            <button
              key={key}
              onClick={() => { setVertical(key); setStep('quiz'); }}
              style={{
                background: 'var(--glass)', border: '1px solid var(--border)',
                borderRadius: '1rem', padding: '1.5rem', cursor: 'pointer',
                textAlign: 'left' as const, transition: 'all 0.2s',
              }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--emerald)' }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)' }}
            >
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>{g.icon}</div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.25rem' }}>{g.label}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.4 }}>{g.hook.slice(0, 80)}…</div>
            </button>
          ))}
        </div>

        {/* Social proof */}
        <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
          ✅ Gratuit • 📊 Résultats immédiats • 🔒 Données conformes RGPD
        </div>
      </section>
    )
  }

  if (!grid) return null

  // ── QUIZ ──
  if (step === 'quiz') {
    const q = allQuestions[questionIdx]
    const currentDim = grid.dimensions.find(d => d.label === q.dimension)
    const dimProgress = currentDim ? `${currentDim.questions.indexOf(q) + 1}/${currentDim.questions.length}` : ''
    const currentDimIdx = grid.dimensions.findIndex(d => d.label === q.dimension)
    const totalDims = grid.dimensions.length

    return (
      <section id="excellence-score" className="section">
        <div style={{ maxWidth: 640, margin: '0 auto' }}>
          {/* Progress bar */}
          <div style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                {grid.icon} {grid.label}
              </span>
              <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--emerald)' }}>
                {questionIdx + 1}/{allQuestions.length}
              </span>
            </div>
            <div style={{ height: 4, background: 'rgba(30,41,59,0.6)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{
                height: '100%', width: `${progress}%`, background: 'var(--emerald)',
                borderRadius: 2, transition: 'width 0.3s ease-out',
              }} />
            </div>
          </div>

          {/* Dimension indicator */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            background: 'var(--glass)', border: '1px solid var(--border)',
            borderRadius: '0.5rem', padding: '0.375rem 0.75rem',
            fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '1.5rem',
          }}>
            {currentDim?.icon} {q.dimension} ({currentDimIdx + 1}/{totalDims}) {dimProgress && `• ${dimProgress}`}
          </div>

          {/* Question card */}
          <div className="glass" style={{ padding: '2.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>{currentDim?.icon}</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.5, marginBottom: '2rem', color: 'var(--text)' }}>
              {q.text}
            </h3>

            {/* Yes / No buttons */}
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
              <button
                onClick={() => handleAnswer(true)}
                style={{
                  padding: '1rem 2.5rem', fontSize: '1rem', fontWeight: 700,
                  background: 'var(--emerald-dim)', border: '1px solid rgba(52,211,153,0.4)',
                  color: 'var(--emerald)', borderRadius: '0.75rem', cursor: 'pointer',
                  transition: 'all 0.15s', minWidth: 140,
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(52,211,153,0.2)' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'var(--emerald-dim)' }}
              >
                ✅ Oui
              </button>
              <button
                onClick={() => handleAnswer(false)}
                style={{
                  padding: '1rem 2.5rem', fontSize: '1rem', fontWeight: 700,
                  background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)',
                  color: '#ef4444', borderRadius: '0.75rem', cursor: 'pointer',
                  transition: 'all 0.15s', minWidth: 140,
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(239,68,68,0.15)' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(239,68,68,0.08)' }}
              >
                ❌ Non
              </button>
            </div>
          </div>

          {/* Dimension mini-progress dots */}
          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginTop: '1.5rem' }}>
            {grid.dimensions.map((d, i) => {
              const answered = (answers[d.label]?.length || 0)
              const total = d.questions.length
              const done = answered >= total
              const active = d.label === q.dimension
              return (
                <div key={d.label} title={`${d.label} (${answered}/${total})`} style={{
                  width: done ? 32 : 24, height: 6,
                  background: done ? 'var(--emerald)' : active ? 'var(--cyan)' : 'rgba(30,41,59,0.6)',
                  borderRadius: 3, transition: 'all 0.2s',
                }} />
              )
            })}
          </div>
        </div>
      </section>
    )
  }

  // ── EMAIL GATE (Isabella pattern: capture before revealing full results) ──
  if (step === 'gate') {
    return (
      <section id="excellence-score" className="section">
        <div style={{ maxWidth: 560, margin: '0 auto' }}>
          {/* Teaser score */}
          <div className="glass" style={{ padding: '2rem', textAlign: 'center', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>{scoreEmoji(scores.global)}</div>
            <div className="mono" style={{ fontSize: '4rem', fontWeight: 800, color: scoreColor(scores.global), lineHeight: 1 }}>
              {scores.global}
            </div>
            <div style={{ fontSize: '1rem', color: 'var(--text-dim)', marginBottom: '0.5rem' }}>/ 100</div>
            <div style={{ fontSize: '1.125rem', fontWeight: 700, color: scoreColor(scores.global) }}>
              {scoreLabel(scores.global)}
            </div>
          </div>

          {/* Gate card */}
          <div className="glass" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem', textAlign: 'center' }}>
              📊 Recevez votre rapport détaillé
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              Score par dimension, 3 priorités immédiates, plan d'action 90 jours.
              <br />Gratuit. Sans engagement.
            </p>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>
                Nom du cabinet *
              </label>
              <input
                type="text" value={companyName} onChange={e => setCompanyName(e.target.value)}
                placeholder={grid.label}
                style={{
                  width: '100%', padding: '0.75rem 1rem', fontSize: '0.9rem',
                  background: 'rgba(15,23,42,0.6)', border: '1px solid var(--border)',
                  borderRadius: '0.5rem', color: 'var(--text)', outline: 'none',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'block', marginBottom: '0.375rem' }}>
                Email professionnel *
              </label>
              <input
                type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="vous@cabinet.fr"
                style={{
                  width: '100%', padding: '0.75rem 1rem', fontSize: '0.9rem',
                  background: 'rgba(15,23,42,0.6)', border: '1px solid var(--border)',
                  borderRadius: '0.5rem', color: 'var(--text)', outline: 'none',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <button
              onClick={handleGateSubmit}
              disabled={!email}
              style={{
                width: '100%', padding: '0.875rem', fontSize: '1rem', fontWeight: 700,
                background: email ? 'var(--emerald)' : 'var(--border)',
                color: email ? '#0f172a' : 'var(--text-dim)',
                border: 'none', borderRadius: '0.75rem', cursor: email ? 'pointer' : 'default',
                transition: 'all 0.2s', fontFamily: 'inherit',
              }}
            >
              → Voir mon rapport complet
            </button>

            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textAlign: 'center', marginTop: '0.75rem' }}>
              🔒 Vos données sont conformes RGPD. Jamais revendues.
            </div>
          </div>
        </div>
      </section>
    )
  }

  // ── RESULTS ──
  if (step === 'results') {
    const priorities = scores.sorted.slice(0, 3)
    const target90 = Math.min(scores.global + 40, 85)

    return (
      <section id="excellence-score" className="section">
        <div style={{ maxWidth: 700, margin: '0 auto' }}>
          {/* Score Header */}
          <div className="glass" style={{ padding: '2.5rem', textAlign: 'center', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{grid.icon}</div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>
              {companyName || grid.label}
            </h2>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '2rem' }}>
              Score d'Excellence Digitale • {new Date().toLocaleDateString('fr-FR')}
            </div>

            {/* Animated score circle */}
            <div style={{
              width: 160, height: 160, borderRadius: '50%',
              border: `4px solid ${scoreColor(scores.global)}`,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 1rem',
            }}>
              <div className="mono" style={{ fontSize: '3.5rem', fontWeight: 900, color: scoreColor(scores.global), lineHeight: 1 }}>
                {scores.global}
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-dim)' }}>/ 100</div>
            </div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: scoreColor(scores.global), marginBottom: '0.5rem' }}>
              {scoreLabel(scores.global)}
            </div>

            {/* Myths busted */}
            <div style={{
              marginTop: '1.5rem', padding: '1rem',
              background: 'rgba(251,191,36,0.06)', border: '1px solid rgba(251,191,36,0.15)',
              borderRadius: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5,
            }}>
              💡 <strong style={{ color: 'var(--amber)' }}>Mythe :</strong> {grid.myths[0]}
              <br />
              <strong style={{ color: 'var(--emerald)' }}>Réalité :</strong> Les cabinets qui adoptent l'IA produisent 2× plus, en toute conformité.
            </div>
          </div>

          {/* Dimensions breakdown */}
          <div className="glass" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
            <div className="mono" style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1.25rem' }}>
              📊 Détail par dimension
            </div>
            {scores.sorted.map(dim => (
              <div key={dim.label} style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {dim.icon} {dim.label}
                  </span>
                  <span className="mono" style={{ fontSize: '0.85rem', fontWeight: 700, color: scoreColor(dim.score) }}>
                    {dim.score}/100
                  </span>
                </div>
                <div style={{ height: 8, background: 'rgba(30,41,59,0.6)', borderRadius: 4, overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', width: `${dim.score}%`, background: scoreColor(dim.score),
                    borderRadius: 4, transition: 'width 1s ease-out',
                  }} />
                </div>
              </div>
            ))}
          </div>

          {/* Priorities */}
          <div className="glass" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
            <div className="mono" style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1.25rem' }}>
              ⚠️ Vos 3 priorités immédiates
            </div>
            {priorities.map((dim, i) => (
              <div key={dim.label} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '1rem' }}>
                <div style={{
                  background: '#ef4444', color: 'white', width: 28, height: 28, borderRadius: '50%',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 800, fontSize: '0.8rem', flexShrink: 0,
                }}>
                  {i + 1}
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>
                    {dim.icon} {dim.label} ({dim.score}/100)
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    {grid.priorities[i] || 'À améliorer en priorité'}
                  </div>
                </div>
              </div>
            ))}

            {/* 90-day target */}
            <div style={{
              marginTop: '1.5rem', padding: '1rem',
              background: 'rgba(52,211,153,0.06)', border: '1px solid rgba(52,211,153,0.2)',
              borderRadius: '0.75rem',
            }}>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.25rem' }}>🎯 Objectif 90 jours</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Passer de <strong style={{ color: scoreColor(scores.global) }}>{scores.global}/100</strong> à{' '}
                <strong style={{ color: 'var(--emerald)' }}>{target90}/100</strong> avec Excellence by Design
              </div>
            </div>
          </div>

          {/* CTA: Audit gratuit */}
          <div style={{
            textAlign: 'center', padding: '2.5rem',
            background: 'linear-gradient(135deg, rgba(52,211,153,0.08), rgba(34,211,238,0.08))',
            border: '1px solid rgba(52,211,153,0.2)', borderRadius: '1rem',
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              {grid.promise.slice(0, 60)}…
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              Audit gratuit de 15 minutes. On vous montre exactement ce qui change — avec des chiffres.
              <br />Si ça ne vous convainc pas, on se serre la main et c'est tout.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button onClick={() => onCta?.()} style={{
                padding: '0.875rem 2rem', fontSize: '1rem', fontWeight: 700,
                background: 'var(--emerald)', color: '#0f172a', border: 'none',
                borderRadius: '0.75rem', cursor: 'pointer', fontFamily: 'inherit',
              }}>
                📞 Obtenir mon audit gratuit
              </button>
              <button onClick={reset} style={{
                padding: '0.875rem 1.5rem', fontSize: '0.875rem', fontWeight: 500,
                background: 'transparent', color: 'var(--text-dim)',
                border: '1px solid var(--border)', borderRadius: '0.75rem', cursor: 'pointer',
                fontFamily: 'inherit',
              }}>
                ← Refaire le test
              </button>
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '1rem' }}>
              📊 Rapport envoyé à {email} • {companyName || grid.label} • Conforme RGPD
            </div>
          </div>
        </div>
      </section>
    )
  }

  return null
}
