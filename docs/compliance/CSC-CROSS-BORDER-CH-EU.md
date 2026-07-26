# docs/compliance/CSC-CROSS-BORDER-CH-EU.md

# Clauses contractuelles standard — Transferts transfrontaliers CH–UE  
## Cortex Leman SARL — Cortex Leman v5

**Version :** [●]  
**Date d’effet :** [●]  
**Exportateur de données :** [Cortex Leman SARL / Client concerné]  
**Importateur de données :** [Cortex Leman SARL / Entité UE concernée]  
**Responsable du traitement :** [●]  
**Sous-traitant :** Cortex Leman SARL, [adresse complète], Suisse  
**Contact protection des données :** [DPO / conseiller à la protection des données / adresse e-mail]  

> **Document modèle — validation obligatoire avant signature.**  
> Le présent document constitue un modèle contractuel à adapter aux flux effectivement réalisés, au rôle de chaque partie, aux catégories de données, aux pays concernés et aux exigences sectorielles applicables. Il doit être revu et validé par un avocat qualifié en droit suisse et, lorsque le RGPD est applicable, en droit de l’Union européenne, avant toute signature ou mise en œuvre.

---

## Préambule commun

Les présentes clauses contractuelles standard (« **Clauses** » ou « **CSC** ») encadrent les transferts internationaux de données personnelles entre la Suisse et l’Union européenne ou l’Espace économique européen (« **EEE** »), réalisés dans le cadre des services d’intelligence artificielle, d’hébergement, d’inférence, de maintenance et de support fournis par Cortex Leman SARL (« **Cortex Leman** »).

Elles sont fondées, selon le flux concerné, sur :

1. la décision d’exécution (UE) 2021/914 de la Commission européenne du 4 juin 2021 relative aux clauses contractuelles types pour le transfert de données à caractère personnel vers des pays tiers ;
2. la loi fédérale suisse sur la protection des données (« **LPD** ») et son ordonnance d’exécution (« **OPDo** ») ;
3. le RGPD, lorsque le responsable du traitement ou le traitement relève de son champ d’application ;
4. les exigences sectorielles applicables, notamment en matière de santé, de secret bancaire ou de secret professionnel de l’avocat ;
5. le règlement (UE) 2024/1689 établissant des règles harmonisées concernant l’intelligence artificielle (« **AI Act** »), lorsqu’il est applicable.

Les présentes Clauses ne remplacent pas les dispositions impératives applicables au traitement, notamment les obligations résultant de la LPD, du RGPD, de la législation bancaire, de la législation sur la profession d’avocat ou de la réglementation sanitaire.

---

# Section 1 — CSC générale CH → UE  
## Squelette commun

### Article 1 — Objet et portée

1. Les présentes Clauses ont pour objet d’encadrer le transfert de données personnelles depuis la Suisse vers [la France / un autre État membre de l’UE ou de l’EEE], ou inversement lorsque le rôle des parties l’exige.

2. Les Clauses s’appliquent aux traitements réalisés dans le cadre du contrat principal suivant :

   - **Contrat principal :** [intitulé et référence] ;
   - **Date de signature :** [●] ;
   - **Services concernés :** [hébergement / inférence IA / annotation / support / maintenance / autre] ;
   - **Durée :** [●] ;
   - **Système concerné :** Cortex Leman v5 ;
   - **Environnement concerné :** [production / test / développement / secours].

3. Les parties déterminent expressément leur qualité respective :

   - **Exportateur de données :** [nom, adresse et rôle] ;
   - **Importateur de données :** [nom, adresse et rôle] ;
   - **Responsable du traitement :** [●] ;
   - **Sous-traitant ou importateur ultérieur :** [●].

4. Lorsque Cortex Leman agit en qualité de sous-traitant, le client demeure responsable de la licéité du traitement, de la détermination des finalités et moyens essentiels du traitement, de l’information des personnes concernées et de la réponse aux demandes d’exercice de leurs droits.

5. Lorsque le transfert relève du RGPD et que le pays de destination ne bénéficie pas d’une décision d’adéquation applicable, les parties sélectionnent le module approprié de la décision d’exécution (UE) 2021/914 :

   - **Module 1 :** responsable du traitement vers responsable du traitement ;
   - **Module 2 :** responsable du traitement vers sous-traitant ;
   - **Module 3 :** sous-traitant vers sous-traitant ;
   - **Module 4 :** sous-traitant vers responsable du traitement.

