# PRÉMORTEM — JUIN 2027 : LES TROIS PROJETS ONT ÉCHOUÉ

---

## PROJET 1 — CORTEX LEMAN v5

### Scénario d'échec le plus probable
Cortex Leman a passé 18 mois à construire une infrastructure irréprochable techniquement que personne dans les cabinets régulés n'a demandé, et les 3 premiers prospects ont dit "intéressant, revenez quand vous avez 10 clients référencés" — cercle vicieux classique du B2B régulé sans distributeur.

### Top 5 causes racines

| # | Cause | Probabilité | Raison |
|---|-------|------------|--------|
| 1 | **Zéro accès au décideur réel** | 85% | Un solo sans réseau dans les barreaux, OECT ou AMF ne vend pas à des professions régulées. Le "contrat revue wedge" est une fonctionnalité, pas un canal. Les cabinets signent avec des intégrateurs qu'ils connaissent depuis 5 ans ou des éditeurs certifiés. Il n'existe aucune preuve de contact qualifié dans les docs. |
| 2 | **Complexité produit auto-infligée** | 80% | 6 verticales × 20 règles JsonLogic × 2 modes (Standard/Haute Protection) × 5 agents = 240 configurations potentielles à maintenir par une seule personne. Chaque verticale ajoutée sans client validé est une dette de maintenance qui ne génère aucun revenu. |
| 3 | **Cycles de vente incompatibles avec le cash-flow solo** | 75% | Un cabinet d'avocats ou une banque privée suisse prend 6 à 18 mois pour signer un contrat SaaS impliquant des données clients. Sans financement bridge, l'opérateur manque d'argent avant la première signature. |
| 4 | **Haute Protection K3s/Ollama = frein déguisé en feature** | 65% | "Zéro appel externe" sur K3s local exige que le client gère une infrastructure. Un cabinet de 5 avocats n'a pas de DSI. Soit l'opérateur assure le déploiement (temps non facturé, support permanent), soit le client abandonne. La valeur technique est réelle ; la proposition commerciale est bancale. |
| 5 | **Phase 1B/1C jamais démarrées = démo inexistante** | 60% | Les dashboards non construits signifient qu'il n'y a rien à montrer à un prospect. 81 tests verts ne remplacent pas une démo qui fonctionne en 10 minutes devant un comptable sceptique. |

### Signaux d'alerte précoces

- **Q3 2026** : Aucun rendez-vous de démonstration avec un décideur réel (associé gérant, DAF, bâtonnier) après 6 semaines de prospection active. Des "intéressants" sur LinkedIn ne comptent pas.
- **Q4 2026** : Le module "revue de contrats" est utilisé en freemium mais aucun utilisateur freemium ne pose de question sur un upgrade payant après 30 jours d'usage.
- **Q1 2027** : La 6e verticale est en cours de développement sans qu'aucune des 5 premières ait un client payant. C'est la signature que le produit s'étend pour éviter de vendre.

### Actions préventives — cette semaine

1. **Tuer 4 verticales immédiatement.** Choisir une seule (hypothèse : expertise-comptable France, marché le plus structuré, Ordre avec 22 000 cabinets, cycle de vente légèrement plus court). Tout le reste devient "roadmap future". Cela réduit la dette de maintenance de ~66% et force un discours de vente cohérent.
2. **Contacter 10 experts-comptables en direct cette semaine** (pas un formulaire, un appel ou un message LinkedIn personnalisé) avec une seule question : "Quel est le problème que vous résolvez le plus mal aujourd'hui avec vos outils ?" — pas de pitch. Écouter. Si aucun ne mentionne un problème que Cortex résout, le positionnement est faux.
3. **Construire la démo Phase 1B en 5 jours** pour un seul cas d'usage (ex : génération de note de synthèse fiscale avec journal WORM visible). Si ce n'est pas faisable en 5 jours en solo, c'est que l'architecture est trop lourde pour une démo commerciale, et c'est une information critique.

---

## PROJET 2 — DROPATOM / PIOCHE

### Scénario d'échec le plus probable
Pioche atteint 8 abonnés payants après 6 mois, l'opérateur réalise que 48 agents à maintenir pour 800€/mois de revenu brut représentent plus de travail qu'un emploi salarié, et abandonne silencieusement.

