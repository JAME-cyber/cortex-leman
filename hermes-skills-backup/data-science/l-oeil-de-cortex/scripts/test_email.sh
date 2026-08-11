#!/bin/bash
#
# Test Email Configuration - ArXiv Cortex Leman
# Script pour vérifier que l'envoi d'email fonctionne
#

echo "=================================="
echo "Test Email Configuration"
echo "=================================="
echo ""

# Check variables
if [ -z "$SMTP_HOST" ] || [ -z "$SMTP_PORT" ] || [ -z "$SMTP_USER" ] || [ -z "$SMTP_PASSWORD" ]; then
    echo "❌ Variables SMTP non configurées"
    echo ""
    echo "Configure les variables:"
    echo "  export SMTP_HOST=..."
    echo "  export SMTP_PORT=..."
    echo "  export SMTP_USER=..."
    echo "  export SMTP_PASSWORD=..."
    echo ""
    exit 1
fi

echo "✅ Variables SMTP configurées:"
echo "   Host: $SMTP_HOST"
echo "   Port: $SMTP_PORT"
echo "   User: $SMTP_USER"
echo "   From: ${EMAIL_FROM:-non configuré}"
echo "   To: ${EMAIL_TO:-non configuré}"
echo ""

# Test connection
echo "🔍 Test connection SMTP..."
if command -v nc &> /dev/null; then
    if nc -z -w5 $SMTP_HOST $SMTP_PORT 2>/dev/null; then
        echo "✅ Connection réussie à $SMTP_HOST:$SMTP_PORT"
    else
        echo "❌ Connection échouée à $SMTP_HOST:$SMTP_PORT"
        echo "   Vérifie que ProtonMail Bridge tourne"
        exit 1
    fi
else
    echo "⚠️  nc non disponible - impossible de tester la connection"
fi
echo ""

# Send test email via Python
echo "📧 Envoi email de test..."

python3 << 'EOF'
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "1025"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "cortex-leman@protonmail.com")
EMAIL_TO = os.environ.get("EMAIL_TO", "eros1974@protonmail.com")
SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "false").lower() == "true"

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = "[CORTEX LEMAN] Test Email Configuration"
    
    # HTML body
    html = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #667eea;">🔍 Test Email Configuration</h2>
        <p><strong>Cortex Leman - ArXiv Research</strong></p>
        <hr>
        <p>Si tu reçois cet email, la configuration SMTP est correcte!</p>
        <p>Prochain scan ArXiv: Demain à 6h00 CET</p>
        <hr>
        <p style="color: #999; font-size: 12px;">
            Test envoyé le """ + os.popen('date').read().strip() + """<br>
            <strong>Cortex Leman - Veille Technologique Automatisée</strong>
        </p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # Connect and send
    if SMTP_USE_TLS:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print("✅ Email envoyé avec succès à:", EMAIL_TO)
    
except Exception as e:
    print("❌ Erreur envoi email:", str(e))
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Test email réussi!"
    echo "=================================="
    echo ""
    echo "Vérifie ta boîte mail pour recevoir l'email de test."
    echo ""
    echo "Prochaines étapes:"
    echo "1. Vérifie que l'email de test est bien arrivé"
    echo "2. Lance le scan ArXiv:"
    echo "   python3 ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/arxiv_daily_scan.py"
    echo ""
else
    echo ""
    echo "=================================="
    echo "❌ Test email échoué"
    echo "=================================="
    echo ""
    echo "Vérifie:"
    echo "1. ProtonMail Bridge est en cours d'exécution"
    echo "2. Le mot de passe bridge est correct"
    echo "3. Les variables SMTP sont correctes"
    echo ""
    exit 1
fi