6. La présente version est conçue prioritairement pour le **Module 2** ou le **Module 3**, selon la qualification retenue dans le contrat principal. Cette qualification doit être confirmée avant signature.

7. Pour les transferts régis par la LPD, les parties conviennent que les présentes Clauses constituent une garantie contractuelle appropriée, sous réserve de leur adaptation aux exigences suisses et de la réalisation d’une analyse de l’impact du droit et des pratiques du pays de destination lorsque celle-ci est nécessaire.

---

### Article 2 — Détails du transfert

Les détails du transfert sont les suivants.

#### 2.1 Pays exportateur

- **Pays :** Suisse ;
- **Canton :** [●] ;
- **Entité exportatrice :** [●] ;
- **Autorité ou organisme compétent :** [PFPDT / autre autorité cantonale compétente, le cas échéant].

#### 2.2 Pays importateur

- **Pays :** [France / autre État membre de l’UE ou de l’EEE] ;
- **Entité importatrice :** [●] ;
- **Lieu principal de traitement :** [●] ;
- **Sous-traitants ultérieurs autorisés :** voir Article 6 et Annexe 2.

#### 2.3 Personnes concernées

Les catégories de personnes concernées peuvent inclure :

- clients, patients, usagers ou bénéficiaires ;
- employés, collaborateurs et candidats ;
- mandataires, représentants légaux et ayants droit ;
- clients bancaires et contreparties ;
- clients de cabinets d’avocats, témoins, adversaires et autres personnes mentionnées dans des dossiers ;
- utilisateurs administrateurs et utilisateurs finaux de Cortex Leman v5.

#### 2.4 Catégories de données

Selon le service souscrit, les données peuvent inclure :

- données d’identification et coordonnées ;
- données professionnelles et administratives ;
- données de connexion, journaux, métadonnées et données de sécurité ;
- contenus transmis à l’outil d’IA, documents, courriels, pièces jointes et transcriptions ;
- données financières et informations relatives à la relation bancaire ;
- données couvertes par le secret professionnel ;
- données de santé et autres catégories particulières ou sensibles ;
- données relatives à des infractions ou condamnations, lorsque le traitement est légalement autorisé.

#### 2.5 Finalités

Les données sont traitées exclusivement pour :

- fournir les services Cortex Leman v5 ;
- héberger, indexer, sécuriser et restituer les données ;
- exécuter des traitements d’inférence ou d’analyse IA demandés par le client ;
- assurer le support, la maintenance et la sécurité ;
- détecter et prévenir les abus, incidents ou accès non autorisés ;
- respecter les obligations légales applicables.

Les données ne sont pas utilisées pour entraîner un modèle général ou un modèle destiné à des tiers sans instruction documentée et autorisation écrite préalable du client.

#### 2.6 Fréquence et durée

- **Fréquence :** [continue / ponctuelle / à la demande] ;
- **Durée du transfert :** pendant la durée du contrat, augmentée des délais de restitution, suppression ou archivage légal ;
- **Date de fin prévue :** [●].

---

### Article 3 — Obligations de l’exportateur de données

L’exportateur de données s’engage à :

1. vérifier la licéité du traitement et du transfert ;
2. disposer d’une base légale appropriée au traitement ;
3. fournir les informations requises aux personnes concernées ;
4. vérifier que les instructions adressées à l’importateur sont documentées, licites et suffisamment précises ;
5. ne transmettre que les données adéquates, pertinentes et limitées à ce qui est nécessaire ;
6. déterminer les durées de conservation applicables ;
7. instruire l’importateur sur les catégories particulières de données et les exigences sectorielles ;
8. réaliser ou faire réaliser, lorsque nécessaire, une analyse du transfert et des risques liés au droit du pays importateur ;
9. coopérer avec l’importateur en cas de demande d’une autorité de contrôle ;
10. informer l’importateur de toute modification affectant la licéité du traitement, la base légale ou les finalités.

