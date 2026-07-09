# Guide d'entretien de découverte — Fiduciaires & Experts-Comptables FR-CH

> **Usage** : valider (ou invalider) que la verticale fiduciaire/comptable franco-suisse est un *beachhead* viable pour Cortex Leman v5.
> **Durée de l'entretien** : 30 minutes. **À mener en 5 exemplaires en 2 semaines.**
> **Statut** : outil de *problem discovery*, pas de vente. **Ne pas mentionner Cortex Leman ni son architecture.**

---

## 0. La seule chose que tu cherches

> **La douleur « mes collaborateurs utilisent l'IA de façon non maîtrisée sur les dossiers clients » est-elle RÉELLE, VIVE, URGENTE et BUDGÉTÉE — ou purement théorique ?**

Tout le reste est secondaire. Si tu sors de l'entretien sans réponse claire à ça, l'entretien a échoué.

---

## 1. Règle de décision GO / NO-GO (objective, pas au feeling)

Compte un fiduciaire comme **douleur validée** si tu coches **au moins 3 des 4** :

| # | Signal | Coché si… |
|---|--------|-----------|
| A | **Incident concret passé** | Il/elle décrit un événement SPÉCIFIQUE déjà arrivé (data collée dans ChatGPT, alerte DPO, peur d'un associé), pas une hypothèse |
| B | **Contrainte réglementaire nominative** | Cite par nom OEC/CNOEC, nLPD/rLPD, RGPD/CNIL, art. 321bis CP, secret professionnel, charte du cabinet — sans que tu aies suggéré |
| C | **Acte de remédiation déjà posé** | A déjà fait qqch : interdiction, charte interne, formation, outil, signalement au DPO (preuve que ça compte assez pour agir) |
| D | **Signal de budget / engagement** | Évoque un budget, demande « ça coûte combien », demande à voir une démo, propose de te mettre en relation avec un confrère |

### Décision après 5 entretiens
- **≥ 3/5 fiduciaires validés (A+B+C+D)** → **GO verticale fiduciaire**. On code la démo.
- **< 3/5** → **PIVOT**. Réexaminer avocat (cycle long mais douleur vive) ou RH (RGPD art. 22 + discrimination algo). Ne pas rajouter de tech.
- **2-3/5 mais signaux mitigés** → 3 entretiens supplémentaires pour trancher, en changeant le profil (taille de cabinet, canton/région).

---

## 2. Principes — The Mom Test (à relire avant chaque entretien)

1. **Parle de LEUR vie, pas de ton idée.**
2. **Demande du PASSÉ concret, jamais du futur hypothétique.** « La dernière fois que… » > « Pensez-vous que… »
3. **Écoute, ne pitch pas.** Tu ne présentes Cortex Leman que s'ils le demandent explicitement — et même là, en une phrase, puis tu reviens à leurs problèmes.
4. **Les opinions et les compliments ne comptent pas.** Seuls les faits, comportements et passés comptent. « C'est une super idée » = signal nul.
5. **Le silence est ton meilleur outil.** Après une question clé, tais-toi. Laisse le malaise se combler par du vrai contenu.

---

## 3. Questions INTERDITES (biaisées / leading)

- ❌ « Pensez-vous que la sécurité des données est importante ? » *(tout le monde dit oui)*
- ❌ « Utiliseriez-vous un outil qui empêche les fuites vers ChatGPT ? » *(opinion sur ton idée)*
- ❌ « Êtes-vous préoccupé par l'IA ? » *(question suggestive)*
- ❌ « Si on avait une solution, vous l'achèteriez ? » *(promesse facile, non engageante)*

---

## 4. Le script (30 min)

### 4.1 — Accroche & cadrage (2 min)
> « Merci pour votre temps. Je ne vends rien — je mène une étude sur la façon dont les cabinets comme le vôtre utilisent l'intelligence artificielle au quotidien. Vos réponses m'aident à comprendre le terrain réel. Anonymat total, sauf si vous me dites le contraire. 30 minutes, ça vous va ? »

*(Si tu veux enregistrer : demande, sinon prends des notes spartiates pendant, verbatims complets après.)*

### 4.2 — Contexte & profil (3 min)
Objectif : calibrer la taille, l'activité, le profil décisionnaire.

1. « Décrivez-moi le cabinet en 2 minutes — combien de collaborateurs, quels types de clients, quelles activités principales ? »
2. « Vous personnellement, c'est quoi votre rôle et depuis combien de temps ? »
3. *(Suivi si utile)* « Vous avez des clients des deux côtés de la frontière, ou plutôt FR / plutôt CH ? »

### 4.3 — Usages IA actuels — LE CŒUR (8-10 min)
Objectif : faire émerger ce qu'ils font RÉELLEMENT, pas ce qu'ils devraient faire.

4. « La dernière fois que vous ou un collaborateur avez utilisé ChatGPT ou un outil d'IA — ça remonte à quand, et c'était pour quoi exactement ? »
5. « Concrètement, sur quoi portait la requête ? Donnez-moi un exemple, même vague. »
6. *(Crucial)* « Est-ce que des données clients — ne serait-ce qu'un morceau, un nom, un montant, une pièce — ont été impliquées dans la requête ? »
7. « Qui, dans le cabinet, utilise ces outils ? Les associés ? Les collaborateurs juniors ? Les stagiaires ? »
8. « Vous utilisez autre chose que ChatGPT ? Copilot, Gemini, un outil métier, un assistant intégré dans votre logiciel compta ? »

🚩 **Ce que tu écoutes** : la banalisation (coller un bilan, un extrait de compte, une déclaration TVA sans y penser) = douleur vive. Le déni (« on ne fait jamais ça ») suivi d'exemples qui contredisent = douleur niée mais réelle.

### 4.4 — Incidents, peurs, contraintes (8-10 min)
Objectif : le signal le plus fort (critère A, B, C).

9. « Racontez-moi la dernière fois qu'il y a eu une inquiétude, un incident ou une peur liée à l'IA dans le cabinet — même mineure. »
10. *(Si « jamais »)* « Et du côté des clients — est-ce qu'un client vous a déjà posé une question sur la façon dont vous utilisez l'IA sur son dossier ? »
11. « Qu'est-ce que votre ordre / votre chambre fiduciaire / votre DPO / votre assureur professionnel vous dit — ou vous demande — sur l'IA en ce moment ? »
12. « Vous avez déjà été confronté au RGPD / à la nLPD côté traitement de données clients par des outils externes ? Racontez. »
13. *(Si rien ne sort)* « Si demain un journaliste ou un contrôleur vous demandait "montrez-moi comment vous maîtrisez l'IA dans votre cabinet", vous répondriez quoi ? »

🚩 **Ce que tu écoutes** : le nom d'un texte/régulateur cité spontanément (B), un acte déjà posé (C), une émotion (frustration, peur, agacement d'associé).

