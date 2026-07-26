# Procédure de gestion des violations de données personnelles  
**Cortex Leman SARL — Version 5**

| Référence | PRO-COMPLIANCE-VIOLATION-RGPD |
|---|---|
| Version | 5 |
| Propriétaire | DPO Cortex Leman |
| Approbateur | [Nom, fonction] |
| Date d’entrée en vigueur | [JJ/MM/AAAA] |
| Prochaine revue | [JJ/MM/AAAA] |
| Classification | Interne — Confidentiel |
| Périmètre | Cortex Leman SARL, collaborateurs, sous-traitants et systèmes exploités pour ses clients FR/CH |

> **Validation obligatoire :** le présent document doit être relu, adapté aux contrats clients et validé par le DPO de Cortex Leman avant mise en application. Les coordonnées, procédures contractuelles et exigences sectorielles doivent être vérifiées au moins annuellement et après tout changement réglementaire ou organisationnel.

---

## 1. Objet et périmètre

La présente procédure définit les mesures à prendre lorsqu’une violation de données personnelles ou un incident de sécurité susceptible d’en constituer une est détecté.

Elle s’applique notamment aux traitements réalisés par Cortex Leman pour :

- **Hôpital de Genève** — données de santé — contact client : Dr Laurent ;
- **UBank SA** — données bancaires et financières — contact client : T. Muller ;
- **Martin Avocat** — données couvertes par le secret professionnel — contact client : P. Martin ;
- **Dupont Comptable** ;
- **Groupe RH** ;
- **StartupParis** ;
- **Darkom-debarras** ;
- tout autre client ou partenaire de Cortex Leman.

Cortex Leman agit principalement en qualité de **sous-traitant** au sens de l’article 4, point 8, du RGPD et de **sous-traitant** au sens de l’article 5, let. j, LPD, sous réserve de l’analyse de chaque traitement et contrat.

En cette qualité, Cortex Leman doit notamment :

1. détecter, contenir et documenter l’incident ;
2. informer le responsable du traitement ou client concerné **sans délai injustifié** ;
3. fournir les informations nécessaires à la notification réglementaire du client ;
4. notifier directement une autorité uniquement lorsque la loi, le contrat, une délégation du client ou une obligation propre de Cortex Leman le prévoit ;
5. préserver les preuves et réduire les risques pour les personnes concernées.

---

## 2. Références légales et réglementaires

### 2.1 France et Union européenne

- **RGPD, article 4, point 12** : définition de la violation de données à caractère personnel ;
- **RGPD, article 28, paragraphe 3, point f** : assistance du sous-traitant au responsable du traitement pour assurer le respect des obligations relatives aux violations ;
- **RGPD, article 32** : sécurité du traitement ;
- **RGPD, article 33** : notification de la violation à l’autorité de contrôle ;
- **RGPD, article 34** : communication de la violation à la personne concernée ;
- **RGPD, article 9** : catégories particulières de données, notamment les données concernant la santé ;
- **RGPD, article 82** : responsabilité et droit à réparation ;
- **RGPD, article 83** : sanctions administratives ;
- **RGPD, article 30, paragraphe 5** : registre des activités de traitement, lorsque applicable ;
- **Règlement (UE) 2024/1689 — AI Act, article 73** : notification des incidents graves liés aux systèmes d’IA, lorsque les conditions d’application sont remplies.

### 2.2 Suisse

- **LPD, art. 5, let. f** : violation de la sécurité des données ;
- **LPD, art. 7** : protection des données dès la conception et par défaut ;
- **LPD, art. 8** : sécurité des données ;
- **LPD, art. 24** : annonce des violations de la sécurité des données au Préposé fédéral à la protection des données et à la transparence (PFPDT) ;
- **LPD, art. 25** : information de la personne concernée ;
- **LPD, art. 26** : restrictions au devoir d’informer ;
- **LPD, art. 27** : traitement de données personnelles par le sous-traitant ;
- **Code pénal suisse, art. 321** : secret professionnel, notamment pour les avocats et certaines professions réglementées ;
- **Loi fédérale sur les banques et les caisses d’épargne, art. 47 LB** : secret bancaire ;
- dispositions FINMA applicables à la gestion des risques, à la résilience opérationnelle, à l’externalisation et aux incidents, selon le statut de l’établissement concerné et la nature de l’incident.