Lorsque Cortex Leman est l’exportateur, elle doit également vérifier la licéité de l’exportation, documenter l’entité importatrice, maintenir un registre des transferts et s’assurer que les garanties contractuelles applicables sont en vigueur.

---

### Article 4 — Obligations de l’importateur de données

L’importateur s’engage à :

1. traiter les données uniquement sur instructions documentées de l’exportateur ;
2. ne pas vendre, louer, divulguer, réutiliser ou exploiter les données à ses propres fins, sauf obligation légale ;
3. garantir que les personnes autorisées à traiter les données sont soumises à une obligation de confidentialité ;
4. limiter l’accès aux données selon le principe du besoin d’en connaître ;
5. informer rapidement l’exportateur s’il estime qu’une instruction viole le RGPD, la LPD ou toute autre règle impérative ;
6. coopérer avec l’exportateur pour répondre aux demandes des personnes concernées ;
7. maintenir une documentation suffisante permettant de démontrer la conformité ;
8. permettre et faciliter les audits prévus par les présentes Clauses ;
9. notifier sans délai toute demande juridiquement contraignante d’une autorité publique visant les données transférées, sauf interdiction légale ;
10. contester, lorsque cela est raisonnablement possible, toute demande manifestement disproportionnée ou illégale ;
11. documenter et communiquer les limitations pratiques ou juridiques empêchant une notification ;
12. ne pas transférer les données à un autre pays ou à un autre sous-traitant sans respecter l’Article 6.

L’importateur doit notamment prendre en compte les éventuels accès des autorités publiques du pays de destination et informer l’exportateur de tout changement susceptible de compromettre les garanties prévues par les présentes Clauses.

---

### Article 5 — Sécurité des données  
#### RGPD, article 32 — LPD, article 7

1. Les parties mettent en œuvre des mesures techniques et organisationnelles appropriées au risque, conformément notamment à l’article 32 du RGPD et à l’article 7 LPD.

2. Les mesures comprennent au minimum :

   - chiffrement des données en transit au moyen de protocoles modernes ;
   - chiffrement des données au repos ;
   - gestion séparée et sécurisée des clés cryptographiques ;
   - authentification forte pour les accès privilégiés ;
   - gestion des habilitations selon le principe du moindre privilège ;
   - journalisation des accès, opérations administratives et événements de sécurité ;
   - surveillance et détection des comportements anormaux ;
   - segmentation des environnements ;
   - procédures de sauvegarde, restauration et continuité ;
   - tests réguliers de sécurité et de résilience ;
   - gestion des vulnérabilités et correctifs ;
   - procédures de suppression sécurisée ;
   - sensibilisation et formation du personnel ;
   - plan de réponse aux incidents ;
   - contrôle des sous-traitants ultérieurs.

3. Cortex Leman maintient une documentation de sécurité comprenant notamment :

   - la description des mesures appliquées ;
   - les résultats des tests ou audits disponibles ;
   - les certificats ou rapports de conformité détenus ;
   - la liste des sous-traitants ultérieurs autorisés ;
   - les procédures de gestion des incidents.

4. L’utilisation des données pour l’entraînement d’un modèle généraliste, l’amélioration d’un produit mutualisé ou la constitution d’une base de données destinée à des tiers est interdite, sauf accord écrit, spécifique et documenté du client.

5. Les mesures spécifiques applicables aux secteurs de la santé, de la banque et de la profession d’avocat figurent respectivement aux Sections 2, 3 et 4.

---

### Article 6 — Sous-traitants ultérieurs

1. L’importateur ne peut engager un sous-traitant ultérieur qu’avec l’autorisation :

   - [générale / spécifique] de l’exportateur ;
   - selon la procédure prévue au contrat principal ;
   - après information préalable du nom, du pays, de la fonction et de l’accès envisagé.

2. Tout sous-traitant ultérieur doit être lié par un contrat imposant des obligations de protection des données et de sécurité au moins équivalentes à celles des présentes Clauses.

3. L’importateur demeure pleinement responsable envers l’exportateur de l’exécution des obligations de tout sous-traitant ultérieur.

4. Aucun sous-traitant ultérieur ne peut accéder aux données depuis un pays non autorisé sans :

   - analyse préalable du transfert ;
   - garantie juridique appropriée ;
   - mesure supplémentaire lorsque nécessaire ;
   - information et, le cas échéant, autorisation du client.

