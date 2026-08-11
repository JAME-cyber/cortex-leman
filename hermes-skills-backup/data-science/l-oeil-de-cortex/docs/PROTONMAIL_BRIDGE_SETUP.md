# ProtonMail Bridge Setup Guide

Configuration complète de ProtonMail Bridge pour les notifications Email Cortex Leman.

---

## Qu'est-ce que ProtonMail Bridge?

ProtonMail Bridge est une application qui permet d'utiliser le chiffrement ProtonMail avec des clients email locaux (SMTP/IMAP). C'est la méthode recommandée pour envoyer des emails depuis eros1974@protonmail.com.

---

## Installation

### Linux (Ubuntu/Debian)

```bash
# Télécharger ProtonMail Bridge
wget https://proton.me/download/bridge/protonmail-bridge_3.13.0-1_amd64.deb

# Installer
sudo dpkg -i protonmail-bridge_3.13.0-1_amd64.deb

# Réparer les dépendances si nécessaire
sudo apt-get install -f

# Démarrer le service
sudo systemctl enable protonmail-bridge
sudo systemctl start protonmail-bridge
```

### Linux (Arch)

```bash
# Depuis AUR
yay -S protonmail-bridge-bin

# Démarrer le service
sudo systemctl enable protonmail-bridge
sudo systemctl start protonmail-bridge
```

### macOS

```bash
# Installer via Homebrew
brew install --cask protonmail-bridge

# Démarrer le service
brew services start protonmail-bridge
```

### Windows

1. Télécharger depuis: https://proton.me/mail/bridge
2. Installer le .exe
3. Suivre les instructions d'installation

---

## Configuration

### Méthode 1: CLI (Recommandée pour automatisation)

```bash
# Lancer le bridge en mode CLI
protonmail-bridge --cli

# Login
login eros1974@protonmail.com
# Enter password
# Enter 2FA code (si activé)

# Générer un mot de passe bridge
info
# Copy le "Bridge password"
```

Le bridge tournera en background sur `127.0.0.1:1025` par défaut.

### Méthode 2: GUI

```bash
# Lancer le bridge en mode GUI
protonmail-bridge

# Connecter ton compte eros1974@protonmail.com
# Générer un mot de passe bridge
# Copier le mot de passe
```

---

## Configuration Variables d'Environnement

Une fois le bridge configuré, définis les variables:

```bash
# ~/.bashrc ou ~/.zshrc
export SMTP_HOST="127.0.0.1"
export SMTP_PORT="1025"
export SMTP_USER="eros1974@protonmail.com"
export SMTP_PASSWORD="TON_MOT_DE_PASSE_BRIDGE"
export EMAIL_FROM="cortex-leman@protonmail.com"
export EMAIL_TO="eros1974@protonmail.com"
export SMTP_USE_TLS="false"
```

Recharger:
```bash
source ~/.bashrc
```

---

## Vérification

### Test connection

```bash
# Vérifier que le bridge tourne
ps aux | grep protonmail-bridge

# Vérifier le port
netstat -tlnp | grep 1025
```

### Test email

```bash
# Lancer le script de test
chmod +x ~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/test_email.sh
~/.hermes/skills/data-science/l-oeil-de-cortex/scripts/test_email.sh
```

Tu devrais recevoir un email de test à eros1974@protonmail.com.

---

## Configuration Automatique (Systemd)

### Créer le service

```bash
# Créer le fichier de service
sudo nano /etc/systemd/system/protonmail-bridge.service
```

Contenu:
```ini
[Unit]
Description=ProtonMail Bridge
After=network.target

[Service]
User=ton_utilisateur
ExecStart=/usr/bin/protonmail-bridge --noninteractive
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Activer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable protonmail-bridge
sudo systemctl start protonmail-bridge
sudo systemctl status protonmail-bridge
```

---

## Configuration Docker (Alternative)

```bash
# Docker Compose
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  protonmail-bridge:
    image: shenxn/protonmail-bridge
    ports:
      - "1025:25"
      - "1143:143"
    volumes:
      - ./protonmail-data:/root/.protonmail-bridge
    restart: always
EOF

# Démarrer
docker-compose up -d
```

---

## Dépannage

### Le bridge ne démarre pas

```bash
# Vérifier les logs
journalctl -u protonmail-bridge -f

# Redémarrer
sudo systemctl restart protonmail-bridge
```

### Mot de passe bridge incorrect

```bash
# Régénérer le mot de passe
protonmail-bridge --cli
login eros1974@protonmail.com
info
```

### Port déjà utilisé

```bash
# Vérifier ce qui utilise le port
sudo lsof -i :1025

# Changer le port du bridge si nécessaire
```

### Connection refusée

```bash
# Vérifier le firewall
sudo ufw allow 1025

# Vérifier que le bridge écoute
sudo ss -tlnp | grep 1025
```

---

## Sécurité

### Bonnes pratiques

1. **Mot de passe bridge unique**: Différent du mot de passe ProtonMail
2. **Activation 2FA**: Sur ton compte ProtonMail
3. **Logs limités**: Vérifier les logs du bridge régulièrement
4. **Mise à jour**: Garder ProtonMail Bridge à jour

### Permissions

```bash
# Limiter l'accès au port 1025
sudo iptables -A INPUT -p tcp --dport 1025 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 1025 -j DROP
```

---

## Alternatives

Si ProtonMail Bridge ne convient pas:

### Gmail

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="ton_email@gmail.com"
export SMTP_PASSWORD="ton_app_password"
export EMAIL_FROM="ton_email@gmail.com"
export EMAIL_TO="eros1974@protonmail.com"
export SMTP_USE_TLS="true"
```

### SMTP Local (Postfix)

```bash
sudo apt install postfix
export SMTP_HOST="localhost"
export SMTP_PORT="25"
export SMTP_USER=""
export SMTP_PASSWORD=""
export EMAIL_FROM="cortex-leman@localhost"
export EMAIL_TO="eros1974@protonmail.com"
export SMTP_USE_TLS="false"
```

---

## Ressources

- **ProtonMail Bridge Docs**: https://proton.me/mail/bridge
- **ProtonMail GitHub**: https://github.com/ProtonMail/proton-bridge
- **Cortex Leman Docs**: ~/.hermes/skills/data-science/l-oeil-de-cortex/SETUP.md

---

## Support

Problèmes? Vérifier:
1. ProtonMail Bridge est en cours d'exécution
2. Le mot de passe bridge est correct
3. Les variables SMTP sont configurées
4. Le port 1025 est accessible
5. Logs: `journalctl -u protonmail-bridge -f`

---

**Setup complet = Notifications email automatiques pour Cortex Leman!** 🚀
