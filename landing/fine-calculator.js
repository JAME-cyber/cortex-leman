/**
 * Cortex Leman — Calculateur d'Amendes RGPD / AI Act / Secret Professionnel
 * 
 * Chiffre le risque financier en euros pour chaque verticale régulée.
 * 5 étapes → estimation personnalisée → CTA audit.
 * 
 * Logique :
 *   - RGPD : Art. 83 → jusqu'à 20M€ ou 4% CA mondial
 *   - AI Act : Art. 99 → jusqu'à 35M€ ou 7% CA mondial
 *   - Secret professionnel FR : Art. 226-13 CP → 1 an + 45 000€
 *   - Secret professionnel CH : Art. 321 CP → 3 ans ou amende
 *   - LPerD (CH) : jusqu'à 250 000 CHF
 *   - HDS (santé FR) : jusqu'à 100 000€ par violation
 *   - FINMA (banque CH) : jusqu'à 10M CHF + retrait agrément
 */

// ════════════════════════════════════════════════════════════
// DATA — Barèmes d'amendes par verticale et réglementation
// ════════════════════════════════════════════════════════════

const VERTICALS = {
  avocat: {
    label: 'Avocat / Cabinet juridique',
    icon: '⚖️',
    regulations: ['rgpd', 'ai_act', 'secret_pro_fr', 'secret_pro_ch'],
    specificRisks: [
      { id: 'client_data_ia', text: 'Données clients traitées par IA (conclusions, correspondances adversaires)', weight: 3 },
      { id: 'confidentiality_breach', text: 'Risque de rupture du secret professionnel via LLM public', weight: 3 },
      { id: 'duty_counsel', text: 'Obligation de conseil sur conformité IA du client', weight: 1 }
    ],
    horrorCases: [
      { who: 'Cabinet parisien', what: 'ChatGPT utilisé pour rédiger conclusions → données adversaire dans le training OpenAI', fine: 'Radiation + poursuites civiles' },
      { who: 'Étude genevoise', what: 'Claude.ai alimenté avec dossiers bancaires clients → violation Art. 321 CP', fine: '3 ans de prison + amende' }
    ]
  },
  comptable: {
    label: 'Expert-comptable / Cabinet',
    icon: '📊',
    regulations: ['rgpd', 'ai_act', 'secret_pro_fr'],
    specificRisks: [
      { id: 'fiscal_data', text: 'Données fiscales et bancaires clients dans des LLM publics', weight: 3 },
      { id: 'automated_reporting', text: 'Déclarations fiscales générées par IA sans validation humaine', weight: 2 },
      { id: 'client_consent', text: 'Absence de consentement client pour traitement IA', weight: 2 }
    ],
    horrorCases: [
      { who: 'Cabinet lyonnais', what: 'DeepSeek utilisé pour analyser bilans → données envoyées en Chine', fine: '150 000€ CNIL + perte agrément DEC' },
      { who: 'Fiduciaire vaudoise', what: 'Outil IA non audité pour préparer les comptes → erreurs systématiques', fine: 'Suspension OEC + dommages clients' }
    ]
  },
  sante: {
    label: 'Santé / Médical',
    icon: '🏥',
    regulations: ['rgpd', 'ai_act', 'hds'],
    specificRisks: [
      { id: 'patient_data', text: 'Données patient dans des IA non certifiées HDS', weight: 3 },
      { id: 'diagnostic_ia', text: 'IA utilisée pour diagnostic sans marquage CE médical', weight: 3 },
      { id: 'consentement', text: 'Consentement patient absent pour traitement IA', weight: 2 }
    ],
    horrorCases: [
      { who: 'CHU français', what: 'Chatbot santé alimenté avec 300 000 dossiers patients → leak via API', fine: '250 000€ CNIL + HDS non conforme' },
      { who: 'Cabinet dentaire', what: 'IA de prédiction traitement sans DPIA → données de santé sur serveur US', fine: '100 000€ par violation + radiation' }
    ]
  },
  banque: {
    label: 'Banque / Finance (CH)',
    icon: '🏦',
    regulations: ['rgpd', 'ai_act', 'secret_pro_ch', 'finma'],
    specificRisks: [
      { id: 'banking_secrecy', text: 'Secret bancaire suisse (Art. 47 LB) violé par LLM cloud', weight: 3 },
      { id: 'aml_fraud', text: 'IA de détection fraud/AML sans validation FINMA', weight: 3 },
      { id: 'cross_border', text: 'Données clients cross-border sur infrastructure non CH', weight: 2 }
    ],
    horrorCases: [
      { who: 'Banque cantonale', what: 'ChatGPT pour synthèses KYC → données bancaires dans le cloud US', fine: '10M CHF FINMA + retrait agrément possible' },
      { who: 'Gestionnaire fortune', what: 'Agent IA de conseil investissement non supervisé → pertes clients', fine: 'FINMA enforcement + poursuites civiles' }
    ]
  },
  rh: {
    label: 'Ressources Humaines',
    icon: '👥',
    regulations: ['rgpd', 'ai_act'],
    specificRisks: [
      { id: 'algorithmic_hiring', text: 'IA de tri CV / scoring candidat sans transparence (Art. 22 RGPD)', weight: 3 },
      { id: 'employee_surveillance', text: 'Surveillance IA des employés sans information', weight: 2 },
      { id: 'sensitive_data', text: 'Données sensibles (santé, syndicat) traitées par IA', weight: 3 }
    ],
    horrorCases: [
      { who: 'Grand groupe FR', what: 'IA de sélection CV biaisée → discrimination systématique', fine: '375 000€ + dommages intérêts' },
      { who: 'Suisse romande', what: 'Chatbot RH qui stockait données santé employés sur serveur US', fine: 'LPerD : 250 000 CHF + réputation' }
    ]
  },
  startup: {
    label: 'Startup / Tech',
    icon: '🚀',
    regulations: ['rgpd', 'ai_act'],
    specificRisks: [
      { id: 'data_minimization', text: 'Collecte excessive de données pour entraîner des modèles IA', weight: 2 },
      { id: 'no_dpia', text: 'Absence d\'AIPD/DPIA malgré traitement à risque', weight: 2 },
      { id: 'transparent_ai', text: 'IA "black box" sans documentation technique obligatoire (AI Act)', weight: 2 }
    ],
    horrorCases: [
      { who: 'Startup fintech FR', what: 'Scoring de crédit par IA sans explicabilité → AI Act high-risk', fine: '4% CA ou 20M€ (au plus élevé)' },
      { who: 'SaaS RH suisse', what: 'Traitement données employees sans base légale → LPerD violation', fine: '250 000 CHF + interdiction traitement' }
    ]
  }
};

