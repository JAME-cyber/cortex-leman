# Hermes Harness — Disaster Recovery Guide

En cas de panne Tars, voici la procédure pour restaurer un Hermes Agent complet.

## 1. Prérequis
- Installer Hermes Agent sur la nouvelle machine
- Avoir accès au repo GitHub `JAME-cyber/cortex-leman`

## 2. Restoration

```bash
# Clone
git clone https://github.com/JAME-cyber/cortex-leman.git /tmp/recovery
cd /tmp/recovery

# Restore config (SANITIZED — voir section secrets plus bas)
cp harness-backup/config.yaml ~/.hermes/config.yaml

# Restore memory
cp harness-backup/memory/MEMORY.md ~/.hermes/memories/
cp harness-backup/memory/USER.md ~/.hermes/memories/

# Restore autonomy policy
cp harness-backup/policies/autonomy.yaml ~/.hermes/agent-harness/policies/

# Restore harness configs
mkdir -p ~/.hermes/agent-harness/workflows
cp -r harness-backup/harness/* ~/.hermes/agent-harness/

# Restore scripts
cp -r harness-backup/scripts/* ~/.hermes/scripts/

# Restore custom skills
cp -r hermes-skills-backup/* ~/.hermes/skills/

# Restore databases (session history, memory store, kanban, research)
mkdir -p ~/.hermes/data
cp harness-backup/db/state.db ~/.hermes/
cp harness-backup/db/memory_store.db ~/.hermes/
cp harness-backup/db/verification_evidence.db ~/.hermes/
cp harness-backup/db/kanban.db ~/.hermes/
cp harness-backup/db/data/* ~/.hermes/data/
cp harness-backup/db/cron-executions.db ~/.hermes/cron/executions.db

# Restore cron jobs
cp harness-backup/cron-jobs.json ~/.hermes/cron/jobs.json
```

## 3. Secrets à restaurer manuellement

Le config.yaml est SANITIZED. Les secrets doivent être restaurés depuis le vault ou le keyring.

### Vault keys (voir vault-keys.txt pour la liste complète)
```bash
python3 ~/.hermes/vault/vault.py set CF_TOKEN "<valeur>"
python3 ~/.hermes/vault/vault.py set CF_ACCOUNT_ID "<valeur>"
python3 ~/.hermes/vault/vault.py set GH_JAME_TOKEN "<valeur>"
# ... voir vault-keys.txt
```

### config.yaml — restaurer manuellement
Les champs suivants ont été redacted dans le backup:
- API keys (tous providers LLM: OpenRouter, ZAI, etc.)
- Tokens (Telegram, etc.)
- OAuth secrets (Google/YouTube)

### OAuth credentials
- `~/african-heroes/CHANNEL/upload_pack/client_secret.json` — Google OAuth pour YouTube upload
- `~/.config/youtubeuploader/broadcast.goauth` — Token OAuth YouTube

## 4. Vérification

```bash
# Check Hermes démarre
hermes config show

# Check cron jobs
hermes cron list

# Check skills
hermes skills list

# Check memory
cat ~/.hermes/memories/MEMORY.md
```

## 5. Ce qui est PERDU (non backupable)
- **Session history récente** (state.db contient l'historique avant le backup)
- **Cache** (browser snapshots, terminal outputs — régénérable)
- **Stock skills** (129 skills — réinstallables via `hermes setup` / plugins)