### Top 5 causes racines

| # | Cause | Probabilité | Raison |
|---|-------|------------|--------|
| 1 | **Le break-even réel est 34-60 abonnés — inatteignable sans acquisition payante** | 90% | À 99€/mois, 34 abonnés = 3 366€/mois. Un solo sans budget marketing en B2C/SMB avec Telegram comme canal principal n'atteint pas 34 abonnés payants rétentifs en 12 mois sans un mécanisme viral documenté ou une audience existante. Hypothèse : si taux de conversion visiteur→payant = 3% (optimiste pour SaaS SMB), il faut 1 133 visiteurs qualifiés/mois. D'où viennent-ils ? |
| 2 | **Le solopreneur e-commerce n'achète pas de SaaS structuré** | 80% | Ce segment achète des formations à 497€ une fois, des outils à 19€/mois avec essai gratuit 14 jours et zéro friction, ou du contenu YouTube gratuit. Un "dossier de lancement" avec 48 agents et Telegram comme interface est cognitif heavy pour quelqu'un qui veut juste savoir quoi vendre la semaine prochaine. |
| 3 | **48 agents = produit sans focus = impossible à marketer** | 75% | Quelle est la promesse en une phrase ? "Usine à dossiers de lancement" est un concept, pas une douleur. Les solopreneurs e-com ont des douleurs précises : trouver un produit gagnant, sourcer moins cher, écrire des fiches produit. 48 agents dilue le message et complexifie le support. |
| 4 | **Héritage WORM + JsonLogic = over-engineering fatal** | 65% | Le solopreneur e-commerce se fiche de la traçabilité WORM et du déterminisme JsonLogic. Ce sont des contraintes de Cortex Leman greffées sur un produit grand public. Elles alourdissent l'infrastructure sans créer de valeur perçue par l'acheteur cible. |
| 5 | **Modèle unitaire mal calculé dès le départ** | 55% | Le "break-even 1 abonné Pro" dans PROJECT.yaml est une erreur de raisonnement documentée (coûts fixes non inclus). Si l'opérateur a commis cette erreur en planifiant, il est probable que d'autres hypothèses financières sont également optimistes. |

### Signaux d'alerte précoces

- **Q3 2026** : Moins de 50 signups (même gratuits) après 8 semaines de communication active sur les canaux solopreneur (Reddit e-commerce, groupes Facebook, TikTok dropship). Si la demande d'essai est faible, la douleur n'est pas assez aiguë ou le message est mauvais.
- **Q4 2026** : Taux de rétention à 30 jours inférieur à 40% sur les premiers abonnés payants. Le solopreneur essaie, ne trouve pas de produit gagnant via Pioche, et annule.
- **Q1 2027** : L'opérateur passe plus de 15h/semaine en support Telegram individuel pour moins de 20 abonnés. Le modèle devient du consulting déguisé en SaaS.

### Actions préventives — cette semaine

1. **Réduire à 5 agents maximum** autour du cas d'usage le plus aigu (hypothèse : "trouver et qualifier un produit gagnant en 48h"). Archiver les 43 autres. Un produit qu'on peut expliquer en 30 secondes se vend ; une "usine à 48 agents" ne se vend pas.
2. **Poster cette semaine** dans 3 communautés solopreneur e-com (Reddit r/dropship, un groupe Telegram francophone dropship, un Discord) : "J'ai un outil qui [promesse spécifique]. Qui veut tester gratuitement 7 jours en échange de 30 minutes de feedback ?" Objectif : 10 testeurs réels avant de construire quoi que ce soit de plus.
3. **Calculer honnêtement le coût réel par abonné** : coût API/mois (48 agents × appels moyens estimés), coût support moyen, coût d'acquisition estimé. Si le coût total dépasse 40€/abonné à 99€/mois, la marge est trop faible pour survivre sans volume.

---

## PROJET 3 — IMPORTEXPORT PRO

