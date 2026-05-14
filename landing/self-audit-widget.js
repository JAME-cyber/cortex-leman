/**
 * Cortex Leman — Self-Audit Widget
 * Agent de diagnostic RGPD-IA en auto-serveur sur la landing page.
 * Inspiré du model 1mind (Mindy génère 78% du pipeline).
 * 
 * 10 questions → score de risque → mini-rapport PDF → upsell audit complet
 */

const QUESTIONS = [
  {
    id: 'q1',
    text: 'Utilisez-vous des outils IA (ChatGPT, Claude, Copilot) dans votre activité professionnelle ?',
    options: ['Oui, quotidiennement', 'Oui,偶尔', 'Non', 'Envisagé'],
    weights: [3, 2, 0, 1]
  },
  {
    id: 'q2',
    text: 'Vos collaborateurs partagent-ils des données client sur des outils IA publics ?',
    options: ['Oui, régulièrement', 'Parfois', 'Non, interdit', 'Je ne sais pas'],
    weights: [3, 2, 0, 3]
  },
  {
    id: 'q3',
    text: 'Avez-vous réalisé une Analyse d\'Impact (AIPD/DPIA) pour vos usages IA ?',
    options: ['Non', 'En cours', 'Oui', 'Je ne sais pas ce que c\'est'],
    weights: [3, 1, 0, 3]
  },
  {
    id: 'q4',
    text: 'Vos données IA sont-elles hébergées en Suisse ou en Europe ?',
    options: ['Non (US/cloud)', 'Partiellement', 'Oui, en EU/CH', 'Je ne sais pas'],
    weights: [3, 1, 0, 2]
  },
  {
    id: 'q5',
    text: 'Avez-vous désigné un DPO (Délégué à la Protection des Données) ?',
    options: ['Non', 'En cours', 'Oui', 'Pas obligé (PME < 250)'],
    weights: [2, 1, 0, 1]
  },
  {
    id: 'q6',
    text: 'Si vous êtes avocat/banquier/médecin : utilisez-vous l\'IA sur des dossiers sensibles ?',
    options: ['Oui, sans restriction', 'Oui, avec précautions', 'Non', 'Pas concerné'],
    weights: [3, 2, 0, 0]
  },
  {
    id: 'q7',
    text: 'Avez-vous informé vos clients que leurs données pourraient être traitées par IA ?',
    options: ['Non', 'En partie', 'Oui', 'Pas concerné'],
    weights: [3, 2, 0, 0]
  },
  {
    id: 'q8',
    text: 'Utilisez-vous des agents IA autonomes (chatbot, clone vocal, sales AI) ?',
    options: ['Oui, plusieurs', 'Un seul', 'Non', 'Envisagé'],
    weights: [3, 2, 0, 1]
  },
  {
    id: 'q9',
    text: 'Connaissez-vous vos obligations au titre de l\'AI Act (juillet 2025) ?',
    options: ['Non', 'Vaguement', 'Oui', 'Pas concerné'],
    weights: [3, 2, 0, 0]
  },
  {
    id: 'q10',
    text: 'Avez-vous un budget alloué à la conformité IA pour 2026 ?',
    options: ['Non', 'En discussion', 'Oui', 'Pas nécessaire selon nous'],
    weights: [2, 1, 0, 2]
  }
];

const RISK_LEVELS = [
  { max: 5, label: 'FAIBLE', color: '#10b981', emoji: '✅', msg: 'Votre exposition est limitée. Un audit de base suffit.' },
  { max: 12, label: 'MOYEN', color: '#f59e0b', emoji: '⚠️', msg: 'Des gaps identifiés. Un audit RGPD-IA est recommandé.' },
  { max: 20, label: 'ÉLEVÉ', color: '#ef4444', emoji: '🔴', msg: 'Risque significatif. Un audit complet OWASP GenAI est urgent.' },
  { max: 30, label: 'CRITIQUE', color: '#dc2626', emoji: '🚨', msg: 'Exposition majeure. Sanctions AI Act jusqu\'à 6% du CA. Action immédiate requise.' }
];