5. La liste initiale des sous-traitants ultérieurs autorisés est la suivante :

| Sous-traitant | Pays | Service | Catégories de données | Autorisation |
|---|---|---|---|---|
| [●] | [●] | [●] | [●] | [●] |

---

### Article 7 — Droits des personnes concernées

1. L’importateur assiste l’exportateur, dans la mesure du possible, pour répondre aux demandes d’exercice des droits prévus par le RGPD et la LPD, notamment :

   - droit d’accès ;
   - droit de rectification ;
   - droit à l’effacement ;
   - droit à la limitation ;
   - droit à la portabilité ;
   - droit d’opposition ;
   - droits relatifs aux décisions automatisées, lorsqu’ils sont applicables.

2. L’importateur ne répond pas directement à une personne concernée, sauf instruction de l’exportateur ou obligation légale.

3. Toute demande reçue directement est transmise à l’exportateur dans un délai maximal de **[24 heures]**, avec les informations disponibles permettant son traitement.

4. L’importateur met en œuvre les moyens raisonnables permettant :

   - la recherche et l’extraction des données ;
   - la correction ou suppression ;
   - l’application d’une limitation ;
   - la traçabilité des opérations réalisées ;
   - la restitution dans un format structuré et couramment utilisé.

5. Les coûts exceptionnels d’assistance sont traités conformément au contrat principal, sans limiter les obligations légales de coopération.

---

### Article 8 — Notification de violation de données

1. L’importateur informe l’exportateur de toute violation de données personnelles **sans délai indu et, en tout état de cause, dans un délai contractuel cible inférieur à 72 heures** à compter du moment où il en a connaissance.

2. La notification initiale comporte, dans la mesure des informations disponibles :

   - la nature de la violation ;
   - les catégories et le nombre approximatif de personnes concernées ;
   - les catégories et le volume approximatif de données ;
   - les conséquences probables ;
   - les mesures prises ou envisagées pour remédier à la violation ;
   - le nom et les coordonnées du point de contact.

3. L’importateur complète la notification au fur et à mesure de la disponibilité des informations.

4. L’exportateur demeure responsable de déterminer s’il doit notifier :

   - la **CNIL**, lorsque le RGPD est applicable ;
   - le **Préposé fédéral à la protection des données et à la transparence (« PFPDT »)**, lorsque la LPD l’exige ;
   - une autorité cantonale, sectorielle ou professionnelle compétente ;
   - les personnes concernées.

5. Les parties coopèrent à la gestion de l’incident, à la conservation des preuves, à l’analyse forensique, à l’information des autorités et à la remédiation.

6. Le délai contractuel de 72 heures ne modifie pas la répartition légale des responsabilités : sous le RGPD, la notification à l’autorité incombe en principe au responsable du traitement, tandis que le sous-traitant doit notifier le responsable du traitement sans délai indu.

---

### Article 9 — Loi applicable et juridiction

1. Les présentes Clauses sont régies par :

   - le droit impératif applicable au transfert ;
   - pour les aspects contractuels complémentaires, le droit de [Suisse / France / autre] ;
   - les dispositions impératives du RGPD et de la LPD lorsqu’elles sont applicables.

2. Les litiges relèvent de la compétence exclusive des tribunaux de [Genève / Paris / autre], sous réserve :

   - des compétences impératives des autorités de contrôle ;
   - des droits des personnes concernées ;
   - des règles impératives applicables aux transferts internationaux ;
   - des compétences de la FINMA ou d’une autorité professionnelle.

3. Les droits des personnes concernées prévus par le RGPD, la LPD ou toute autre loi impérative ne peuvent être limités par la présente clause attributive de juridiction.

---

# Section 2 — Clause spécifique Santé  
## Dr Sophie Laurent — Hôpital de Genève

### Article S1 — Parties et périmètre

