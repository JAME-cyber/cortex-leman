# ACTION 2: Section "Auto-hébergé en Suisse" — Landing Page

## Section à intégrer dans la landing page v5

Cette section est à placer **avant la section FAQ** de `cortex-leman-v5/landing/index.html`.

---

### HTML

```html
<!-- ═══ SOUVERAINETÉ SUISSE ═══ -->
<section id="souverainete" class="sec">
    <div class="si">
        <div class="sec-header fi">
            <div class="left">
                <span class="sl" style="background:rgba(234,179,8,0.12);color:#eab308">🇨🇭 Souveraineté</span>
            </div>
            <div class="right">
                <h2 class="sh">Vos données restent<br>chez vous. Point.</h2>
                <p class="sd">
                    Pas de cloud US. Pas de transfert hors frontières. Cortex Leman est 
                    auto-hébergé sur votre infrastructure — en Suisse ou en France.
                </p>
            </div>
        </div>
        <div class="cards3">
            <div class="card3 fi">
                <div class="card3-top">
                    <div class="card3-icon" style="background:var(--amber-s)">🔒</div>
                    <span class="card3-num">01.</span>
                </div>
                <div>
                    <h3>100% On-Premise</h3>
                    <p>n8n, LLM, journal WORM — tout tourne sur vos serveurs. Zéro appel sortant en mode Haute Protection. Vos données ne quittent jamais votre réseau.</p>
                    <span class="tag" style="background:rgba(234,179,8,0.12);color:#eab308">Zero egress</span>
                </div>
            </div>
            <div class="card3 fi">
                <div class="card3-top">
                    <div class="card3-icon" style="background:var(--amber-s)">🇨🇭</div>
                    <span class="card3-num">02.</span>
                </div>
                <div>
                    <h3>Conforme LPD + RGPD + AI Act</h3>
                    <p>Triple conformité par design. Data residency en Suisse = conforme LPerD. Pas de Privacy Shield précaire, pas de Standard Contractual Clauses. C'est local ou rien.</p>
                    <span class="tag" style="background:rgba(234,179,8,0.12);color:#eab308">FR-CH natif</span>
                </div>
            </div>
            <div class="card3 fi">
                <div class="card3-top">
                    <div class="card3-icon" style="background:var(--amber-s)">🛡️</div>
                    <span class="card3-num">03.</span>
                </div>
                <div>
                    <h3>Secret professionnel garanti</h3>
                    <p>Avocats (Art. 321 CP), banquiers (Art. 47 LB), médecins (LPM) — le mode Haute Protection bloque tout envoi externe. Le secret n'est pas négociable.</p>
                    <span class="tag" style="background:rgba(234,179,8,0.12);color:#eab308">Secret pro</span>
                </div>
            </div>
        </div>

        <!-- Comparison banner -->
        <div class="compare-banner fi" style="margin-top:48px;background:var(--card);border:1px solid var(--bdr);border-radius:12px;padding:28px 32px;display:flex;align-items:center;gap:32px;flex-wrap:wrap">
            <div style="flex:1;min-width:240px">
                <h3 style="font-size:18px;margin-bottom:4px">Cloud US vs Auto-hébergé Suisse</h3>
                <p style="color:var(--t2);font-size:14px">Ce que votre DPO veut entendre</p>
            </div>
            <div style="flex:2;min-width:300px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
                <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:8px;padding:14px">
                    <div style="font-size:12px;font-weight:600;color:#ef4444;margin-bottom:6px">❌ Cloud US (Make, Zapier, OpenAI)</div>
                    <ul style="font-size:13px;color:var(--t2);list-style:none;padding:0;margin:0;line-height:1.8">
                        <li>• Données hébergées aux États-Unis</li>
                        <li>• CLOUD Act = accès gouvernemental US</li>
                        <li>• RGPD: transferts hors UE risqués</li>
                        <li>• LPD: non conforme pour données suisses</li>
                        <li>• Secret pro: impossible à garantir</li>
                    </ul>
                </div>
                <div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);border-radius:8px;padding:14px">
                    <div style="font-size:12px;font-weight:600;color:#10b981;margin-bottom:6px">✅ Cortex Leman (Auto-hébergé CH)</div>
                    <ul style="font-size:13px;color:var(--t2);list-style:none;padding:0;margin:0;line-height:1.8">
                        <li>• Données sur votre infrastructure</li>
                        <li>• Zéro accès tiers, zéro CLOUD Act</li>
                        <li>• RGPD: data residency EU/CH</li>
                        <li>• LPD: conforme nativement</li>
                        <li>• Secret pro: garanti par architecture</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</section>
```

### Instructions d'intégration

Insérer ce bloc dans `/home/tars/cortex-leman-v5/landing/index.html` avant la section FAQ.

Le style réutilise les variables CSS existantes (`--amber-s`, `--card`, `--bdr`, etc.) et les classes `.cards3`, `.card3`, `.sec`, `.si`, `.sec-header`, `.sh`, `.sd` déjà définies.

---

## Supports de vente à mettre à jour

### 1. Fiche produit (`cortex-leman/marketing-hybride/01-templates-marketing/03-fiche-cortex-leman.md`)

Ajouter une section **"🇨🇭 Souveraineté des données"** en position #1 des avantages:

> **🇨🇭 Auto-hébergé en Suisse — Zéro cloud US**
> Vos données restent sur votre infrastructure. Pas de CLOUD Act, pas de Privacy Shield précaire.
> Conforme LPD suisse + RGPD + AI Act par design.
> Mode Haute Protection: zero appel réseau externe — secret professionnel garanti.

### 2. Deck de vente (`cortex-leman/marketing-hybride/03-deck-vente/`)

Ajouter un slide dédié **"Souveraineté Suisse = votre avantage"** avec le comparatif Cloud US vs Auto-hébergé CH.

### 3. Templates LinkedIn

Ajouter un post dédié "Souveraineté" au calendrier éditorial.

### 4. Landing page v1 (`cortex-leman-landing-page/index.html`)

Ajouter une section souveraineté similaire avec le comparatif.