> **Attention :** les obligations de notification peuvent incomber au responsable du traitement, à l’exploitant, au fournisseur d’un système d’IA ou à une autre entité selon le rôle juridique réel. Le DPO et le conseil juridique doivent confirmer le rôle de Cortex Leman et l’autorité compétente pour chaque incident.

---

## 3. Définitions

### 3.1 Violation de données personnelles

Constitue une violation de données personnelles toute violation de la sécurité entraînant, de manière accidentelle ou illicite :

- la destruction ;
- la perte ;
- l’altération ;
- la divulgation non autorisée ;
- l’accès non autorisé ;

de données personnelles transmises, conservées ou traitées.

### 3.2 Violation de confidentialité

Accès ou divulgation non autorisé(e) de données personnelles.

**Exemples :**

- accès à un dossier patient par un utilisateur non habilité ;
- envoi d’un rapport à un mauvais destinataire ;
- exposition d’une base de données sur Internet ;
- fuite de secrets bancaires ou professionnels ;
- compromission d’un compte administrateur ;
- sortie non autorisée de données depuis un système d’IA ou une API ;
- inclusion de données d’un client dans la réponse destinée à un autre client.

### 3.3 Violation d’intégrité

Modification, suppression, corruption ou altération non autorisée de données personnelles.

**Exemples :**

- modification d’un dossier médical ;
- altération d’un montant ou d’une instruction financière ;
- empoisonnement ou modification d’un jeu de données d’entraînement ;
- modification d’un modèle, d’un prompt système ou d’une règle de filtrage ;
- falsification d’un journal ou d’une preuve.

### 3.4 Violation de disponibilité

Perte d’accès, destruction ou indisponibilité temporaire ou définitive de données personnelles ou de systèmes nécessaires à leur traitement.

**Exemples :**

- ransomware ;
- destruction d’une base de données ;
- perte d’un support contenant des données ;
- panne prolongée d’un service critique ;
- indisponibilité d’une plateforme de traitement de données de santé ;
- suppression accidentelle sans sauvegarde exploitable.

### 3.5 Incident de sécurité sans violation confirmée

Tout événement pouvant affecter la confidentialité, l’intégrité ou la disponibilité, même si aucune violation de données personnelles n’est encore confirmée.

Un incident doit être traité comme une violation potentielle jusqu’à ce que l’analyse démontre de manière documentée qu’aucune donnée personnelle n’a été concernée.

### 3.6 Incident grave lié à un système d’IA

Incident susceptible d’entrer dans le champ de l’article 73 de l’AI Act, notamment lorsqu’un système d’IA cause ou contribue à causer :

- un décès ou une atteinte grave à la santé ;
- une perturbation grave de la gestion ou de l’exploitation d’une infrastructure critique ;
- une violation grave et avérée d’obligations fondamentales ;
- des dommages graves à des biens ou à l’environnement.

L’applicabilité de l’article 73 doit être évaluée au regard du rôle de Cortex Leman, du type de système d’IA, du statut du client et de la date d’application des obligations concernées.

---

## 4. Gouvernance et responsabilités

| Fonction | Responsabilités principales |
|---|---|
| Tout collaborateur ou prestataire | Signaler immédiatement tout incident suspect ; ne pas supprimer ni modifier les preuves |
| Service de surveillance / SOC / IT | Détection, qualification initiale, confinement technique, conservation des journaux |
| Responsable sécurité / RSSI | Direction technique de la réponse, analyse de l’impact et des mesures de remédiation |
| DPO | Qualification RGPD/LPD, analyse du risque, conseil sur les notifications, tenue du registre |
| Direction | Activation de la cellule de crise, arbitrage des ressources et validation des communications sensibles |
| Juriste / conseil externe | Analyse des obligations légales, contractuelles, professionnelles et sectorielles |
| Responsable client | Information du client concerné, coordination des décisions et du calendrier |
| Responsable IA / MLOps | Analyse des impacts liés au modèle, aux prompts, aux données d’entraînement et aux sorties |
| Communication | Préparation des messages externes, exclusivement après validation juridique et direction |
| Client responsable du traitement | Décision et, en principe, réalisation des notifications RGPD/LPD aux autorités et personnes concernées |

### 4.1 Principe de non-interférence

Aucun collaborateur ne doit :

