# PREMORTEM — Juin 2027 : Les 3 projets ont échoué

Hypothèse de travail explicite : je suppose que le solde de trésorerie personnel finance ~12-18 mois de runway sans revenu, et que le temps de travail total disponible est ~50-60h/semaine (un seul humain). Si ces chiffres sont faux, dis-le, ça change les conclusions.

---

## PROJET 1 — CORTEX LEMAN v5

**Scénario d'échec le plus probable :** Tu as construit une cathédrale technique (graphe de confiance déterministe, WORM, dual-mode K3s/Ollama) que personne n'a achetée parce que tu n'as jamais réussi à faire signer un seul cabinet régulé avant d'épuiser ta motivation et ton runway sur 6 verticales simultanées.

**Top 5 causes racines :**

1. **(35%) Sur-ingénierie pré-revenu.** Tu as 81 tests verts et un Médiateur déterministe à 120 règles (20×6) avant d'avoir une signature. Chaque heure passée sur l'architecture est une heure non passée en vente. Le déterminisme JsonLogic est un argument de conformité qui n'a de valeur QUE si un acheteur régulé le réclame contractuellement — or tu ne l'as pas validé.

2. **(30%) Cycle de vente régulé incompatible avec un solo auto-financé.** Vendre à un cabinet d'avocats ou une banque = 6-12 mois, comité, sécurité IT, DPO, références clients existantes. Tu n'as ni références, ni équipe support, ni assurance responsabilité. Un solo ne ferme pas ce type de deal en moins de runway que ce qu'il lui reste.

3. **(20%) 6 verticales = 0 verticale.** Comptable, avocat, santé, banque, startup, RH ont des règles, des cycles d'achat et des acheteurs totalement différents. Tu disperses 1 personne sur 6 marchés. Le wedge "revue de contrats" est le bon instinct mais tu ne l'as pas amputé du reste.

4. **(10%) Incumbents.** Microsoft Copilot, Harvey, Luminance arrivent avec budgets marketing et conformité enterprise. Ton avantage "souveraineté FR-CH locale" est réel mais étroit, et tu n'as pas chiffré le segment qui paie POUR ça.

5. **(5%) Mode Haute Protection (K3s+Ollama local) ingérable en solo.** Si tu vends du on-prem souverain, tu dois maintenir des déploiements chez des clients régulés. Un solo ne fait pas de support SLA on-prem santé/banque. Promesse intenable.

**Signaux d'alerte (datés) :**
- **Q3 2026 :** Aucun rendez-vous découverte avec un acheteur économique réel (associé de cabinet, pas un contact LinkedIn) en 8 semaines. → Le marché ne se déplace pas.
- **Q4 2026 :** Tu codes encore les dashboards Phase 1B/1C au lieu de vendre. Le temps "build" > "sell" reste >70%.
- **Q1 2027 :** Zéro pilote payant signé, zéro lettre d'intention. Tu rationalises ("il faut juste finir la feature X").

**Actions cette semaine :**
1. **Tue 5 verticales sur 6.** Garde UNIQUEMENT "revue de contrats pour cabinets d'avocats OU comptables FR-CH" (choisis selon ton réseau réel). Écris-le noir sur blanc.
2. **20 appels de découverte** auprès d'associés réels. Question unique : "Aujourd'hui, comment gérez-vous la confidentialité quand vous utilisez ChatGPT sur un contrat client ? Combien payez-vous / paieriez-vous pour une solution conforme ?"
3. **Gel total du code** pendant 3 semaines. Aucune nouvelle feature tant que tu n'as pas 1 lettre d'intention.

---

## PROJET 2 — DROPATOM / PIOCHE

**Scénario d'échec le plus probable :** Tu as lancé une "usine à dossiers" à 49€ dont le break-even business réel (34-60 abonnés) n'a jamais été atteint parce que les solopreneurs e-commerce churnent au bout de 2 mois après avoir généré leur dossier unique et n'ont aucune raison de rester abonnés.

**Top 5 causes racines :**

1. **(35%) Modèle économique cassé par construction.** Tu l'as toi-même chiffré : break-even 34-60 abonnés à 99€, impossible à 49€ médian. Tu vends un livrable ponctuel (un dossier de lancement) sur un modèle d'abonnement récurrent. Mauvais fit produit/pricing. **Le churn va te tuer.**