const REGULATIONS = {
  rgpd: {
    label: 'RGPD (UE)',
    article: 'Art. 83 RGPD',
    maxFine: '20 000 000€ ou 4% CA mondial',
    maxFineNum: 20000000,
    description: 'Violation des données personnelles, absence de consentement, transfert hors UE non conforme'
  },
  ai_act: {
    label: 'AI Act (UE)',
    article: 'Art. 99 AI Act',
    maxFine: '35 000 000€ ou 7% CA mondial',
    maxFineNum: 35000000,
    description: 'Utilisation de systèmes IA à risque non conforme, absence de documentation technique'
  },
  secret_pro_fr: {
    label: 'Secret professionnel (FR)',
    article: 'Art. 226-13 Code pénal',
    maxFine: '45 000€ + 1 an de prison',
    maxFineNum: 45000,
    description: 'Révélation d\'informations confidentielles par avocat, médecin, expert-comptable'
  },
  secret_pro_ch: {
    label: 'Secret professionnel (CH)',
    article: 'Art. 321 Code pénal suisse',
    maxFine: '3 ans de prison ou amende',
    maxFineNum: 540000,
    description: 'Violation du secret professionnel par avocat, médecin, banquier, notaire suisse'
  },
  hds: {
    label: 'Hébergeur Données de Santé (FR)',
    article: 'Art. L.1111-8 Code santé publique',
    maxFine: '100 000€ par violation',
    maxFineNum: 100000,
    description: 'Données de santé hébergées chez un prestataire non certifié HDS'
  },
  finma: {
    label: 'FINMA (CH)',
    article: 'Art. 49 LB + circulaire FINMA',
    maxFine: '10 000 000 CHF + retrait agrément',
    maxFineNum: 10000000,
    description: 'Non-respect des obligations de surveillance, violation secret bancaire, risques systémiques'
  }
};