- contacter une autorité ou une personne concernée sans validation de la cellule de crise, sauf urgence imposée par la loi ;
- communiquer publiquement sur l’incident ;
- supprimer, réinitialiser ou modifier les systèmes avant préservation des preuves ;
- reconnaître une responsabilité juridique ou contractuelle ;
- transmettre des données supplémentaires non nécessaires à l’analyse.

---

## 5. Niveaux de gravité

### 5.1 Classification opérationnelle

| Niveau | Description | Exemple | Action minimale |
|---|---|---|---|
| G0 — Faux positif | Aucun incident confirmé après vérification | Alerte bloquée sans exposition | Documenter et clôturer |
| G1 — Faible | Incident limité, sans donnée personnelle ou avec risque négligeable | Tentative bloquée, données fortement chiffrées, aucune consultation | Traiter, documenter, informer le client si prévu |
| G2 — Modéré | Violation confirmée avec risque limité pour les personnes | Données ordinaires, faible volume, accès rapidement révoqué | Informer le client sans délai ; notification autorité selon analyse |
| G3 — Élevé | Risque probable ou élevé pour les personnes | Données de santé, financières, juridiques, RH, identifiants ou volume important | Cellule de crise ; décision de notification ; préparation des personnes concernées |
| G4 — Critique | Risque très élevé, incident massif, systémique ou impact vital/financier majeur | Exfiltration de dossiers patients, compromission bancaire, incident IA grave | Notification immédiate au client et autorités compétentes ; communication de crise |

### 5.2 Critères d’évaluation

L’évaluation doit prendre en compte au minimum :

1. **Nature de la violation**
   - confidentialité ;
   - intégrité ;
   - disponibilité ;
   - combinaison de plusieurs impacts.

2. **Volume de données**
   - nombre approximatif de personnes ;
   - nombre d’enregistrements ;
   - durée d’exposition ;
   - quantité de données exfiltrées ou accessibles.

3. **Sensibilité des données**
   - données de santé au sens de l’article 9 du RGPD ;
   - données génétiques ou biométriques ;
   - données financières et bancaires ;
   - identifiants, mots de passe, secrets d’authentification ;
   - données relatives aux infractions ;
   - données de mineurs ou de personnes vulnérables ;
   - données RH ;
   - données couvertes par le secret professionnel ou le secret bancaire.

4. **Nombre et profil des personnes**
   - patients ;
   - clients bancaires ;
   - salariés ou candidats ;
   - clients d’un avocat ;
   - personnes vulnérables ;
   - mineurs ;
   - personnes exposées à un risque de discrimination, fraude, chantage ou atteinte à la réputation.

5. **Criticité verticale**
   - santé : risque vital, diagnostic, continuité des soins ;
   - banque : fraude, perte financière, secret bancaire, stabilité ou confiance ;
   - avocat : secret professionnel, stratégie contentieuse, réputation ;
   - comptabilité : données financières, fiscales et patrimoniales ;
   - RH : discrimination, emploi, rémunération, données sociales ;
   - autres secteurs : impact sur les droits et libertés et continuité d’activité.

6. **Facilité d’exploitation**
   - données en clair ou chiffrées ;
   - clés compromises ou non ;
   - pseudonymisation effective ;
   - possibilité d’identifier les personnes ;
   - données directement exploitables.

7. **Durée et étendue de l’exposition**
   - accès ponctuel ou persistant ;
   - présence d’un acteur externe ;
   - diffusion publique ;
   - réutilisation ou copie des données.

8. **Mesures déjà prises**
   - isolement ;
   - révocation des accès ;
   - restauration ;
   - suppression des copies ;
   - confirmation de la non-exploitation ;
   - notification volontaire des personnes.

### 5.3 Décision de notification

#### RGPD — notification à l’autorité

Le responsable du traitement notifie la violation à l’autorité de contrôle compétente **dans les meilleurs délais et, si possible, dans les 72 heures après en avoir pris connaissance**, lorsque la violation est susceptible d’engendrer un risque pour les droits et libertés des personnes — **article 33, paragraphe 1, du RGPD**.

Lorsque Cortex Leman agit comme sous-traitant, il informe le client responsable du traitement **sans délai injustifié**, conformément à l’article 33, paragraphe 2, du RGPD et au contrat applicable.