2. **(25%) Cible non solvable et non rétentive.** Les solopreneurs e-commerce débutants ont peu d'argent, fort churn, et beaucoup ABANDONNENT leur projet e-commerce lui-même. Tu construis sur du sable démographique.

3. **(20%) 48 agents = dispersion produit + dette de maintenance.** 48 wrappers API qui cassent à chaque changement d'API amont, maintenus par 1 personne. La valeur perçue ne croît pas avec le nombre d'agents ; la fragilité, oui.

4. **(15%) Pas de canal d'acquisition.** Telegram + API ne sont pas un canal. Comment trouves-tu 60 abonnés payants ? Tu n'as pas de réponse, donc CAC inconnu = modèle non finançable.

5. **(5%) Héritage WORM/JsonLogic non pertinent.** Tu transposes la conformité de Cortex sur une cible (solopreneurs) qui s'en fiche totalement. Effort recopié sans valeur.

**Signaux d'alerte (datés) :**
- **Q3 2026 :** CAC inconnu ou >100€ pour un produit à 49€. → Économie unitaire négative confirmée.
- **Q4 2026 :** Churn mensuel >20% sur les premiers inscrits. → Confirme l'achat ponctuel déguisé en abonnement.
- **Q1 2027 :** <15 abonnés payants. Tu n'atteindras jamais 34-60.