### 4.5 — Workflow & outils (3-4 min)
Objectif : cartographier l'écosystème → nourrit le moat « intégrations métier ».

14. « C'est quoi votre stack logicielle aujourd'hui ? Logiciel compta, GED, gestion de dossiers, facturation ? »
15. « Où vivent les données clients principalement ? »
16. « Vous avez un DPO interne, externe, ou pas du tout ? »

🚩 **Ce que tu écoutes** : liste de logiciels nommés (future cible d'intégration), existence d'un DPO (acheteur potentiel).

### 4.6 — Budget & décision (2-3 min)
Objectif : critère D. Doux, pas commercial.

17. « Si vous deviez investir demain dans un outil pour maîtriser l'IA dans le cabinet — est-ce que ce serait une décision pour vous, pour les associés, pour le DPO ? »
18. « Sur ce genre de sujet, vous avez un budget annuel, ou c'est du cas par cas ? »
19. *(Si l'ouverture est là)* « Concrètement, ça représenterait quel ordre de grandeur pour le cabinet — quelques centaines, quelques milliers par mois ? »

### 4.7 — Clôture & réseautage (1 min) — LE PLUS SOUS-ESTIMÉ
20. « Vous est-il arrivé de discuter de ces sujets avec des confrères ? »
21. **« Y a-t-il 1 ou 2 autres fiduciaires ou experts-comptables à qui je devrais parler ? »** *(toujours demander — c'est comme ça qu'on passe de 5 à 15 entretiens)*
22. « Je peux vous recontacter dans quelques semaines si j'ai une démo concrète à vous montrer ? »

---

## 5. Fiche de scoring (à remplir < 5 min après l'entretien)

```
Cabinet : __________________________  Date : __________
Profil  : taille ___  FR/CH/mixte ___  rôle interlocuteur ___
DPO     : interne / externe / aucun

A. Incident concret passé      :  ☐ oui  ☐ non   verbatim clé :
B. Contrainte réglement. citée :  ☐ oui  ☐ non   laquelle :
C. Remédiation déjà posée      :  ☐ oui  ☐ non   laquelle :
D. Signal budget/engagement    :  ☐ oui  ☐ non   lequel :

Score : __ / 4   →   DOULEUR : ☐ VALIDÉE (≥3)   ☐ PARTIELLE   ☐ ABSENTE

3 verbatims les plus forts (mots exacts) :
  1. « »
  2. « »
  3. « »

Logiciels cités (cibles d'intégration) :
  - 

Lead intro proposé ?  ☐ oui (qui : ________)   ☐ non
M'a-t-il demandé la démo ?  ☐ oui  ☐ non

Sentiment global (1 phrase) :
```

---

## 6. Signaux à surveiller

### 🟢 Douleur probablement réelle
- Silence gêné après « des données clients impliquées ? »
- Récit d'incident précis avec date/conséquence
- Texte réglementaire cité spontanément
- « On a interdit / formé / écrit une charte »
- Frustration envers les juniors « qui collent tout dans ChatGPT »
- Question sur le prix, demande de démo, parrainage

### 🔴 Douleur probablement absente / théorique
- « On n'utilise pas l'IA » (et aucune anecdote ne suit)
- Tout est au conditionnel / futur (« ça pourrait »)
- Politesse sans substance (« c'est très intéressant »)
- Aucune mention réglementaire même quand tu sondes
- Aucun acte de remédiation posé
- Réponse au parrainage : « je ne vois personne »

### ⚠️ Pièges
- **Compliments sur le projet** = bruit. Recentre sur leurs faits.
- « **On devrait** se protéger » = opinion future, pas douleur. Creuse le passé.
- L'interlocuteur **sur-éduqué** (associé qui maîtrise le sujet) peut masquer une base collaborateurs indisciplinée — demande comment la maîtrise est *appliquée* au quotidien.

---

## 7. Plan d'exécution (lundi → 2 semaines)

1. **Lister 20 cibles** : fiduciaires genevoises/vaudoises/valaisannes + experts-comptables HAUTE-Savoie / Ain / Jura. Sources : annuaires Chambre suisse des fiduciaires, CNOEC, LinkedIn (filtrer « fiduciaire » + Genève/Lausanne/Annemasse).
2. **Message d'approche** (cold email / LinkedIn) — 3 lignes, zéro pitch produit :
   > « Bonjour, je mène une étude sur l'usage réel de l'IA dans les cabinets fiduciaires franco-suisses. 30 min d'échange, je ne vends rien, anonymat garanti. Vous auriez 30 min la semaine prochaine ? »
3. **Viser 10 contacts → 5 entretiens** (taux de réponse ~50%).
4. **Logger chaque entretien** dans `docs/prospects/entretiens/` (un fichier par cabinet, anonymisé).
5. **Décision GO/NO-GO** au bout du 5e, avec le tableau de scoring consolidé.

---

## 8. Ce que tu fais des résultats

- **GO** : tu reviens avec les verbatims → on choisit ensemble le 1 use case démo (probablement « titrer/trier des pièces comptables sans fuite » ou « assistant questions TVA FR/CH sur dossier ») et on le code sur la codebase existante.
- **NO-GO** : on pivote vertical sans regret, sans avoir codé une ligne de plus.

---

*Ce guide est conçu pour être imprimé/placé à côté du clavier pendant l'app. Ne pas le lire à voix bout à bout — l'entretien doit respirer.*