#### RGPD — communication aux personnes

Une communication aux personnes concernées est requise lorsque la violation est susceptible d’engendrer un **risque élevé** pour leurs droits et libertés — **article 34 du RGPD** — sauf exception applicable.

#### LPD — notification au PFPDT

Selon l’article 24 LPD, le responsable du traitement annonce au PFPDT, dans les meilleurs délais, une violation de la sécurité des données lorsqu’elle est vraisemblablement susceptible d’entraîner un risque élevé pour la personnalité ou les droits fondamentaux de la personne concernée.

Le délai de 72 heures constitue une cible interne stricte pour les incidents FR/CH, mais ne remplace pas l’analyse du délai légal applicable en Suisse.

#### AI Act — incidents graves

Lorsque l’article 73 de l’AI Act est applicable, l’incident grave doit être évalué et notifié à l’autorité compétente dans les délais prévus par cet article et les textes d’application. Cette obligation est distincte des notifications RGPD et LPD.

---

## 6. Procédure opérationnelle — T0 à T+1 heure

### 6.1 Détection

Un incident peut être détecté par :

- systèmes automatiques :
  - SIEM ;
  - EDR/XDR ;
  - détection d’exfiltration ;
  - alertes IAM ;
  - surveillance cloud ;
  - outils DLP ;
  - contrôles de disponibilité ;
  - monitoring des modèles et API ;
  - alertes de fournisseurs ;
- signalement manuel :
  - collaborateur ;
  - client ;
  - personne concernée ;
  - prestataire ;
  - autorité ;
  - chercheur en sécurité ;
  - fournisseur cloud ou logiciel.

### 6.2 Canaux internes de signalement

Tout signalement doit être effectué immédiatement par l’un des canaux suivants :

| Canal | Coordonnées |
|---|---|
| Email sécurisé incidents | `[incident@cortex-leman.example]` |
| Téléphone cellule de crise | `[+41 XX XXX XX XX]` |
| Numéro de permanence 24/7 | `[+41 XX XXX XX XX]` |
| Canal sécurisé interne | `[Nom de l’outil / URL]` |
| Escalade DPO | `[dpo@cortex-leman.example]` |
| Escalade RSSI | `[rssi@cortex-leman.example]` |

Les coordonnées ci-dessus doivent être remplacées par les coordonnées réelles avant diffusion.

Le signalement initial doit comporter, si connu :

- date et heure de détection ;
- personne ou outil ayant détecté l’événement ;
- système concerné ;
- client concerné ;
- type d’incident suspecté ;
- données potentiellement concernées ;
- mesures déjà prises ;
- niveau d’urgence apparent.

### 6.3 Actions obligatoires dans la première heure

La personne qui reçoit le signalement doit :

1. attribuer un identifiant unique :
   - `[INC-AAAA-MM-JJ-XXX]` ;
2. enregistrer l’heure T0 ;
3. accuser réception au déclarant ;
4. alerter immédiatement le RSSI, le DPO et le responsable client ;
5. déterminer si des données personnelles sont potentiellement concernées ;
6. activer la cellule de crise si le niveau présumé est G2 ou supérieur ;
7. isoler les composants affectés lorsque cela est techniquement possible ;
8. révoquer ou suspendre les comptes, tokens, clés et sessions compromis ;
9. bloquer les flux malveillants ;
10. préserver les preuves avant toute action destructive ;
11. vérifier les sauvegardes et la capacité de restauration ;
12. identifier les clients, environnements et pays concernés ;
13. consigner chaque décision et chaque horodatage.

### 6.4 Mesures de confinement

Selon la nature de l’incident :

- segmentation ou isolement réseau ;
- arrêt contrôlé d’un service exposé ;
- révocation des credentials ;
- rotation des clés et secrets ;
- suspension d’une intégration ou API ;
- gel des suppressions automatiques ;
- activation d’un environnement de secours ;
- blocage des comptes d’export ;
- désactivation temporaire d’un modèle ou d’une fonctionnalité IA ;
- mise en quarantaine des postes ;
- conservation des journaux et snapshots ;
- restauration à partir d’une sauvegarde saine.

Le confinement doit être proportionné et ne doit pas détruire les éléments nécessaires à l’analyse forensique.

### 6.5 Activation de la cellule de crise

La cellule de crise comprend au minimum :