- **Client / responsable du traitement :** Dr Sophie Laurent / Hôpital de Genève, [forme et adresse] ;
- **Délégué à la protection des données de l’hôpital :** [nom, coordonnées] ;
- **Fournisseur / sous-traitant :** Cortex Leman SARL ;
- **Tenant :** `tenant-hopital-geneve` ;
- **Services concernés :** [●] ;
- **Flux transfrontalier :** [Suisse → France / Suisse → UE / autre, à préciser] ;
- **Durée contractuelle :** [●].

### Article S2 — Données de santé et données sensibles

1. Les données traitées peuvent constituer :

   - des **données concernant la santé** au sens de l’article 9 RGPD ;
   - des données sensibles au sens de l’article 3 LPD ;
   - des données couvertes par le secret médical et les règles professionnelles applicables.

2. Le traitement de données de santé n’est autorisé que si le client dispose d’une base légale appropriée et, lorsque le RGPD s’applique, d’une exception valable à l’interdiction de l’article 9, paragraphe 1, RGPD.

3. Cortex Leman s’interdit :

   - d’utiliser les données à des fins commerciales propres ;
   - d’identifier ou de réidentifier des personnes en dehors des instructions ;
   - de combiner les données avec celles d’un autre client ;
   - de les utiliser pour l’entraînement d’un modèle mutualisé ;
   - de divulguer les données à un tiers non autorisé.

### Article S3 — AI Act et qualification du système

1. Les parties évaluent séparément si Cortex Leman v5 constitue un système d’IA à haut risque au sens de l’article 6 et de l’annexe III de l’AI Act, ou s’il est intégré à un produit réglementé, notamment un dispositif médical.

2. La seule utilisation dans le secteur de la santé ne suffit pas nécessairement à qualifier le système de « haut risque ». La qualification dépend de la fonction, de la finalité, de l’intégration au produit et des conditions d’utilisation.

3. Lorsque l’AI Act est applicable, les parties documentent notamment :

   - la finalité prévue ;
   - les responsabilités du fournisseur, du déployeur et du sous-traitant ;
   - la gouvernance des données ;
   - la traçabilité et la journalisation ;
   - la supervision humaine ;
   - la gestion des risques ;
   - l’exactitude, la robustesse et la cybersécurité ;
   - l’information des utilisateurs et des personnes concernées, lorsque requise.

4. Cortex Leman ne prend aucune décision clinique ou médicale à la place d’un professionnel de santé, sauf cadre réglementaire spécifique, validation et instruction écrite du client.

### Article S4 — Mesures renforcées

Pour le tenant `tenant-hopital-geneve`, Cortex Leman applique au minimum les mesures suivantes :

1. chiffrement de bout en bout lorsque techniquement possible ;
2. chiffrement des données au repos et en transit ;
3. gestion dédiée des clés cryptographiques ;
4. séparation logique et, lorsque requis, physique des environnements ;
5. interdiction de mutualiser les prompts, sorties, index, embeddings ou journaux avec ceux d’autres clients ;
6. authentification multifacteur pour les comptes administrateurs ;
7. accès administratifs limités, approuvés et journalisés ;
8. surveillance renforcée des accès ;
9. pseudonymisation ou minimisation avant transfert lorsque compatible avec la finalité ;
10. hébergement et stockage en Suisse exclusivement, sauf autorisation écrite préalable et garantie juridique documentée ;
11. désignation d’un DPO ou d’un référent protection des données par [Cortex Leman / l’hôpital], avec coordonnées communiquées aux parties ;
12. tests réguliers de restauration, de cloisonnement et d’intrusion ;
13. interdiction de traitement secondaire à des fins d’entraînement sans accord écrit spécifique.

### Article S5 — Rétention

1. Les données du tenant `tenant-hopital-geneve` sont conservées pendant une durée maximale de **180 jours**, sauf :

   - obligation légale contraire ;
   - nécessité de préserver une preuve ou de gérer un litige ;
   - instruction écrite du client ;
   - obligation médicale, réglementaire ou archivistique applicable à l’hôpital.

2. À l’expiration de cette durée, Cortex Leman supprime ou anonymise les données, y compris les copies, caches, index, embeddings, sauvegardes et journaux contenant des données personnelles, sous réserve des cycles techniques de sauvegarde documentés.

3. La politique applicable est la **politique `tenant-hopital-geneve`**.

4. Un rapport de suppression ou d’anonymisation est remis au client sur demande.

