#!/bin/bash
#
# Configuration des notifications ArXiv Cortex Leman
# Telegram et/ou Discord
#

# ======================
# TELEGRAM NOTIFICATIONS
# ======================
# 1. Créer un bot Telegram via @BotFather
# 2. Copier le token (format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
# 3. Trouver ton chat_id (envoyer un message à ton bot et visiter: https://api.telegram.org/bot<TOKEN>/getUpdates)
# 4. Désactiver les lignes ci-dessous et remplacer par tes valeurs

export TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
export TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID_HERE"

# ======================
# Discord Notifications
# ======================
# 1. Aller sur ton serveur Discord > Channel Settings > Integrations > Webhooks
# 2. Créer un nouveau webhook
# 3. Copier l'URL du webhook
# 4. Désactiver la ligne ci-dessous et remplacer par ton URL

export DISCORD_WEBHOOK_URL="YOUR_DISCORD_WEBHOOK_URL_HERE"

# ======================
# EMAIL NOTIFICATIONS (SMTP)
# ======================
#
# OPTION 1: ProtonMail Bridge (recommandé pour eros1974@protonmail.com)
# 1. Télécharger et installer ProtonMail Bridge: https://proton.me/mail/bridge
# 2. Configurer le bridge avec ton compte Proton
# 3. Le bridge tourne sur 127.0.0.1:1025 par défaut
# 4. Utiliser ces credentials:
export SMTP_HOST="127.0.0.1"
export SMTP_PORT="1025"
export SMTP_USER="eros1974@protonmail.com"
export SMTP_PASSWORD="YOUR_PROTONMAIL_BRIDGE_PASSWORD"
export EMAIL_FROM="cortex-leman@protonmail.com"
export EMAIL_TO="eros1974@protonmail.com"
export SMTP_USE_TLS="false"  # ProtonMail Bridge ne utilise pas TLS

#
# OPTION 2: Gmail (alternative simple)
# 1. Activer 2FA sur ton compte Gmail
# 2. Générer un App Password: https://myaccount.google.com/apppasswords
# 3. Utiliser ces credentials à la place:
# export SMTP_HOST="smtp.gmail.com"
# export SMTP_PORT="587"
# export SMTP_USER="ton_email@gmail.com"
# export SMTP_PASSWORD="ton_app_password"
# export EMAIL_FROM="ton_email@gmail.com"
# export EMAIL_TO="eros1974@protonmail.com"
# export SMTP_USE_TLS="true"

# ======================
# ACTIVATION
# ======================
# Pour activer les notifications:
# 1. Copie ce fichier dans ~/.hermes/skills/data-science/l-oeil-de-cortex/.env
# 2. Source le fichier avant de lancer les scripts:
#    source ~/.hermes/skills/data-science/l-oeil-de-cortex/config/notification_config.sh
# 3. Ou ajoute à ~/.bashrc pour persistance:
#    echo "source ~/.hermes/skills/data-science/l-oeil-de-cortex/config/notification_config.sh" >> ~/.bashrc

# ======================
# TEST
# ======================
# Pour tester les notifications:
# python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/alert_papers.py