- DPO ;
- RSSI ou responsable sécurité ;
- responsable informatique/Cloud ;
- responsable client ;
- direction ;
- juriste ou conseil externe ;
- responsable IA/MLOps, si système d’IA concerné ;
- communication, si une communication externe est probable.

**Chef de crise :** `[Nom / fonction]`  
**Suppléant :** `[Nom / fonction]`

---

## 7. Évaluation de la gravité — T+1 heure à T+4 heures

### 7.1 Objectifs

Dans les quatre premières heures, la cellule de crise doit :

- confirmer ou écarter l’existence d’une violation ;
- identifier les clients et traitements concernés ;
- estimer les catégories et le volume de données ;
- évaluer le risque pour les personnes ;
- déterminer les obligations de notification ;
- décider des premières mesures de communication ;
- établir les informations manquantes et leur responsable.

L’évaluation initiale peut être fondée sur des estimations. Les informations complémentaires sont transmises ultérieurement dès qu’elles sont disponibles.

### 7.2 Matrice de scoring

Attribuer un score de 0 à 3 pour chaque critère.

| Critère | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Volume | 0 personne ou données non personnelles | 1 à 10 personnes | 11 à 1 000 personnes | Plus de 1 000 personnes ou volume inconnu avec exposition potentielle |
| Sensibilité | Données non sensibles ou anonymisées | Données ordinaires limitées | Identifiants, données financières, RH ou professionnelles | Santé, biométrie, données pénales, secrets bancaire/professionnel, mineurs |
| Confidentialité | Aucun accès non autorisé | Tentative bloquée | Accès limité ou interne | Exfiltration, diffusion publique ou accès externe confirmé |
| Intégrité | Aucune altération | Altération réversible sans impact | Altération de données opérationnelles | Altération de données médicales, financières, juridiques ou critiques |
| Disponibilité | Aucun impact | Interruption inférieure à 1 heure | Interruption de 1 à 24 heures | Destruction, ransomware ou interruption supérieure à 24 heures |
| Vulnérabilité des personnes | Population générale sans conséquence identifiable | Impact limité | Personnes vulnérables ou risque de fraude/discrimination | Risque vital, financier grave, chantage ou atteinte majeure |
| Criticité verticale | Activité non critique | Activité importante | Secteur régulé | Santé, banque, secret professionnel ou système critique |
| Exploitabilité | Données anonymisées ou clés intactes | Chiffrement robuste, risque faible | Pseudonymisation partielle ou contrôle incertain | Données en clair, clés compromises ou exploitation constatée |
| Durée d’exposition | Moins de 15 minutes | 15 min à 4 h | 4 h à 24 h | Plus de 24 h ou durée inconnue |

### 7.3 Interprétation du score

| Score total | Niveau indicatif | Décision |
|---:|---|---|
| 0–5 | G0/G1 | Pas de notification généralement requise ; justification obligatoire |
| 6–11 | G2 | Notification du client ; analyse de la notification à l’autorité |
| 12–18 | G3 | Notification du client et préparation de la notification à l’autorité ; communication aux personnes à évaluer |
| 19–27 | G4 | Escalade immédiate ; notification aux autorités et personnes selon les obligations applicables ; communication de crise |

Le score ne remplace pas l’analyse juridique. Un seul critère peut justifier une notification, notamment :

- exposition de données de santé ;
- compromission de comptes bancaires ;
- violation du secret professionnel ;
- atteinte à l’intégrité de données médicales ou financières ;
- incident susceptible de relever de l’article 73 AI Act ;
- risque élevé pour une personne ou une catégorie de personnes.

### 7.4 Décision formalisée

La décision doit être validée par le DPO et, lorsque nécessaire, par le client responsable du traitement et la direction.

| Question | Réponse |
|---|---|
| Violation confirmée ? | `[Oui / Non / À confirmer]` |
| Confidentialité affectée ? | `[Oui / Non / À confirmer]` |
| Intégrité affectée ? | `[Oui / Non / À confirmer]` |
| Disponibilité affectée ? | `[Oui / Non / À confirmer]` |
| Données de santé au sens de l’article 9 RGPD ? | `[Oui / Non / À confirmer]` |
| Secret bancaire potentiel ? | `[Oui / Non / À confirmer]` |
| Secret professionnel potentiel ? | `[Oui / Non / À confirmer]` |
| Incident grave AI Act potentiel ? | `[Oui / Non / À confirmer]` |
| Risque pour les droits et libertés ? | `[Nul / Faible / Probable / Élevé]` |
| Notification autorité requise ? | `[Oui / Non / À confirmer]` |
| Notification personnes requise ? | `[Oui / Non / À confirmer]` |
| Client responsable du traitement informé ? | `[Date/heure]` |
| Décision validée par | `[Nom / fonction / date / heure]` |

