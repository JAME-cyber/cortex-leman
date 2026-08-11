# ArXiv Research - L'Oeil de Cortex

## Status: READY FOR PRODUCTION

### Ce qui est fait

✅ **4 Scripts Python**:
- `arxiv_daily_scan.py` - Scan ArXiv quotidien (65+ papers)
- `analyze_papers.py` - Impact analysis Semantic Scholar (avec retry/backoff)
- `score_relevance.py` - Scoring 0-1 pour Cortex Leman
- `alert_papers.py` - Alerting + reporting quotidien

✅ **Base de données SQLite**: `~/.hermes/data/hermes_research.db`
- Tables: `arxiv_papers`, `paper_alerts`
- Index: domain, date, relevance

✅ **Cron job**: Automatisé (scan 6h00, alertes 7h30 CET)

✅ **Thresholds ajustés**: high_relevance = 0.15 (basé sur données réelles)

✅ **Notifications**: Telegram et Discord (prêtes à configurer)

---

## Setup Rapide

### 1. Configurer les notifications (optionnel)

**Email (recommandé pour eros1974@protonmail.com):**

Option 1: ProtonMail Bridge
1. Télécharger ProtonMail Bridge: https://proton.me/mail/bridge
2. Installer et configurer avec ton compte eros1974@protonmail.com
3. Le bridge tourne sur 127.0.0.1:1025 par défaut
4. Configurer les variables d'environnement:
   ```bash
   export SMTP_HOST="127.0.0.1"
   export SMTP_PORT="1025"
   export SMTP_USER="eros1974@protonmail.com"
   export SMTP_PASSWORD="ton_bridge_password"
   export EMAIL_FROM="cortex-leman@protonmail.com"
   export EMAIL_TO="eros1974@protonmail.com"
   export SMTP_USE_TLS="false"
   ```

Option 2: Gmail (alternative)
1. Activer 2FA sur Gmail
2. Générer un App Password: https://myaccount.google.com/apppasswords
3. Configurer:
   ```bash
   export SMTP_HOST="smtp.gmail.com"
   export SMTP_PORT="587"
   export SMTP_USER="ton_email@gmail.com"
   export SMTP_PASSWORD="ton_app_password"
   export EMAIL_FROM="ton_email@gmail.com"
   export EMAIL_TO="eros1974@protonmail.com"
   export SMTP_USE_TLS="true"
   ```

**Telegram:**
1. Bot @BotFather → /newbot → copier le token
2. Envoyer un message au bot → visiter https://api.telegram.org/bot<TOKEN>/getUpdates → trouver "chat_id"

**Discord:**
1. Channel Settings → Integrations → Webhooks → Create Webhook → copier l'URL

**Pour configurer tout:**
```bash
# Copier le template
cp ~/.hermes/skills/data-science/l-oeil-de-cortex/config/notification_config.sh ~/.hermes/skills/data-science/l-oeil-de-cortex/.env

# Editer avec tes credentials
nano ~/.hermes/skills/data-science/l-oeil-de-cortex/.env

# Sourcing pour la session courante
source ~/.hermes/skills/data-science/l-oeil-de-cortex/.env
```

### 2. Vérifier le cron job

```bash
crontab -l
# Doit montrer le cortex-leman-arxiv.cron activé
```

### 3. Test manuel

```bash
# Scanner maintenant
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/arxiv_daily_scan.py

# Analyser
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/analyze_papers.py

# Scorer
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/score_relevance.py

# Alertes
python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/alert_papers.py
```

---

## Métriques Actuelles

- Papers scannés: 65
- Domains: 6 (gdpr, ai_act, vision, ocr, fr_ch, security)
- High relevance (>0.15): 3 papers
- Avg relevance: 0.028
- Max relevance: 0.18

---

## Structure des Alertes

### Channels de notification

**Email** (HTML, responsive design):
- Header gradient avec logo Cortex Leman
- Stats en grille (3 colonnes)
- Sections: Critiques, High Relevance, Nouveaux
- Badges colorés par type d'alerte
- Footer avec timestamp et prochain scan
- Destinataire par défaut: eros1974@protonmail.com

**Telegram** (Markdown format):
- Alertes compactes mobile-friendly
- Sections clairement délimitées
- URLs cliquables pour les papers
- Emoji-rich pour meilleure lisibilité

**Discord** (Embeds):
- Embeds riches avec colors
- Fields pour chaque paper
- Timestamp automatique
- Format adapté au chat

### Thresholds

```
high_impact: >50 citations
high_relevance: >0.15 (top 10%)
recent: <7 jours
```

### Types d'alertes

- **HIGH_IMPACT**: Papers avec beaucoup de citations
- **HIGH_RELEVANCE**: Papers pertinents pour Cortex Leman
- **RECENT**: Papers publiés <7 jours
- **CRITICAL**: HIGH_IMPACT + HIGH_RELEVANCE

---

## Logs

```bash
# Voir les logs cron
tail -f ~/.hermes/cron/logs/arxiv_*.log

# Voir les alertes sauvegardées
sqlite3 ~/.hermes/data/hermes_research.db "SELECT * FROM paper_alerts ORDER BY created_at DESC LIMIT 10"
```

---

## Next Steps (post-validation)

1. ✅ Ajuster thresholds basés sur feedback
2. ⏸️ Dashboard Grafana (monitoring visuel)
3. ⏸️ Intégration avec Le Gardien des Normes (workflow automatique)
4. ⏸️ Export PDF pour clients (rapports audit)

---

## Support

Problèmes? Check logs:
- `~/.hermes/cron/logs/arxiv_scan.log`
- `~/.hermes/cron/logs/arxiv_analyze.log`
- `~/.hermes/cron/logs/arxiv_score.log`
- `~/.hermes/cron/logs/arxiv_alert.log`

---

**L'Oeil de Cortex + ArXiv = Veille Technologique Automatisée Enterprise**

*Tu scannes, tu scores, tu alertes. Cortex Leman reste state-of-the-art.*