### Article S6 — Incidents et autorités

Tout incident affectant des données de santé est classé comme incident critique. Cortex Leman :

- avertit le client dans le délai prévu à l’Article 8 ;
- fournit un point de contact disponible 24 heures sur 24 pendant la gestion de l’incident ;
- assiste le client dans ses échanges avec la CNIL, le PFPDT, l’autorité cantonale compétente et les autorités sanitaires ;
- préserve les journaux et éléments techniques nécessaires à l’analyse.

---

# Section 3 — Clause spécifique Banque  
## Thomas Müller — UBank SA

### Article B1 — Parties et périmètre

- **Client / responsable du traitement :** UBank SA, [adresse] ;
- **Contact conformité / sécurité :** [●] ;
- **Fournisseur / sous-traitant :** Cortex Leman SARL ;
- **Tenant :** [tenant-ubank-sa] ;
- **Services concernés :** [●] ;
- **Lieu de résidence des données :** Suisse exclusivement ;
- **Date d’effet :** [●].

### Article B2 — Secret bancaire

1. Les données peuvent être soumises au secret bancaire prévu par l’article 47 de la loi fédérale sur les banques et les caisses d’épargne (« **LB** »).

2. Cortex Leman reconnaît que le secret bancaire s’applique aux informations relatives aux clients, à leur relation bancaire, à leurs avoirs, opérations, identifiants, profils et communications, lorsque les conditions légales sont réunies.

3. Cortex Leman s’interdit toute divulgation, communication, réutilisation ou exploitation non autorisée des données.

4. Les obligations de confidentialité s’appliquent :

   - pendant toute la durée du contrat ;
   - après sa résiliation ;
   - à tous les collaborateurs, dirigeants, sous-traitants et prestataires autorisés ;
   - indépendamment du lieu depuis lequel l’accès est réalisé.

5. Cortex Leman informe immédiatement UBank SA de toute demande d’accès émanant d’une autorité, sous réserve d’une interdiction légale de notification, et coopère avec UBank SA pour déterminer la réponse juridiquement appropriée.

### Article B3 — Outsourcing bancaire et FINMA

1. Les parties tiennent compte de la réglementation FINMA applicable à l’externalisation, notamment de la **FINMA Circular 2018/3 — Outsourcing – banks and insurers**, dans sa version applicable au moment du transfert.

2. UBank SA conserve la maîtrise de ses obligations réglementaires, notamment en matière :

   - d’inventaire des fonctions externalisées ;
   - d’analyse des risques ;
   - de contrôle et de surveillance du prestataire ;
   - de réversibilité ;
   - de continuité des activités ;
   - d’accès de la FINMA et de l’audit ;
   - de sous-traitance en chaîne ;
   - de localisation et d’accès aux données.

3. Cortex Leman garantit à UBank SA, à son organe de révision et à la FINMA, dans les limites légales et contractuelles applicables :

   - un droit d’audit approprié ;
   - l’accès aux informations nécessaires ;
   - la coopération lors des contrôles ;
   - la mise à disposition des rapports de sécurité pertinents ;
   - la notification des changements significatifs de service ou de sous-traitant.

4. Un **audit FINMA annuel ou un audit annuel répondant aux exigences FINMA** est prévu, selon les modalités convenues avec UBank SA. Les modalités pratiques, la portée et les coûts sont définis dans le contrat principal.

### Article B4 — AI Act et haut risque financier

1. Les parties évaluent si l’usage de Cortex Leman v5 relève de l’article 6 et de l’annexe III de l’AI Act, notamment lorsqu’il est utilisé pour l’évaluation de la solvabilité, l’accès à des services essentiels ou financiers, la détection de fraude ou une décision affectant significativement une personne.

2. La qualification « haut risque » doit être confirmée au regard de la fonction précise du système. Une utilisation dans le secteur bancaire ne rend pas automatiquement tout système d’IA haut risque.

3. Cortex Leman ne prend aucune décision automatisée relative à l’octroi, au refus, à la tarification ou à la résiliation d’un produit financier sans instruction écrite, validation réglementaire et mécanisme de supervision humaine défini par UBank SA.