---

## 8. Information et notification des clients

### 8.1 Délai interne

Cortex Leman informe le client concerné :

- **immédiatement** pour un incident G3 ou G4 ;
- au plus tard dans les **4 heures** suivant T0 pour tout incident susceptible d’exiger une notification ;
- sans délai injustifié pour tout autre incident confirmé impliquant des données personnelles.

Le contrat client peut imposer un délai plus court. Le délai contractuel le plus exigeant s’applique.

### 8.2 Contenu de l’information initiale

L’information doit contenir, dans la mesure disponible :

- identifiant de l’incident ;
- date et heure de détection ;
- date et heure présumée du début ;
- systèmes et environnements concernés ;
- nature de la violation ;
- catégories de données ;
- nombre estimé de personnes et d’enregistrements ;
- catégories de personnes concernées ;
- risques identifiés ;
- mesures de confinement ;
- mesures correctives prévues ;
- coordonnées du DPO ou du point de contact ;
- informations encore inconnues ;
- calendrier des mises à jour.

### 8.3 Clients à verticales régulées

| Client | Vigilances spécifiques | Escalade minimale |
|---|---|---|
| Hôpital de Genève | Données de santé, confidentialité médicale, continuité des soins | DPO, RSSI, Dr Laurent, conseil juridique ; autorités suisses compétentes selon analyse |
| UBank SA | Données financières, secret bancaire, fraude, exigences FINMA | DPO, RSSI, T. Muller, fonction conformité/risques, FINMA selon obligations |
| Martin Avocat | Secret professionnel, stratégie contentieuse, pièces sensibles | DPO, P. Martin, conseil juridique ; analyse de l’art. 321 CP |
| Dupont Comptable | Données fiscales, patrimoniales et financières | Responsable client, DPO, conseil juridique |
| Groupe RH | Données salariés, rémunération, recrutement, discrimination | Responsable client, DPO, conseil juridique |
| StartupParis | Données clients et utilisateurs, exposition transfrontalière | Responsable client, DPO |
| Darkom-debarras | Données clients et opérationnelles | Responsable client, DPO |

---

## 9. Notification CNIL — France

### 9.1 Autorité compétente

La notification doit être adressée à la **CNIL** lorsque celle-ci est l’autorité de contrôle compétente, notamment pour un responsable du traitement établi ou opérant dans le périmètre français concerné.

Formulaire indiqué :

**https://www.cnil.fr/notifier-une-violation**

La validité et l’URL du formulaire doivent être vérifiées avant utilisation.

### 9.2 Délai

Le responsable du traitement notifie la violation à la CNIL :

- dans les meilleurs délais ;
- si possible dans les **72 heures** après en avoir pris connaissance ;
- en cas de dépassement, avec indication des motifs du retard.

Pour Cortex Leman, sous-traitant, l’objectif interne est de transmettre au client toutes les informations disponibles au plus tard à **T+24 heures**, afin de permettre au responsable du traitement de respecter son délai de 72 heures.

### 9.3 Contenu obligatoire ou attendu

La notification doit comprendre, selon les informations disponibles :

1. la nature de la violation ;
2. les catégories et le nombre approximatif de personnes concernées ;
3. les catégories et le nombre approximatif d’enregistrements concernés ;
4. le nom et les coordonnées du DPO ou du point de contact ;
5. les conséquences probables de la violation ;
6. les mesures prises ou proposées pour remédier à la violation ;
7. les mesures prises pour atténuer les éventuels effets négatifs ;
8. les raisons d’un éventuel retard ;
9. la chronologie de l’incident ;
10. l’identité des sous-traitants ou fournisseurs impliqués ;
11. les pays concernés ;
12. les pièces utiles, sans transmettre de données personnelles non nécessaires.

### 9.4 Données de santé — article 9 RGPD

