#!/bin/bash
# -----------------------------
# SOCIALPULSE - Génération Automatisée de Contenu Social
# -----------------------------

set -e

echo "🚀 DÉMARRAGE SOCIALPULSE (mardi/jeudi à 10h)"

# 1. Récupérer les derniers papiers arXiv
echo "🔍 Récupération des derniers papiers arXiv..."
PYTHONPATH=/home/tars/.hermes/skills/cortex-leman/cortex-leman-compliance-generator python3 cortex-leman-compliance-generator/scripts/arxiv_fetcher.py || echo "[!] Warning: échec fetching arXiv"

# 2. Générer les post LinkedIn + images
echo "📝 Génération du contenu..."
PYTHONPATH=/home/tars/.hermes/skills/cortex-leman/cortex-leman-compliance-generator python3 cortex-leman-compliance-generator/scripts/compliance_generator.py \
  --brief "Générer des posts sur les derniers risques IA du 01 avril 2026" \
  --platforms "linkedin" \
  --image_count 2 \
  --use_arxiv true \
  --tone "professional"

# 3. Envoyer via Telegram
echo "📤 Envoi vers Telegram..."
curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
  -H "Content-Type: application/json" \
  -d '{\n    "chat_id": "${TELEGRAM_CHAT_ID}",\n    "text": "✅ Posts LinkedIn générés avec succès. Vérifiez les liens ici : <https://your-frontend-dashboard.com>"\n  }'

echo "🎉 SOCIALPULSE terminé."