4. Les parties documentent, lorsqu’applicable :

   - la finalité et les limites du système ;
   - les données d’entraînement ou de référence autorisées ;
   - les risques de biais et d’erreur ;
   - la supervision humaine ;
   - la journalisation ;
   - les procédures de contestation ;
   - la robustesse, la cybersécurité et la continuité.

### Article B5 — Mesures de sécurité renforcées

Pour le tenant UBank SA, Cortex Leman applique au minimum :

1. résidence des données en Suisse exclusivement ;
2. interdiction de transfert ou d’accès depuis un pays tiers sans autorisation écrite d’UBank SA ;
3. déploiement d’un LLM local, on-premise ou dans une infrastructure suisse exclusivement contrôlée et approuvée ;
4. interdiction d’utiliser un LLM cloud mutualisé ;
5. interdiction d’envoyer des données à un fournisseur externe d’IA générative non approuvé ;
6. isolation stricte du tenant ;
7. chiffrement des données au repos et en transit ;
8. gestion dédiée des secrets et clés ;
9. authentification multifacteur et séparation des rôles ;
10. journalisation immuable des accès et opérations sensibles ;
11. revue trimestrielle des accès privilégiés ;
12. tests annuels de sécurité, continuité et restauration ;
13. plan de réversibilité permettant la restitution des données dans un délai de [●] ;
14. notification des incidents critiques à UBank SA dans un délai maximal de [24 heures], sans préjudice du délai contractuel inférieur à 72 heures prévu à l’Article 8.

### Article B6 — Rétention

1. Les données du tenant UBank SA sont conservées pendant **2 555 jours**, soit sept ans, conformément à la politique de conservation convenue entre les parties.

2. Cette durée contractuelle ne doit pas être interprétée comme une limitation ou une modification :

   - de l’article 47 LB ;
   - des obligations de conservation applicables au titre du Code des obligations, notamment l’article 962 CO ;
   - des obligations prudentielles, fiscales, comptables, probatoires ou de lutte contre le blanchiment ;
   - d’une obligation de conservation plus longue imposée par la loi ou une autorité.

3. En cas de contradiction entre la durée de 2 555 jours et une obligation légale impérative, la durée la plus longue légalement requise s’applique, sous réserve d’une limitation d’accès et d’une suppression dès que la conservation n’est plus nécessaire.

4. Les données sont supprimées ou restituées à l’issue de la période applicable, selon les instructions d’UBank SA.

### Article B7 — Sanctions et autorités

Les parties reconnaissent que les manquements peuvent entraîner notamment :

- des mesures ou sanctions de la FINMA ;
- des conséquences civiles, administratives ou pénales liées à l’article 47 LB ;
- des sanctions du PFPDT ou de la CNIL lorsque la réglementation applicable le prévoit ;
- des mesures contractuelles, notamment suspension, résiliation, indemnisation et obligation de remédiation.

---

# Section 4 — Clause spécifique Avocat  
## Pierre Martin — Martin Avocat

### Article A1 — Parties et périmètre

- **Client / responsable du traitement :** Martin Avocat, représenté par Pierre Martin, [adresse] ;
- **Contact protection des données :** [●] ;
- **Fournisseur / sous-traitant :** Cortex Leman SARL ;
- **Tenant :** `tenant-martin-ch` ;
- **Services concernés :** [●] ;
- **Lieu de résidence des données :** Suisse exclusivement, sauf accord écrit contraire ;
- **Date d’effet :** [●].

### Article A2 — Secret professionnel de l’avocat

1. Les données peuvent relever du secret professionnel prévu par l’article 321 du Code pénal suisse (« **CP** »), ainsi que des obligations professionnelles, déontologiques et procédurales applicables aux avocats.

2. Cortex Leman garantit que les informations couvertes par le secret professionnel :

   - ne sont accessibles qu’aux personnes autorisées ;
   - ne sont pas utilisées à des fins propres ;
   - ne sont pas communiquées à des tiers non autorisés ;
   - ne sont pas intégrées à un modèle mutualisé ;
   - ne sont pas utilisées pour l’entraînement d’un système d’IA destiné à d’autres clients ;
   - font l’objet de mesures de confidentialité renforcées.

3. Toute personne ayant accès aux données doit être soumise à une obligation écrite de confidentialité adaptée au secret professionnel de l’avocat.

