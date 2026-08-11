# ArXiv Research - L'Oeil de Cortex

## STATUS: IMPLEMENTATION COMPLETE 🚀

Veille technologique automatisée pour Cortex Leman - Production Ready pour validation J2-14.

---

## RÉSUMÉ

Système de veille technologique qui:
1. Scan ArXiv quotidiennement (6h00 CET) pour 6 domains
2. Analyse l'impact via Semantic Scholar API
3. Score la pertinence pour Cortex Leman (0-1)
4. Génère des alertes multi-channel (Email, Telegram, Discord, JSON)
5. Sauvegarde tout en SQLite pour tracking

---

## COMPOSANTS IMPLÉMENTÉS

### 1. Scripts Python (4 scripts)

**arxiv_daily_scan.py** (7,867 bytes)
- Scan 6 domains: gdpr, ai_act, vision, ocr, fr_ch, security
- Parse XML ArXiv API avec URL encoding
- Sauvegarde 65+ papers en SQLite
- Rate limiting: curl avec timeout 90s

**analyze_papers.py** (6,158 bytes)
- Impact analysis via Semantic Scholar API
- Retry exponentiel pour rate limiting (429)
- Citations + influential citations tracking
- Related works discovery

**score_relevance.py** (7,689 bytes)
- Scoring 0-1 basé sur 30 keywords Cortex Leman
- 6 domains pondérés (25%, 25%, 15%, 15%, 10%, 10%)
- Bonus multi-domain (10%)
- Top papers identification

**alert_papers.py** (23,016 bytes)
- Alertes multi-channel: Email + Telegram + Discord + JSON
- HTML email responsive avec branding Cortex Leman
- Markdown format Telegram
- Discord embeds riches
- JSON export pour Grafana
- Database: 3 alerts sauvegardées

### 2. Infrastructure

**Database SQLite** (~/.hermes/data/hermes_research.db, 164KB)
- Table arxiv_papers: 65 papers with metadata
- Table paper_alerts: 3 alerts saved
- Index: domain, published_date, relevance_score

**Cron Job** (Active)
```
6h00: Scan ArXiv
6h30: Analyse citations
7h00: Score relevance
7h30: Alertes journalières
Monday 9h00: Rapport hebdomadaire
```

**Logs** (~/.hermes/cron/logs/)
- arxiv_scan.log
- arxiv_analyze.log
- arxiv_score.log
- arxiv_alert.log
- arxiv_weekly.log

### 3. Channels de Notification

**Email** ✅ NOUVEAU
- HTML responsive design
- Header gradient + branding
- Stats en 3 colonnes
- Sections: Critiques, High Relevance, Nouveaux
- Destinataire: eros1974@protonmail.com
- SMTP: ProtonMail Bridge (127.0.0.1:1025) ou Gmail (smtp.gmail.com:587)

**Telegram**
- Markdown format compact
- Mobile-friendly
- URLs cliquables
- Emoji-rich

**Discord**
- Rich embeds
- Color-coded alerts
- Auto-timestamps
- Team collaboration

**JSON Reports**
- Daily reports: ~/.hermes/data/arxiv_report_YYYYMMDD.json
- Pour intégration Grafana (future)

### 4. Documentation

**SETUP.md** - Guide rapide setup
- Configuration notifications (Email, Telegram, Discord)
- Test commands
- Troubleshooting

**PROTONMAIL_BRIDGE_SETUP.md** - Guide complet ProtonMail
- Installation Linux/macOS/Windows
- Configuration CLI/GUI
- Systemd service setup
- Docker alternative
- Dépannage

**notification_config.sh** - Template configuration
- Telegram: BOT_TOKEN + CHAT_ID
- Discord: WEBHOOK_URL
- Email: SMTP_HOST/PORT + USER + PASSWORD + FROM/TO

**test_email.sh** - Script test email
- Vérifie variables SMTP
- Test connection nc
- Envoie email de test HTML
- Validation configuration

---

## MÉTRIQUES ACTUELLES

### Database
- **Papers scannés**: 65
- **Alertes générées**: 3
- **Database size**: 164KB