**Actions cette semaine :**
1. **Teste le pricing par la vente, pas par le code.** Crée une page de vente à 99€ et essaie de vendre 5 dossiers MANUELLEMENT (toi qui livres). Si tu ne vends pas 5 unités à la main, le SaaS ne se vendra pas.
2. **Repense le modèle :** soit one-shot payant (149€ le dossier, pas d'abonnement), soit tue le projet. L'abonnement est un mensonge à toi-même.
3. **Réduis 48 agents → 3** qui produisent le livrable cœur. Le reste est du théâtre.

---

## PROJET 3 — IMPORTEXPORT PRO

**Scénario d'échec le plus probable :** Tu as construit 5 agents + un module compliance HS impressionnant sur une base de 24h de YouTube, mais tu n'as jamais identifié qui paie ni comment les atteindre, et le projet est mort faute de premier client après 12 mois de "consulting hybride" jamais facturé.

**Top 5 causes racines :**

1. **(40%) Zéro canal de distribution.** Tu le dis toi-même : "aucun canal identifié". C'est la cause de mort n°1. Un produit import-export sans accès aux importateurs/PME est un orphelin. Pas de canal = pas de business, point.

2. **(25%) Base de connaissances faible et risquée en domaine régulé.** 782KB de transcripts YouTube comme fondation pour conseiller sur CE/RoHS/REACH/sanctions = risque de conseil erroné. Une erreur de classification HS ou de sanctions coûte cher au client → ta responsabilité.

3. **(15%) Hybride consulting+produit = ni l'un ni l'autre.** Le consulting ne scale pas (ton temps) et le produit n'est pas prouvé. Tu portes les coûts des deux modèles sans les revenus de l'un.

4. **(15%) Marché import-export Chine→Europe/Afrique = relationnel et de confiance.** Les acheteurs travaillent avec des transitaires et agents établis depuis des années. Un solo avec des agents IA n'a pas la crédibilité pour remplacer ça.

5. **(5%) Le module compliance abstrait (TARIC/EUR-Lex/WCO) est complexe à maintenir à jour.** Les nomenclatures et sanctions changent ; un solo ne tient pas la fraîcheur réglementaire.

**Signaux d'alerte (datés) :**
- **Q3 2026 :** Toujours aucun canal nommé ni premier prospect concret. → Mort lente confirmée.
- **Q4 2026 :** Tu améliores la base de connaissances (plus de vidéos) au lieu de chercher un client. Fuite dans le build.
- **Q1 2027 :** Zéro mission de consulting facturée. Même le modèle "facile" (consulting) n'a pas démarré.

**Actions cette semaine :**
1. **Vends UNE mission de consulting manuelle** à 500-1500€ à un importateur réel de ton réseau. Si tu ne peux pas, le produit n'a pas de marché accessible.
2. **Identifie 1 canal précis :** groupe Facebook d'importateurs FR, un transitaire partenaire, une CCI franco-africaine. Nomme-le. Si tu ne peux pas, mets le projet en pause.
3. **Audit de responsabilité :** liste ce qui se passe si ton agent compliance se trompe sur une sanction. Si tu n'es pas couvert, n'en fais pas un produit.

---

## ANALYSE TRANSVERSALE — Les 3 risques d'avoir 3 (4) projets en parallèle

**Risque 1 — Dispersion d'attention = aucun projet n'atteint la masse critique de vente.**
Un solo a une ressource scarce : son attention de vente, pas son temps de code. Le code se réplique (tu copies WORM/JsonLogic partout), la vente non. En répartissant sur 3-4 projets, tu n'atteins le seuil de traction d'AUCUN. La preuve : les 3 projets ont "aucune preuve de revenu". Ce n'est pas une coïncidence, c'est la signature de la dispersion. **Tu fais du build parce que c'est confortable et que ça donne l'illusion d'avancer. La vente fait mal, donc tu l'évites en codant le 4e agent.**

**Risque 2 — Faux levier / dilution par "réutilisation".**
Tu te racontes que WORM + JsonLogic + le pattern "compliance + adoption layer" se réutilisent d'un projet à l'autre, ce qui justifierait le parallélisme. **C'est un piège.** La conformité a de la valeur chez Cortex (régulés), zéro chez Pioche (solopreneurs), et incertaine chez ImportExport. Tu transposes une solution technique à des marchés qui ne la veulent pas, ce qui te fait croire que tu avances alors que tu recopies un actif non désiré. La réutilisation de code n'est PAS une synergie de marché.

**Risque 3 — Interdépendance d'échec / contagion de motivation.**
Tu es le single point of failure des 4. Quand le projet le plus dur (Cortex, cycle long régulé) ne décolle pas, ta motivation chute, et ça contamine les autres. Pire : le runway est COMMUN. Chaque euro et chaque heure dépensés sur ImportExport sans canal sont volés à Cortex. Les projets ne sont pas indépendants : ils se cannibalisent une trésorerie et une énergie finies. **Et il y a un 4e projet (SocialPulse) "separate" — c'est exactement le symptôme : tu ouvres un nouveau front au lieu d'en fermer.**

**Verdict transversal dur :** Tu n'as pas un portefeuille de projets, tu as un mécanisme d'évitement de la vente sous forme de prototypes. La dispersion n'est pas un risque parmi d'autres : c'est LA cause racine commune des 3 échecs.

---

## Lequel survit ? Lequel tuer en premier ?

**Le plus de chances de survivre : CORTEX LEMAN (mais seulement amputé à 1 verticale + wedge contrats).**
Raison : c'est le seul qui adresse un acheteur SOLVABLE (cabinets régulés ont de l'argent) avec un problème RÉEL et CROISSANT (confidentialité IA en milieu régulé). Le déterminisme/souveraineté est un différenciateur défendable face à Copilot. Mais sa survie est conditionnelle : focus 1 verticale, vente avant build, un pilote payant sous 90 jours.

**À tuer le plus vite : DROPATOM / PIOCHE.**
Raison : c'est le seul dont TU AS DÉJÀ PROUVÉ par les chiffres que le modèle est cassé (break-even 34-60 abonnés impossible au prix médian, cible non rétentive). Les deux autres ont une incertitude ; Pioche a une quasi-certitude négative. On ne garde pas un projet dont on a calculé l'impasse économique. **Tue-le cette semaine, récupère l'attention.**

(ImportExport : mise en pause immédiate conditionnée à 1 vente de consulting manuelle sous 30 jours. S'il n'y a pas de canal et pas de premier client, il rejoint Pioche.)

---

## VERDICT FINAL

**Tu n'échoueras pas par manque de compétence technique mais par excès de celle-ci : tue Pioche aujourd'hui, gèle ImportExport et SocialPulse, concentre 100% de ton attention sur UNE verticale de Cortex et obtiens une signature payante avant d'écrire une ligne de code de plus — sinon, dans 12 mois, tu auras 4 prototypes brillants et zéro euro.**