4. Cortex Leman informe immédiatement Martin Avocat de toute demande d’accès, perquisition, injonction ou demande d’autorité affectant les données, sauf interdiction légale. Martin Avocat conserve la maîtrise de la réponse et des éventuels droits d’opposition ou recours.

### Article A3 — Transferts internationaux

1. Tout transfert hors de Suisse est soumis à l’article 16 LPD et aux exigences applicables en matière de protection des données.

2. Lorsque le RGPD s’applique, les articles 44 à 49 RGPD sont respectés. En l’absence de décision d’adéquation applicable, les parties mettent en place les clauses contractuelles standard appropriées et les mesures supplémentaires nécessaires.

3. La Suisse bénéficie d’une décision d’adéquation de l’Union européenne, historiquement reconnue depuis 2000 et maintenue dans le cadre applicable aux transferts UE–Suisse. La portée exacte de cette décision doit être vérifiée au jour du transfert et ne dispense pas les parties de respecter les autres exigences du RGPD, de la LPD et du secret professionnel.

4. Les transferts vers des fournisseurs cloud, services d’IA générative ou sous-traitants situés hors de Suisse sont interdits sans :

   - accord écrit préalable de Martin Avocat ;
   - analyse documentée du transfert ;
   - garantie juridique appropriée ;
   - mesures supplémentaires suffisantes ;
   - vérification de la compatibilité avec l’article 321 CP et les obligations professionnelles.

### Article A4 — Mesures de sécurité renforcées

Pour le tenant `tenant-martin-ch`, Cortex Leman met en œuvre :

1. une isolation absolue du tenant ;
2. une séparation des bases, index, embeddings, journaux et sauvegardes ;
3. l’interdiction d’utiliser un LLM cloud mutualisé ;
4. l’interdiction de transmettre les données à un fournisseur externe d’IA sans autorisation ;
5. le déploiement d’un LLM local, privé ou on-premise approuvé par Martin Avocat ;
6. le chiffrement des données au repos et en transit ;
7. une gestion dédiée des clés lorsque techniquement disponible ;
8. l’authentification multifacteur ;
9. la journalisation et la revue des accès privilégiés ;
10. l’interdiction des accès administrateurs permanents ;
11. la pseudonymisation lorsque compatible avec la mission ;
12. la suppression des données temporaires, caches et fichiers de travail après exécution ;
13. des tests périodiques de restauration, d’isolement et d’intrusion ;
14. une procédure de restitution et de suppression vérifiable.

### Article A5 — Rétention

1. Les données du tenant `tenant-martin-ch` sont conservées pendant une durée maximale de **365 jours**, conformément à la politique de conservation applicable.

2. À l’issue de cette durée, Cortex Leman supprime ou anonymise les données, notamment :

   - les documents importés ;
   - les prompts et sorties ;
   - les index et embeddings ;
   - les fichiers temporaires ;
   - les copies de sauvegarde ;
   - les journaux contenant des données personnelles.

3. Une conservation plus longue n’est permise que :

   - sur instruction écrite de Martin Avocat ;
   - en présence d’une obligation légale ou professionnelle ;
   - pour préserver des preuves en cas de litige ;
   - dans le cadre d’une obligation de conservation documentée.

4. La politique applicable est la **politique `tenant-martin-ch`**.

### Article A6 — Responsabilité professionnelle et sanctions

Les parties reconnaissent qu’un manquement peut entraîner notamment :

- des conséquences pénales au titre de l’article 321 CP ;
- des mesures disciplinaires ou sanctions du barreau ou de l’autorité professionnelle compétente ;
- des sanctions ou mesures du PFPDT ou de la CNIL, lorsque leurs règles sont applicables ;
- une responsabilité civile et contractuelle ;
- la suspension immédiate des services ;
- la résiliation pour manquement grave ;
- des obligations de notification, de remédiation et d’indemnisation.

---

# Annexe 1 — Matrice des rôles

| Élément | Partie / valeur |
|---|---|
| Responsable du traitement | [●] |
| Sous-traitant | [●] |
| Exportateur | [●] |
| Importateur | [●] |
| Module SCC sélectionné | [Module 1 /