### Performance
- **Scan time**: ~90s pour 65 papers (6 domains)
- **Score time**: ~5s pour 65 papers
- **Alerts generation**: ~2s pour 3 papers

### Relevance Distribution
- **Max relevance**: 0.18
- **Avg relevance**: 0.028
- **High relevance (>0.15)**: 3 papers
- **Top papers**:
  1. [0.18] 2512.22060v1 (security) - Toward Secure and Compliant AI
  2. [0.17] 2501.09182v1 (fr_ch) - Cross-Border Compliance and Trust
  3. [0.17] 2503.20464v1 (fr_ch) - Privacy Compliance in Cross-border Data

### Domains Coverage
- gdpr: 10 papers, avg relevance 0.039
- ai_act: 10 papers, avg relevance 0.008
- vision: 15 papers, avg relevance 0.009
- ocr: 10 papers, avg relevance 0.000
- fr_ch: 10 papers, avg relevance 0.060
- security: 10 papers, avg relevance 0.057

---

## THRESHOLDS CONFIGURÉS

```
high_impact: >50 citations
high_relevance: >0.15 (top 10% basé sur données réelles)
recent: <7 jours
```

**Note**: Thresholds calibrés sur données réelles (65 papers testés).

---

## SETUP RAPIDE

### 1. Configurer ProtonMail Bridge (si pas déjà fait)

```bash
# Télécharger et installer
wget https://proton.me/download/bridge/protonmail-bridge_3.13.0-1_amd64.deb
sudo dpkg -i protonmail-bridge_3.13.0-1_amd64.deb

# Configurer avec eros1974@protonmail.com
protonmail-bridge --cli
login eros1974@protonmail.com
info  # Copier le bridge password
```

### 2. Configurer variables d'environnement

```bash
# Copier template
cp ~/.hermes/skills/data-science/l-oeil-de-cortex/config/notification_config.sh ~/.hermes/skills/data-science/l-oeil-de-cortex/.env

# Editer avec tes credentials
nano ~/.hermes/skills/data-science/l-oeil-de-cortex/.env

# Remplacer:
# SMTP_PASSWORD="TON_MOT_DE_PASSE_BRIDGE"

# Source
source ~/.hermes/skills/data-science/l-oeil-de-cortex/.env
```

### 3. Test email

```bash
chmod +x ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/test_email.sh
~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/test_email.sh
```

Tu devrais recevoir un email de test à eros1974@protonmail.com.

### 4. Vérifier cron job

```bash
crontab -l | grep arxiv
# Doit montrer les 5 jobs actifs
```

### 5. Test manuel complet

```bash
# Scan
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/arxiv_daily_scan.py

# Analyse (optionnel - nécessite Semantic Scholar API)
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/analyze_papers.py

# Score
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/score_relevance.py

# Alertes
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/alert_papers.py
```

---

## WORKFLOW QUOTIDIEN (AUTOMATISÉ)

1. **6h00 CET** - Scan ArXiv
   - 6 domains scannés
   - 60+ papers récupérés
   - Database mise à jour

2. **6h30 CET** - Analyse citations
   - Semantic Scholar API
   - Citations tracked
   - Impact scores calculés

3. **7h00 CET** - Score relevance
   - Keywords matching
   - Scores 0-1 calculés
   - Top papers identifiés

4. **7h30 CET** - Alertes multi-channel
   - Email HTML → eros1974@protonmail.com
   - Telegram Markdown → Mobile
   - Discord Embeds → Team
   - JSON → Grafana (future)

5. **Monday 9h00 CET** - Rapport hebdomadaire
   - Résumé des 7 derniers jours
   - Trends analysis
   - Recommandations

---

## INTEGRATION CORTEX LEMAN

### Agents concernés

**L'Oeil de Cortex** (Data Visionary)
- Papers vision/relevantes
- OCR/Deepfake detection papers
- Document authentication updates

**Le Gardien des Normes** (Compliance Officer)
- GDPR/RGPD legal updates
- AI Act regulation changes
- Security standards (NIST/OWASP/ISO)
- Cross-border compliance FR-CH

**L'Architecte Lémanique** (CSO)
- Strategic review des high impact papers
- Business impact assessment
- Priorité d'implémentation