Lorsque l’incident concerne des données de santé :

- le caractère « catégorie particulière de données » doit être expressément indiqué ;
- le traitement doit être rattaché à l’article 9 RGPD pertinent ;
- le niveau de risque doit tenir compte des conséquences médicales, psychologiques, sociales et réputationnelles ;
- l’intégrité des données doit être analysée séparément de leur confidentialité ;
- les risques de perturbation de la continuité des soins doivent être évalués ;
- aucune donnée de santé nominative ne doit être communiquée à la CNIL au-delà de ce qui est nécessaire ;
- le client, l’établissement de santé et les autorités sectorielles éventuellement compétentes doivent être associés selon le contrat et le droit applicable.

---

## 10. Notification PFPDT — Suisse

### 10.1 Autorité et formulaire

La notification au PFPDT est effectuée via le canal officiel applicable, notamment :

**https://www.dataprivacy.ch/notification**

La disponibilité, l’authenticité et l’URL du formulaire doivent être vérifiées au moment de la notification. En cas d’indisponibilité, utiliser le canal officiel publié par le PFPDT et conserver la preuve de la tentative de notification.

### 10.2 Délai

Selon l’article 24 LPD, le responsable du traitement annonce au PFPDT, dans les meilleurs délais, les violations de la sécurité des données vraisemblablement susceptibles d’entraîner un risque élevé pour la personnalité ou les droits fondamentaux.

Cortex Leman applique une cible interne de notification ou de transmission au client :

- T+4 heures : décision préliminaire ;
- T+24 heures : dossier initial complet dans la mesure du possible ;
- au plus tard T+72 heures : transmission ou notification initiale pour les incidents relevant également du RGPD, sauf instruction juridique contraire.

### 10.3 Contenu

La notification doit contenir notamment :

- nature de la violation ;
- date et durée de l’incident ;
- date de détection ;
- catégories de données concernées ;
- catégories et nombre estimé de personnes concernées ;
- conséquences probables ;
- mesures prises ou prévues ;
- coordonnées du responsable et du DPO ;
- clients et sous-traitants impliqués ;
- pays concernés ;
- justification du délai ;
- statut de l’information des personnes concernées.

### 10.4 Secret bancaire — article 47 LB

En cas d’incident affectant UBank SA ou des données susceptibles d’être couvertes par le secret bancaire :

- informer immédiatement T. Muller et la fonction conformité/risques de UBank SA ;
- identifier la nature des données bancaires exposées ;
- déterminer si des personnes non autorisées ont eu connaissance des données ;
- préserver les preuves et limiter toute diffusion ;
- analyser les obligations de UBank SA au titre de l’article 47 LB ;
- déterminer, avec UBank SA et son conseil, si une information ou notification à la FINMA est nécessaire ;
- ne communiquer à FINMA que les informations nécessaires et validées.

### 10.5 Secret professionnel — article 321 CP

En cas d’incident affectant Martin Avocat ou des données couvertes par le secret professionnel :

- informer immédiatement P. Martin ;
- limiter strictement l’accès aux informations ;
- ne pas inclure de contenu de dossiers, pièces, stratégies ou correspondances dans les communications non nécessaires ;
- analyser l’application de l’article 321 CP ;
- obtenir les instructions du client et du conseil juridique avant toute divulgation ;
- documenter la base juridique de toute communication à une autorité ou à un tiers.

### 10.6 Double notification PFPDT et FINMA — vertical bancaire

Pour un incident affectant UBank SA, la cellule de crise doit systématiquement ouvrir une analyse « PFPDT + FINMA ».

La notification à la FINMA n’est pas automatiquement substituée à la notification PFPDT. Les deux régimes doivent être examinés séparément.

| Action | Responsable | Délai interne |
|---|---|---|
| Informer UBank SA | Responsable client / DPO | Immédiat, G3/G4 |
| Évaluer le secret bancaire | UBank SA + conseil juridique | T+4 h |
| Évaluer la notification PFPDT | DPO + UBank SA | T+4 h |
| Évaluer la notification FINMA | UBank SA conformité/risques | T+4 h |
| Préparer les notifications | Client, assisté par Cortex | T+24 h |
| Effectuer les notifications | Entité légalement responsable | Selon délai applicable |

---

## 11. Notification des personnes concernées

### 11.1 Conditions

