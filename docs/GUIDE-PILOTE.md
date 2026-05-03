# Cortex Leman v5 — Guide Démarrage Pilote

## Bienvenue dans Cortex Leman

Vous avez reçu un accès au pilote Cortex Leman v5, une infrastructure de confiance IA pour votre cabinet. Ce guide vous permet d'être opérationnel en 5 minutes.

---

## 1. Connexion

Ouvrez votre navigateur et accédez à l'URL communiquée (ex: http://192.168.x.x:8090)

Connectez-vous avec vos identifiants :
- **Email** : celui communiqué par l'équipe Cortex Leman
- **Mot de passe** : celui communiqué

---

## 2. Le Dashboard — Vue d'ensemble

Après connexion, vous accédez au tableau de bord avec 8 sections dans le menu latéral :

| Section | Ce que ça fait |
|---------|---------------|
| 📊 **Tableau de bord** | Vue exécutive : agents actifs, conflits, conformité |
| 🤫 **Serment numérique** | Le serment de votre agent IA — gravé dans le journal WORM |
| 📅 **Échéancier** | Dates clés réglementaires à venir |
| 💬 **Chat Agent** | Posez une question en langage naturel |
| 🎯 **Intentions** | Les requêtes soumises aux agents et leur statut |
| 📝 **Journal d'audit** | Journal inviolable (hash-chain SHA-256) |
| ⚖️ **Arbitrage** | Quand l'IA ne peut pas décider seule — vous décidez |
| ⚙️ **Paramètres** | Clés API, règles du Médiateur, data residency |

---

## 3. Premier test — Poser une question

1. Cliquez sur **💬 Chat Agent**
2. Tapez une question métier, par exemple :
   - *"Quel est le seuil de déclaration anti-blanchiment ?"*
   - *"Que dit le RGPD Art. 22 sur les décisions automatisées ?"*
   - *"Quelles sont mes obligations pour un diagnostic par IA ?"*
3. L'agent consulte le Knowledge Vault réglementaire et vous répond avec les références exactes

---

## 4. Comprendre le Médiateur

Le **Médiateur** est le gardien du système. Il est **100% déterministe** (jamais d'IA).

Quand vous soumettez une intention :
1. L'Agent **Data** cherche les sources
2. L'Agent **Raisonnement** analyse et recommande
3. Le **Médiateur** vérifie les règles de votre verticale
4. Si un risque est détecté → **gel automatique**
5. Si gel → l'intention remonte pour **arbitrage humain** (vous)

---

## 5. Le Journal d'Audit

Chaque action est enregistrée dans un journal **inviolable** :
- Hash-chainé SHA-256 (chaque entrée dépend de la précédente)
- Impossible à modifier ou supprimer
- Consultable par audit
- Vérifiable : cliquez sur **Journal d'audit → Vérifier l'intégrité**

---

## 6. Ce que fait le système automatiquement

| Action | Automatique ? | Qui décide ? |
|--------|--------------|-------------|
| Recherche documentaire | ✅ Oui | Agent Data |
| Analyse réglementaire | ✅ Oui | Agent Raisonnement + LLM |
| Vérification conformité | ✅ Oui | Médiateur (JsonLogic) |
| **Gel préventif** (risque détecté) | ✅ Oui | Médiateur |
| **Exécution d'action** | ❌ Non | Vous (arbitrage) |
| **Décision fiscale/juridique** | ❌ Non | Vous (expert) |

**L'IA ne prend JAMAIS de décision à votre place.** Elle prépare, analyse, recommande. Vous validez.

---

## 7. Questions fréquentes

**Q : Mes données sont-elles sécurisées ?**
Oui. En mode Haute Protection, tout reste sur votre infrastructure. En mode Standard, les données sont chiffrées et le journal est inviolable.

**Q : L'IA peut-elle prendre une décision sans moi ?**
Non. C'est le principe fondamental de Cortex Leman. Toute décision sensible est gelée et remonte pour arbitrage humain.

**Q : Puis-je vérifier ce que l'IA a fait ?**
Oui. Le journal d'audit enregistre tout, de manière immuable et vérifiable.

**Q : Que se passe-t-il en cas de conflit entre agents ?**
Le Médiateur détecte le conflit, gèle l'action, et vous soumet les deux positions pour arbitrage.

---

## 8. Support

- Email : contact@cortex-leman.com
- Documentation : accessible via le dashboard

---

*Cortex Leman v5 — Graphe de Confiance*
*Déterministe là où il faut. Intelligent là où on peut.*