### Scénario d'échec le plus probable
ImportExport Pro reste un prototype avec une base de connaissances YouTube et zéro client 12 mois après lancement parce que l'opérateur n'a jamais défini si c'est un outil SaaS, un service de consulting, ou une formation — et donc n'a jamais su à qui le vendre ni comment.

### Top 5 causes racines

| # | Cause | Probabilité | Raison |
|---|-------|------------|--------|
| 1 | **Identité produit inexistante : hybride consulting+produit = ni l'un ni l'autre** | 90% | Un consultant facturer au temps ou un SaaS à l'abonnement : les deux modèles ont des structures radicalement différentes (vente, pricing, support, scalabilité). "Hybride" sans définition précise signifie que l'opérateur répondra à n'importe quelle demande de n'importe quelle façon, consommant du temps sans construire de récurrence. |
| 2 | **Base de connaissances YouTube = données non vérifiables, non auditables, obsolètes** | 85% | 782KB de transcriptions YouTube pour entraîner des agents compliance (classifications HS, REACH, sanctions)? Les sanctions changent toutes les semaines (Russia, Belarus, Iran). Les codes HS évoluent. Une erreur de classification HS coûte à l'importateur des amendes douanières réelles. La responsabilité est totale et la source est un YouTubeur. C'est un risque légal non trivial. |
| 3 | **Aucun canal de distribution identifié** | 80% | Qui sont les clients ? Des PME qui importent ? Des transitaires ? Des courtiers ? Chaque segment a ses propres canaux d'acquisition, son langage, ses objections. Sans canal défini, le produit est invisible. |
| 4 | **Marché saturé par des acteurs établis avec données officielles** | 70% | Customs City, Descartes, Amber Road, ou simplement un consultant douanier expérimenté à 150€/h offrent une proposition plus solide sur la compliance. La différenciation "IA + WORM" n'est pas un avantage perçu par un responsable import qui risque sa licence. |
| 5 | **Complexité réglementaire réelle sous-estimée** | 65% | La chaîne HS + CE/RoHS/REACH + sanctions + EUR-Lex est un domaine où les experts humains se trompent. 5 agents IA avec des interfaces abstraites vers TARIC ne remplacent pas une veille juridique professionnelle. Le module "compliance" fraîchement ajouté suggère que cette complexité a été découverte après le début du développement — signal d'un scope mal cadré dès l'origine. |

### Signaux d'alerte précoces

- **Q3 2026** : Incapacité à répondre à la question "Qui est votre client type, quel est son titre, dans quelle taille d'entreprise, et quel problème précis résolvez-vous pour lui ?" en moins de 2 minutes, sans hésitation.
- **Q4 2026** : Le module compliance est mis à jour pour couvrir un 4e régime de sanctions sans qu'aucun client n'ait utilisé les 3 premiers. Construction en avant du marché.
- **Q1 2027** : L'opérateur est sollicité pour du "consulting one-shot" via le produit (un importateur veut une classification spécifique), accepte, facture une fois, mais le cas ne génère pas de récurrence ni de SaaS conversion. Le modèle dérive vers du conseil artisanal non scalable.

### Actions préventives — cette semaine