// ════════════════════════════════════════════════════════════
// CALCULATOR ENGINE
// ════════════════════════════════════════════════════════════

class FineCalculator {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.step = 0;
    this.data = {};
    this.render();
  }

  // ─── Fine estimation algorithm ───
  calculateFines() {
    const v = VERTICALS[this.data.vertical];
    const ca = parseInt(this.data.revenue) || 500000;
    const employees = parseInt(this.data.employees) || 10;
    const iaUsage = parseInt(this.data.iaUsage) || 2;
    const sensitiveData = parseInt(this.data.sensitiveData) || 2;
    const dpia = parseInt(this.data.dpia) || 2;
    const hosting = parseInt(this.data.hosting) || 2;

    // Risk multiplier based on answers (1.0 = baseline, 3.0 = max exposure)
    let riskMult = 1.0;
    riskMult += (iaUsage - 1) * 0.4;       // 1=jamais(0), 2=parfois(0.4), 3=tout le temps(0.8)
    riskMult += (sensitiveData - 1) * 0.5;  // sensitive data increases risk
    riskMult += (dpia === 2) ? 0.3 : 0;     // no DPIA = higher risk
    riskMult += (hosting === 1) ? 0 : (hosting === 2) ? 0.2 : 0.5; // US hosting = higher risk
    riskMult = Math.min(riskMult, 3.0);

    const fines = [];

    for (const regKey of v.regulations) {
      const reg = REGULATIONS[regKey];
      const percentCA = regKey === 'ai_act' ? 0.07 : regKey === 'rgpd' ? 0.04 : regKey === 'finma' ? 0.10 : 0;
      const fineBasedOnCA = percentCA > 0 ? ca * percentCA * riskMult : Infinity;
      const fineFixed = reg.maxFineNum * (0.1 + (riskMult / 3) * 0.9);
      const estimatedFine = Math.round(Math.min(fineBasedOnCA, fineFixed));
      const probability = riskMult >= 2.0 ? 'Élevée' : riskMult >= 1.3 ? 'Modérée' : 'Faible';

      fines.push({
        regulation: reg,
        estimatedFine,
        probability,
        riskMult: riskMult.toFixed(1)
      });
    }

    // Sort by estimated fine descending
    fines.sort((a, b) => b.estimatedFine - a.estimatedFine);

    const totalExposure = fines.reduce((sum, f) => sum + f.estimatedFine, 0);

    return { fines, totalExposure, riskMult: riskMult.toFixed(1) };
  }

  formatEuros(amount) {
    if (amount >= 1000000) return (amount / 1000000).toFixed(1).replace('.0', '') + ' M€';
    if (amount >= 1000) return Math.round(amount / 1000) + ' k€';
    return amount + ' €';
  }

  formatCHF(amount) {
    if (amount >= 1000000) return (amount / 1000000).toFixed(1).replace('.0', '') + ' M CHF';
    if (amount >= 1000) return Math.round(amount / 1000) + ' k CHF';
    return amount + ' CHF';
  }

  // ─── Rendering ───
  render() {
    switch (this.step) {
      case 0: this.renderIntro(); break;
      case 1: this.renderStep1(); break;
      case 2: this.renderStep2(); break;
      case 3: this.renderStep3(); break;
      case 4: this.renderStep4(); break;
      case 5: this.renderResults(); break;
    }
  }

  renderIntro() {
    this.container.innerHTML = `
      <div class="fc-intro">
        <div class="fc-intro-icon">💰</div>
        <h3 class="fc-intro-title">Calculateur d'Amendes<br>RGPD · AI Act · Secret Pro</h3>
        <p class="fc-intro-sub">
          Chiffrez votre risque financier en 4 questions.<br>
          Estimation personnalisée basée sur les barèmes légaux en vigueur.
        </p>
        <div class="fc-intro-stats">
          <div class="fc-stat">
            <span class="fc-stat-val">35M€</span>
            <span class="fc-stat-lbl">Amende max AI Act</span>
          </div>
          <div class="fc-stat">
            <span class="fc-stat-val">20M€</span>
            <span class="fc-stat-lbl">Amende max RGPD</span>
          </div>
          <div class="fc-stat">
            <span class="fc-stat-val">3 ans</span>
            <span class="fc-stat-lbl">Prison secret pro CH</span>
          </div>
        </div>
        <button class="fc-btn-primary" onclick="fineCalc.next()">
          Calculer mon risque →
        </button>
        <p class="fc-intro-disclaimer">⏱ 1 minute · Données non collectées · Sans engagement</p>
      </div>
    `;
  }

  renderStep1() {
    this.container.innerHTML = `
      <div class="fc-step">
        <div class="fc-progress"><div class="fc-progress-bar" style="width:25%"></div></div>
        <div class="fc-step-header">
          <span class="fc-step-num">1/4</span>
          <h3 class="fc-step-title">Votre secteur d'activité</h3>
        </div>
        <div class="fc-grid">
          ${Object.entries(VERTICALS).map(([key, v]) => `
            <button class="fc-card ${this.data.vertical === key ? 'fc-card-selected' : ''}" 
                    onclick="fineCalc.data.vertical='${key}'; fineCalc.render()">
              <span class="fc-card-icon">${v.icon}</span>
              <span class="fc-card-label">${v.label}</span>
            </button>
          `).join('')}
        </div>
        <div class="fc-nav">
          <button class="fc-btn-ghost" onclick="fineCalc.step=0; fineCalc.render()">← Retour</button>
          <button class="fc-btn-primary ${!this.data.vertical ? 'fc-btn-disabled' : ''}" 
                  onclick="fineCalc.next()" ${!this.data.vertical ? 'disabled' : ''}>
            Suivant →
          </button>
        </div>
      </div>
    `;
  }

  renderStep2() {
    this.container.innerHTML = `
      <div class="fc-step">
        <div class="fc-progress"><div class="fc-progress-bar" style="width:50%"></div></div>
        <div class="fc-step-header">
          <span class="fc-step-num">2/4</span>
          <h3 class="fc-step-title">Votre utilisation de l'IA</h3>
        </div>
        <div class="fc-form">
          <div class="fc-field">
            <label class="fc-label">Chiffre d'affaires annuel</label>
            <div class="fc-select-wrap">
              <select class="fc-select" id="fc-revenue" onchange="fineCalc.data.revenue=this.value">
                <option value="200000" ${this.data.revenue === '200000' ? 'selected' : ''}>Moins de 500K€</option>
                <option value="500000" ${this.data.revenue === '500000' || !this.data.revenue ? 'selected' : ''}>500K€ — 1M€</option>
                <option value="2000000" ${this.data.revenue === '2000000' ? 'selected' : ''}>1M€ — 5M€</option>
                <option value="10000000" ${this.data.revenue === '10000000' ? 'selected' : ''}>5M€ — 20M€</option>
                <option value="50000000" ${this.data.revenue === '50000000' ? 'selected' : ''}>20M€ — 100M€</option>
                <option value="200000000" ${this.data.revenue === '200000000' ? 'selected' : ''}>Plus de 100M€</option>
              </select>
            </div>
          </div>
          <div class="fc-field">
            <label class="fc-label">Utilisez-vous des outils IA (ChatGPT, Claude, Copilot…) ?</label>
            <div class="fc-options">
              <button class="fc-opt ${this.data.iaUsage === '1' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.iaUsage='1'; fineCalc.render()">Non, jamais</button>
              <button class="fc-opt ${this.data.iaUsage === '2' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.iaUsage='2'; fineCalc.render()">Oui, parfois</button>
              <button class="fc-opt ${this.data.iaUsage === '3' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.iaUsage='3'; fineCalc.render()">Oui, quotidiennement</button>
            </div>
          </div>
          <div class="fc-field">
            <label class="fc-label">Traitez-vous des données sensibles via IA ? (clients, patients, dossiers)</label>
            <div class="fc-options">
              <button class="fc-opt ${this.data.sensitiveData === '1' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.sensitiveData='1'; fineCalc.render()">Non</button>
              <button class="fc-opt ${this.data.sensitiveData === '2' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.sensitiveData='2'; fineCalc.render()">Oui, partiellement</button>
              <button class="fc-opt ${this.data.sensitiveData === '3' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.sensitiveData='3'; fineCalc.render()">Oui, massivement</button>
            </div>
          </div>
        </div>
        <div class="fc-nav">
          <button class="fc-btn-ghost" onclick="fineCalc.step=1; fineCalc.render()">← Retour</button>
          <button class="fc-btn-primary ${!this.data.iaUsage ? 'fc-btn-disabled' : ''}" 
                  onclick="fineCalc.next()" ${!this.data.iaUsage ? 'disabled' : ''}>
            Suivant →
          </button>
        </div>
      </div>
    `;
  }

  renderStep3() {
    this.container.innerHTML = `
      <div class="fc-step">
        <div class="fc-progress"><div class="fc-progress-bar" style="width:75%"></div></div>
        <div class="fc-step-header">
          <span class="fc-step-num">3/4</span>
          <h3 class="fc-step-title">Conformité actuelle</h3>
        </div>
        <div class="fc-form">
          <div class="fc-field">
            <label class="fc-label">Avez-vous réalisé une Analyse d'Impact (AIPD/DPIA) ?</label>
            <div class="fc-options">
              <button class="fc-opt ${this.data.dpia === '1' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.dpia='1'; fineCalc.render()">Oui, à jour</button>
              <button class="fc-opt ${this.data.dpia === '2' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.dpia='2'; fineCalc.render()">Non</button>
              <button class="fc-opt ${this.data.dpia === '3' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.dpia='3'; fineCalc.render()">Je ne sais pas ce que c'est</button>
            </div>
          </div>
          <div class="fc-field">
            <label class="fc-label">Où sont hébergées vos données IA ?</label>
            <div class="fc-options">
              <button class="fc-opt ${this.data.hosting === '1' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.hosting='1'; fineCalc.render()">EU / Suisse (conforme)</button>
              <button class="fc-opt ${this.data.hosting === '2' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.hosting='2'; fineCalc.render()">US / Cloud (risqué)</button>
              <button class="fc-opt ${this.data.hosting === '3' ? 'fc-opt-active' : ''}" onclick="fineCalc.data.hosting='3'; fineCalc.render()">Je ne sais pas</button>
            </div>
          </div>
        </div>
        <div class="fc-nav">
          <button class="fc-btn-ghost" onclick="fineCalc.step=2; fineCalc.render()">← Retour</button>
          <button class="fc-btn-primary ${!this.data.dpia ? 'fc-btn-disabled' : ''}" 
                  onclick="fineCalc.next()" ${!this.data.dpia ? 'disabled' : ''}>
            Voir mon risque →
          </button>
        </div>
      </div>
    `;
  }

  renderStep4() {
    // Confirmation step — show what was selected and prepare results
    this.next(); // skip straight to results
  }

  renderResults() {
    const result = this.calculateFines();
    const v = VERTICALS[this.data.vertical];
    const maxFine = result.fines[0];
    const totalStr = this.formatEuros(result.totalExposure);

    // Risk level
    const rm = parseFloat(result.riskMult);
    const riskLevel = rm >= 2.0 ? { label: 'CRITIQUE', color: '#dc2626', bg: '#dc262622' }
      : rm >= 1.5 ? { label: 'ÉLEVÉ', color: '#ef4444', bg: '#ef444422' }
      : rm >= 1.2 ? { label: 'MODÉRÉ', color: '#f59e0b', bg: '#f59e0b22' }
      : { label: 'FAIBLE', color: '#10b981', bg: '#10b98122' };

    this.container.innerHTML = `
      <div class="fc-results">
        <div class="fc-results-header">
          <span class="fc-results-icon">${v.icon}</span>
          <div class="fc-results-title">
            <h3>Votre exposition pour <em>${v.label}</em></h3>
            <div class="fc-risk-badge" style="background:${riskLevel.bg};color:${riskLevel.color}">
              Risque ${riskLevel.label}
            </div>
          </div>
        </div>

        <div class="fc-hero-number">
          <span class="fc-hero-label">Exposition totale estimée</span>
          <span class="fc-hero-val" style="color:${riskLevel.color}">${totalStr}</span>
          <span class="fc-hero-sub">cumul des risques réglementaires identifiés</span>
        </div>

        <div class="fc-fines-list">
          ${result.fines.map(f => `
            <div class="fc-fine-item">
              <div class="fc-fine-left">
                <span class="fc-fine-reg">${f.regulation.label}</span>
                <span class="fc-fine-art">${f.regulation.article}</span>
              </div>
              <div class="fc-fine-right">
                <span class="fc-fine-amount" style="color:${f.estimatedFine > 50000 ? '#ef4444' : '#f59e0b'}">
                  ~${this.formatEuros(f.estimatedFine)}
                </span>
                <span class="fc-fine-prob">Probabilité : ${f.probability}</span>
              </div>
            </div>
          `).join('')}
        </div>

        <div class="fc-breakdown">
          <h4>📋 Ce que cela signifie concrètement</h4>
          <ul>
            ${result.fines.filter(f => f.estimatedFine > 10000).map(f => `
              <li><strong>${f.regulation.label}</strong> : ${f.regulation.description}. Votre exposition est estimée à <strong>~${this.formatEuros(f.estimatedFine)}</strong> compte tenu de votre profil.</li>
            `).join('')}
          </ul>
        </div>

        ${v.horrorCases ? `
        <div class="fc-horror">
          <h4>⚠️ Cas réels comparables</h4>
          ${v.horrorCases.map(c => `
            <div class="fc-horror-case">
              <strong>${c.who}</strong> — ${c.what}
              <div class="fc-horror-fine">→ ${c.fine}</div>
            </div>
          `).join('')}
        </div>
        ` : ''}

        <div class="fc-cta-block">
          <div class="fc-cta-text">
            <strong>Cortex Leman peut réduire votre exposition à zéro.</strong><br>
            Notre audit RGPD-IA identifie chaque gap, chiffre le risque, et déploie un plan d'action conforme.
          </div>
          <div class="fc-cta-actions">
            <a href="mailto:contact@cortex-leman.com?subject=Demande%20audit%20RGPD-IA%20-%20${encodeURIComponent(v.label)}&body=Profil%3A%20${encodeURIComponent(v.label)}%0ACA%3A%20${this.data.revenue}%0AExposition%20estimée%3A%20${encodeURIComponent(totalStr)}%0ARisque%3A%20${encodeURIComponent(riskLevel.label)}%0A%0AJe%20souhaite%20un%20audit%20RGPD-IA%20complet." 
               class="fc-btn-primary fc-cta-btn">
              Demander un audit gratuit →
            </a>
            <button class="fc-btn-ghost" onclick="fineCalc.restart()">Recalculer</button>
          </div>
          <p class="fc-cta-sub">« Les agences IA font de l'automatisation. Les auditeurs font du RGPD. Nous faisons les deux. »</p>
        </div>
      </div>
    `;
  }

  next() {
    this.step++;
    this.render();
    this.container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  restart() {
    this.step = 0;
    this.data = {};
    this.render();
  }
}

// Initialize
let fineCalc;
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('cortex-fine-calculator');
  if (container) {
    fineCalc = new FineCalculator('cortex-fine-calculator');
  }
});