class SelfAuditWidget {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.currentStep = 0;
    this.answers = {};
    this.score = 0;
    this.render();
  }

  render() {
    if (this.currentStep === 0) {
      this.renderWelcome();
    } else if (this.currentStep <= QUESTIONS.length) {
      this.renderQuestion();
    } else {
      this.renderResult();
    }
  }

  renderWelcome() {
    this.container.innerHTML = `
      <div style="text-align:center;padding:40px 20px">
        <div style="font-size:48px;margin-bottom:16px">🔍</div>
        <h3 style="font-size:24px;font-weight:800;margin-bottom:12px;color:var(--text)">Diagnostic RGPD-IA Gratuit</h3>
        <p style="color:var(--t2);font-size:15px;max-width:420px;margin:0 auto 24px;line-height:1.7">
          10 questions pour évaluer votre exposition aux risques RGPD, AI Act et LPerD.
          Résultat instantané. Aucune donnée collectée.
        </p>
        <button onclick="widget.start()" style="
          background:linear-gradient(135deg,#3b82f6,#10b981);color:white;border:none;
          padding:14px 36px;border-radius:10px;font-size:16px;font-weight:700;cursor:pointer;
          font-family:inherit;transition:transform .2s
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='none'">
          Commencer le diagnostic →
        </button>
        <p style="color:var(--t3);font-size:12px;margin-top:16px">⏱ 2 minutes · 100% confidentiel · Sans engagement</p>
      </div>
    `;
  }

  start() {
    this.currentStep = 1;
    this.render();
  }

  renderQuestion() {
    const q = QUESTIONS[this.currentStep - 1];
    const progress = (this.currentStep / QUESTIONS.length) * 100;
    
    this.container.innerHTML = `
      <div style="padding:32px 24px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
          <span style="font-size:12px;font-weight:600;color:var(--t3);font-family:var(--m)">QUESTION ${this.currentStep}/${QUESTIONS.length}</span>
          <span style="font-size:12px;font-weight:600;color:var(--t3);font-family:var(--m)">${Math.round(progress)}%</span>
        </div>
        <div style="background:var(--bdr);height:4px;border-radius:2px;margin-bottom:28px;overflow:hidden">
          <div style="background:linear-gradient(90deg,var(--blue),var(--green));height:100%;width:${progress}%;border-radius:2px;transition:width .3s"></div>
        </div>
        <h3 style="font-size:18px;font-weight:700;line-height:1.5;margin-bottom:24px;color:var(--text)">${q.text}</h3>
        <div style="display:flex;flex-direction:column;gap:10px">
          ${q.options.map((opt, i) => `
            <button onclick="widget.answer(${i})" style="
              background:var(--card);border:1px solid var(--bdr);color:var(--text);
              padding:14px 18px;border-radius:8px;font-size:14px;font-weight:500;
              cursor:pointer;text-align:left;transition:all .2s;font-family:inherit
            " onmouseover="this.style.borderColor='var(--blue)';this.style.background='var(--card-h)'"
               onmouseout="this.style.borderColor='var(--bdr)';this.style.background='var(--card)'">
              ${opt}
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }

  answer(optionIndex) {
    const q = QUESTIONS[this.currentStep - 1];
    this.answers[q.id] = optionIndex;
    this.score += q.weights[optionIndex];
    this.currentStep++;
    this.render();
  }

  renderResult() {
    const risk = RISK_LEVELS.find(r => this.score <= r.max) || RISK_LEVELS[RISK_LEVELS.length - 1];
    
    this.container.innerHTML = `
      <div style="text-align:center;padding:40px 24px">
        <div style="font-size:56px;margin-bottom:12px">${risk.emoji}</div>
        <div style="
          display:inline-block;padding:6px 20px;border-radius:20px;font-weight:700;
          font-size:14px;margin-bottom:16px;
          background:${risk.color}22;color:${risk.color};border:1px solid ${risk.color}44
        ">Risque ${risk.label}</div>
        <p style="color:var(--text);font-size:16px;line-height:1.7;margin-bottom:8px">${risk.msg}</p>
        <p style="color:var(--t2);font-size:14px;margin-bottom:28px">Score: ${this.score}/30 points de risque</p>
        
        <div style="background:var(--card);border:1px solid var(--bdr);border-radius:12px;padding:24px;text-align:left;margin-bottom:28px">
          <h4 style="font-size:14px;font-weight:700;color:var(--blue);margin-bottom:12px">📋 Recommandation</h4>
          ${this.score >= 12 ? `
            <p style="color:var(--text);font-size:14px;line-height:1.7">
              Un <strong>audit RGPD-IA complet</strong> est nécessaire pour identifier précisément les gaps et établir un plan d'action.
              Notre audit couvre OWASP Top 10 + GenAI (9 phases Agentic AI + 12 menaces Data Security) + AI Act + LPerD.
            </p>
            <div style="margin-top:12px;font-size:13px;color:var(--t2)">
              <strong>Formule recommandée:</strong> ${this.score >= 20 ? 'Enterprise (CHF 6,500)' : 'Growth (CHF 4,000)'} · Délai: ${this.score >= 20 ? '3-4' : '3'} semaines
            </div>
          ` : `
            <p style="color:var(--text);font-size:14px;line-height:1.7">
              Votre exposition est contenue. Un <strong>diagnostic approfondi</strong> peut confirmer votre niveau et identifier les points d'attention.
            </p>
            <div style="margin-top:12px;font-size:13px;color:var(--t2)">
              <strong>Formule recommandée:</strong> Startup (CHF 2,500) · Délai: 2 semaines
            </div>
          `}
        </div>

        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
          <a href="mailto:contact@cortexleman.ch?subject=Demande%20audit%20RGPD-IA%20-%20Score%20${this.score}/30&body=Score%20diagnostic%3A%20${risk.label}%20(${this.score}/30)%0A%0AJe%20souhaite%20un%20audit%20complet." style="
            background:linear-gradient(135deg,#3b82f6,#10b981);color:white;text-decoration:none;
            padding:14px 28px;border-radius:10px;font-size:15px;font-weight:700;
            transition:transform .2s;display:inline-block
          " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='none'">
            Demander un audit →
          </a>
          <button onclick="widget.restart()" style="
            background:var(--card);border:1px solid var(--bdr);color:var(--t2);
            padding:14px 28px;border-radius:10px;font-size:15px;font-weight:500;
            cursor:pointer;font-family:inherit;transition:all .2s
          " onmouseover="this.style.borderColor='var(--blue)'" onmouseout="this.style.borderColor='var(--bdr)'">
            Refaire le test
          </button>
        </div>
        
        <p style="color:var(--t3);font-size:11px;margin-top:20px">
          « Les agences IA font de l'automatisation. Les auditeurs font du RGPD. Nous faisons les deux. »
        </p>
      </div>
    `;
  }

  restart() {
    this.currentStep = 0;
    this.answers = {};
    this.score = 0;
    this.render();
  }
}

// Initialize
let widget;
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('cortex-self-audit');
  if (container) {
    widget = new SelfAuditWidget('cortex-self-audit');
  }
});