1. **Décider en 24h** : SaaS ou consulting ? Si SaaS : quel abonnement, quelle fonctionnalité principale, quel segment précis ? Si consulting : quel tarif horaire, quel type de mission, et comment atteindre les clients (LinkedIn, transitaires, CCI) ? L'ambiguïté actuelle est plus coûteuse que n'importe quelle mauvaise décision.
2. **Remplacer la base YouTube** par au moins 3 sources officielles machine-readable sur le cas d'usage principal (ex : API TARIC pour les codes HS, EUR-Lex pour REACH) et documenter explicitement les limites légales du produit. Sans cela, le risque de responsabilité est ouvert et indéfendable.
3. **Identifier 5 prospects cette semaine** via les CCI franco-chinoises (Paris, Lyon, Marseille ont toutes des clubs d'importateurs), LinkedIn "responsable import" + filtres France/Belgique. Pas de pitch : une demande d'entretien de 20 minutes pour comprendre leurs outils actuels.

---

## ANALYSE TRANSVERSALE — LA DISPERSION EST LE MÉTA-RISQUE

### Risque 1 : Le temps est une ressource non-extensible et l'opérateur se ment à lui-même sur ce point

Un solo qui gère 3 projets en parallèle (plus SocialPulse "séparé") n'a pas 3× moins de temps par projet — il a en réalité bien moins, à cause des coûts de contexte-switching. Des recherches sur les développeurs en multi-tâche (étude Gloria Mark, UC Irvine) montrent 23 minutes de récupération cognitive après chaque interruption. Estimation brute : si l'opérateur consacre 8h/jour à ses projets et switch 6× par jour, il perd ~2h30 en friction cognitive pure. Sur 12 mois, c'est ~45 jours ouvrés de travail effectif évaporés. **Aucun des trois projets n'est en phase de "maintenance passive" : tous trois exigent du développement actif et de la vente active simultanément. C'est physiquement impossible à un niveau de qualité suffisant.**

### Risque 2 : L'architecture partagée crée une fausse impression de progrès

Le fait que Cortex Leman, Dropatom et (partiellement) ImportExport Pro partagent le journal WORM et JsonLogic est présenté implicitement comme une économie d'échelle. C'est en réalité un risque de couplage. Un bug dans le module WORM touche les trois produits simultanément. Une décision d'architecture sur Cortex (ex : changer le schéma de hash) force une migration sur Dropatom. **Le "playbook partagé" transforme 3 projets indépendants en un monolithe caché, avec la fragilité d'un monolithe sans la cohérence d'un produit unique.**

### Risque 3 : Trois projets sans revenu = zéro signal marché réel, donc zéro apprentissage prioritaire

Quand aucun projet ne génère de revenu, l'opérateur ne peut pas utiliser l'argent comme signal de validation. Il compense avec des métriques proxy (tests verts, agents créés, lignes de code, verticales couvertes) qui donnent l'illusion de progrès sans valider l'hypothèse centrale de chaque projet : quelqu'un paie-t-il ? **Dans 12 mois, l'opérateur aura produit davantage de code, d'agents et de documentation — et sera toujours à zéro revenu récurrent. Le rythme de construction est devenu une fin en soi.**

---

## LEQUEL SURVIT ? LEQUEL MEURT ?

### Projet avec le plus de chances de survivre : **Cortex Leman v5**

Pas parce que c'est le mieux parti — il ne l'est pas. Mais parce que :
- Le problème réel existe (les professions régulées ont des besoins de traçabilité et de conformité IA documentés)
- La barrière technique est haute (ce qui décourage les concurrents directs au même niveau d'architecture)
- Le wedge "revue de contrats" est la seule fonctionnalité des trois projets qui ressemble à quelque chose qu'un professionnel payerait directement pour un gain immédiat

**Condition stricte** : focalisé sur une seule verticale (expertise-comptable ou avocat, pas les deux), avec une démo fonctionnelle, et un premier client pilote signé avant fin Q3 2026. Sans ça, même Cortex meurt.

### Projet à tuer le plus vite : **ImportExport Pro**

- Identité produit inexistante
- Base de données fondamentalement inadaptée au risque compliance réel
- Aucun canal de distribution
- Marché avec des concurrents ayant des données officielles en temps réel
- Risque légal potentiel si un client commet une erreur de classification basée sur l'outil

Ce n'est pas un projet en difficulté — c'est une idée qui n'a pas encore été confrontée à la réalité. La tuer maintenant coûte zéro ; la tuer dans 6 mois coûte 6 mois.

**Dropatom/Pioche** : à suspendre (pas à tuer complètement), parce que le marché solopreneur est plus accessible et les cycles de validation sont plus courts. Si une version réduite à 5 agents trouve 20 abonnés payants en 8 semaines, c'est le seul signal marché concret disponible à court terme. Sinon, suspendre définitivement.

---

## VERDICT FINAL

> **L'opérateur construit trois fusées dans trois hangars avec les mêmes pièces détachées, sans client, sans piste de lancement, et s'approche du moment où il n'aura plus ni pièces ni hangar — la seule décision rationnelle cette semaine est de choisir une fusée, démonter les deux autres pour récupérer le carburant, et trouver un passager payant avant de construire quoi que ce soit de plus.**