Une communication aux personnes concernées doit être effectuée lorsque la violation est susceptible d’engendrer un **risque élevé** pour leurs droits et libertés — article 34 RGPD.

En Suisse, l’article 25 LPD impose également une information lorsque cela est nécessaire à la protection de la personne concernée ou lorsque le PFPDT l’exige, sous réserve des restrictions prévues par l’article 26 LPD.

La communication doit intervenir **sans retard excessif** après la décision de notifier.

### 11.2 Contenu minimal

La communication doit être claire, concise et facilement accessible. Elle contient :

- la nature de la violation ;
- les données ou catégories de données concernées ;
- la période ou date de l’incident, si connue ;
- les conséquences probables ;
- les mesures prises par Cortex Leman et le client ;
- les mesures recommandées aux personnes :
  - changement de mot de passe ;
  - activation de l’authentification multifacteur ;
  - vigilance contre le phishing ;
  - surveillance des comptes ;
  - contact de la banque ;
  - opposition ou renouvellement de documents, si nécessaire ;
- les coordonnées du DPO ou point de contact ;
- les coordonnées du client responsable du traitement ;
- les moyens d’obtenir des informations complémentaires ;
- le cas échéant, les coordonnées d’un service d’assistance dédié.

### 11.3 Forme

La communication est effectuée par un moyen permettant de limiter les risques secondaires :

- email individualisé ;
- courrier ;
- espace sécurisé ;
- notification dans une application ;
- appel téléphonique pour les situations critiques ;
- communication publique uniquement si nécessaire et validée.

Une communication ne doit jamais révéler l’adresse ou l’identité d’autres personnes concernées.

### 11.4 Exceptions à la communication RGPD

La communication individuelle peut ne pas être requise notamment lorsque :

1. des mesures techniques et organisationnelles appropriées ont été mises en œuvre avant la violation, telles que le chiffrement rendant les données incompréhensibles aux personnes non autorisées ;
2. des mesures ultérieures garantissent que le risque élevé ne se matérialisera probablement plus ;
3. une communication individuelle exigerait des efforts disproportionnés, auquel cas une communication publique efficace et équivalente peut être utilisée, sous réserve de validation juridique ;
4. une restriction légale ou une décision d’autorité s’applique.

Toute exception doit être documentée, motivée et validée par le DPO et le client responsable du traitement.

### 11.5 Cas des données de santé, bancaires et couvertes par un secret

La communication doit être coordonnée avec le client afin de :

- ne pas aggraver le risque médical ou financier ;
- ne pas révéler indirectement l’existence d’un dossier ou d’une relation professionnelle ;
- ne pas divulguer le secret bancaire ou professionnel ;
- utiliser un canal d’authentification adapté ;
- prévoir une assistance aux personnes vulnérables.

---

## 12. Notification des incidents graves liés à l’IA — AI Act

### 12.1 Déclenchement de l’analyse

Une analyse AI Act est obligatoire lorsque l’incident concerne :

- un modèle ou système d’IA exploité par Cortex Leman ;
- un composant fourni, intégré ou maintenu par Cortex Leman ;
- des sorties susceptibles d’avoir causé un dommage grave ;
- une décision ou recommandation automatisée ayant produit un effet critique ;
- une atteinte grave à la santé, aux infrastructures critiques, aux droits fondamentaux ou aux biens.

### 12.2 Actions

La cellule de crise doit :

1. identifier le système, la version du modèle et l’environnement ;
2. conserver les prompts, entrées, sorties, paramètres, logs et traces de décision ;
3. suspendre le système ou le cas d’usage si nécessaire ;
4. identifier les utilisateurs et personnes potentiellement affectés ;
5. évaluer si l’incident constitue une violation de données personnelles ;
6. analyser l’article 73 AI Act et les obligations sectorielles ;
7. informer le client déployeur ou fournisseur ;
8. identifier l’autorité de surveillance compétente ;
9. préparer les notifications séparées AI Act, RGPD et LPD ;
10. documenter les mesures de correction et de prévention de la récurrence.

---

## 13. Documentation interne et registre des violations

### 13.1 Obligation

Toute violation, y compris lorsqu’elle n’est pas notifiée à une autorité, doit être documentée afin de permettre à Cortex Leman et au responsable du traitement de démontrer le respect des obligations applicables.

Pour le RG