**Le Narrateur Augmenté** (Brand UI)
- Visual reports generation
- Client-facing documentation
- Dashboard data

**L'Ingénieur de Flux** (Automation)
- Integration skills updates
- New controls implementation
- Workflow automation

### Alertes workflow

Pour chaque paper important:
1. **Extraction** → Full PDF analysis
2. **Summary** → L'Oeil de Cortex generates
3. **Review** → Le Gardien des Normes validates
4. **Discussion** → L'Architecte Lémanique assesses
5. **Implementation** → L'Ingénieur de Flux deploys

---

## NEXT STEPS (POST-VALIDATION)

### Short term (J2-14)
1. ✅ Ajuster thresholds basés sur feedback
2. ⏸️ Activer Grafana dashboard monitoring
3. ⏸️ Intégration workflow automatique avec agents

### Medium term (validation complète)
4. ⏸️ Export PDF pour clients (rapports audit)
5. ⏸️ API REST pour integration externe
6. ⏸️ ML model pour relevance prediction (basé sur historical data)

### Long term (production)
7. ⏸️ Multi-source (autres que ArXiv: SSRN, IEEE, etc.)
8. ⏸️ Real-time alerts (streaming au lieu de batch)
9. ⏸️ Knowledge graph des citations et connexions

---

## SUPPORT

### Logs
```bash
# Tous les logs
ls -lh ~/.hermes/cron/logs/arxiv_*.log

# Logs en temps réel
tail -f ~/.hermes/cron/logs/arxiv_alert.log
```

### Database queries
```bash
sqlite3 ~/.hermes/data/hermes_research.db

-- Top papers par relevance
SELECT arxiv_id, domain, relevance_score, citation_count
FROM arxiv_papers
ORDER BY relevance_score DESC
LIMIT 10;

-- Alertes récentes
SELECT * FROM paper_alerts
ORDER BY created_at DESC
LIMIT 20;

-- Stats par domain
SELECT domain, COUNT(*), AVG(relevance_score)
FROM arxiv_papers
GROUP BY domain;
```

### Troubleshooting

**Scan échoue**
```bash
# Vérifier connexion ArXiv
curl -s "https://export.arxiv.org/api/query?search_query=GDPR&cat:cs.CR" | head -n 20
```

**Analyse échoue (429)**
```bash
# Rate limit Semantic Scholar - attendre et retry
# Le script a déjà retry exponentiel (5s, 10s, 20s)
```

**Email échoue**
```bash
# Vérifier ProtonMail Bridge
ps aux | grep protonmail-bridge
netstat -tlnp | grep 1025

# Test email
~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/test_email.sh
```

**Cron ne tourne pas**
```bash
# Vérifier cron
crontab -l

# Vérifier service cron
sudo systemctl status cron

# Logs cron
grep CRON /var/log/syslog
```

---

## RÉFÉRENCES

- **ArXiv API**: https://arxiv.org/help/api/index.html
- **Semantic Scholar API**: https://www.semanticscholar.org/product/api
- **ProtonMail Bridge**: https://proton.me/mail/bridge
- **Skills**: l-oeil-de-cortex, le-gardien-des-normes, l-architecte-lemanique

---

## RÉCAPITULATIF

✅ **4 Scripts Python** - Scan, Analyse, Score, Alertes
✅ **1 Database SQLite** - 65 papers, 3 alerts
✅ **5 Cron Jobs** - Automatisation complète 6h00-9h00 CET
✅ **4 Channels Notification** - Email + Telegram + Discord + JSON
✅ **Email HTML Responsive** - eros1974@protonmail.com
✅ **Thresholds calibrés** - Basés sur données réelles
✅ **Documentation complète** - SETUP + PROTONMAIL_BRIDGE + TROUBLESHOOTING
✅ **Test email script** - Validation configuration

**SYSTEM READY FOR PRODUCTION VALIDATION** 🚀

---

*L'Oeil de Cortex + ArXiv = Veille Technologique Automatisée au Niveau Enterprise.*

*Tu scannes, tu scores, tu alertes. Cortex Leman reste state-of-the-art.*
