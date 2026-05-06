"""
HyperFrame Templates — Excellence by Design
Templates HTML/GSAP broadcast-quality pour SocialPulse.

Effets inclus:
- Karaoke captions (mot par mot, coloré)
- Keyword cards flottantes  
- Fenêtres macOS chrome
- Transitions crossfade entre scènes
- Dead zone Instagram (zone safe)
- Progress bar avec segments
- Counter animé (score)
- Screenshot scroll simulé
"""
import uuid


# ═══════════════════════════════════════════════════
# Palette & Constantes
# ═══════════════════════════════════════════════════

CORTEX = {
    "primary": "#0d9488",
    "accent": "#14b8a6",
    "dark": "#0a0a0a",
    "navy": "#0f172a",
    "text": "#f1f5f9",
    "text2": "#94a3b8",
    "danger": "#ef4444",
    "success": "#22c55e",
    "warning": "#f59e0b",
}

ICONS = {
    "comptable": "📊", "avocat": "⚖️", "sante": "🏥",
    "banque": "🏦", "startup": "🚀", "rh": "👥",
}

DEAD_ZONE = """
  /* Dead zone Instagram Reels: top 120px + bottom 180px + right 60px */
  .safe-zone {
    position: absolute;
    top: 120px; left: 40px; right: 80px; bottom: 200px;
  }
"""

GSAP_CDN = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"

def _comp_id():
    return f"sp-{uuid.uuid4().hex[:8]}"


# ═══════════════════════════════════════════════════
# SCENE 1: Hook — "ALERTE CONFORMITÉ IA"  
# SCENE 2: Company card + keyword cards
# SCENE 3: Risk reveal + Karaoke caption
# SCENE 4: CTA
# Transitions: crossfade 0.4s entre chaque scène
# ═══════════════════════════════════════════════════

def lead_card_html(args: dict) -> str:
    company = args.get("company_name", "Entreprise")
    vertical = args.get("vertical", "comptable")
    risk = args.get("risk_type", "Risque IA détecté")
    duration = args.get("duration", 12)
    fmt = args.get("format", "9:16")
    brand = args.get("brand_color", CORTEX["primary"])
    icon = ICONS.get(vertical, "⚠️")

    w, h = ("1080", "1920") if fmt == "9:16" else ("1920", "1080")

    # Scènes timing
    s1_end = 2.5      # Hook visible
    s2_start = 2.0    # Company entre
    s2_end = 6.0      # Company + keywords
    s3_start = 5.5    # Risk entre
    s3_end = duration - 2.5  # Risk + karaoke
    s4_start = duration - 3.0  # CTA

    # Keyword cards par verticale
    keywords = {
        "comptable": ["RGPD", "DPIA", "Consentement", "IA Fiscal"],
        "avocat": ["Secret Pro", "AI Act", "Consentement", "Éthique"],
        "sante": ["HDS", "DICOM", "Consentement", "DPI"],
        "banque": ["Bâle III", "KYC IA", "Scoring", "DORA"],
        "startup": ["RGPD", "AI Act", "Pitch Deck", "Data Min"],
        "rh": ["CV IA", "Biais Algo", "Consentement", "CSE"],
    }
    kw = keywords.get(vertical, ["RGPD", "IA", "Conformité", "Audit"])

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<script src="{GSAP_CDN}"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {w}px; height: {h}px; overflow: hidden; background: {CORTEX["dark"]};
    font-family: 'Inter', sans-serif; color: {CORTEX["text"]}; }}

  /* ── Progress bar ── */
  .progress {{ position: absolute; top: 0; left: 0; right: 0; height: 4px; z-index: 100; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, {brand}, {CORTEX["accent"]}); }}
  .progress-markers {{ position: absolute; top: 4px; left: 0; right: 0; height: 2px; display: flex; }}
  .progress-mark {{ flex: 1; background: rgba(255,255,255,0.06); }}
  .progress-mark.active {{ background: rgba(13,148,136,0.3); }}

  /* ── Scenes ── */
  .scene {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
  #scene1 {{ z-index: 1; }}
  #scene2 {{ z-index: 2; opacity: 0; }}
  #scene3 {{ z-index: 3; opacity: 0; }}
  #scene4 {{ z-index: 4; opacity: 0; }}

  /* ── Scene 1: Hook ── */
  .hook-container {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  .hook-badge {{ font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: 4px;
    color: {CORTEX["danger"]}; background: rgba(239,68,68,0.12); padding: 10px 24px;
    border-radius: 8px; border: 1px solid rgba(239,68,68,0.2); }}
  .hook-title {{ font-size: 52px; font-weight: 900; letter-spacing: -1px; text-align: center;
    margin-top: 32px; line-height: 1.1; }}
  .hook-title .accent {{ color: {brand}; }}
  .hook-subtitle {{ font-size: 16px; color: {CORTEX["text2"]}; margin-top: 20px;
    font-weight: 500; letter-spacing: 1px; }}

  /* ── Scene 2: Company + Keywords ── */
  .company-section {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    padding: 40px; }}
  .company-card {{ background: rgba(15,23,42,0.85); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 36px 40px; backdrop-filter: blur(10px); }}
  .company-top {{ display: flex; align-items: center; gap: 16px; }}
  .company-icon {{ font-size: 44px; }}
  .company-info {{ flex: 1; }}
  .company-name {{ font-size: 30px; font-weight: 800; letter-spacing: -0.5px; }}
  .company-vertical {{ font-size: 12px; color: {brand}; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; margin-top: 4px; }}
  .company-divider {{ height: 1px; background: rgba(255,255,255,0.06); margin: 28px 0; }}

  /* macOS window chrome */
  .mac-window {{ background: rgba(15,23,42,0.9); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px; padding: 16px 20px; margin-top: 24px; }}
  .mac-dots {{ display: flex; gap: 6px; margin-bottom: 12px; }}
  .mac-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
  .mac-dot.red {{ background: #ff5f57; }}
  .mac-dot.yellow {{ background: #febc2e; }}
  .mac-dot.green {{ background: #28c840; }}
  .mac-content {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; color: {CORTEX["text2"]};
    line-height: 1.8; }}
  .mac-content .highlight {{ color: {brand}; font-weight: 700; }}
  .mac-content .danger {{ color: {CORTEX["danger"]}; }}

  /* Keyword cards */
  .keywords {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }}
  .keyword {{ font-size: 13px; font-weight: 700; padding: 8px 16px; border-radius: 10px;
    background: rgba(13,148,136,0.1); color: {brand}; border: 1px solid rgba(13,148,136,0.2); }}

  /* ── Scene 3: Risk + Karaoke ── */
  .risk-section {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; }}
  .risk-card {{ background: linear-gradient(135deg, rgba(13,148,136,0.15), rgba(20,184,166,0.05));
    border: 1px solid rgba(13,148,136,0.25); border-radius: 20px; padding: 40px;
    backdrop-filter: blur(10px); }}
  .risk-badge {{ font-size: 11px; font-weight: 800; color: {CORTEX["danger"]};
    text-transform: uppercase; letter-spacing: 2px; margin-bottom: 16px; }}
  .risk-title {{ font-size: 34px; font-weight: 800; line-height: 1.25; letter-spacing: -0.3px; }}

  /* Karaoke caption */
  .karaoke {{ margin-top: 32px; display: flex; flex-wrap: wrap; gap: 0; justify-content: center; }}
  .karaoke-word {{ font-size: 22px; font-weight: 700; padding: 4px 6px; opacity: 0.2;
    transition: none; }}
  .karaoke-word.active {{ opacity: 1; color: {brand}; transform: scale(1.08); }}
  .karaoke-word.past {{ opacity: 0.6; color: {CORTEX["text"]}; transform: scale(1); }}

  /* ── Scene 4: CTA ── */
  .cta-section {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  .cta-logo {{ font-size: 48px; font-weight: 900; color: {brand}; }}
  .cta-tagline {{ font-size: 20px; color: {CORTEX["text2"]}; margin-top: 16px; text-align: center; }}
  .cta-btn {{ margin-top: 32px; font-size: 18px; font-weight: 700; color: {CORTEX["dark"]};
    background: {brand}; padding: 18px 48px; border-radius: 14px; }}
  .cta-url {{ margin-top: 16px; font-size: 13px; color: {CORTEX["text2"]}; font-weight: 500; }}
</style>
</head>
<body>
  <div class="progress"><div class="progress-fill" id="progressFill"></div></div>

  <!-- SCENE 1: Hook -->
  <div class="scene" id="scene1">
    <div class="hook-container">
      <div class="hook-badge" id="hookBadge">⚠️ ALERTE CONFORMITÉ</div>
      <div class="hook-title" id="hookTitle">Votre IA est-elle <span class="accent">en règle</span> ?</div>
      <div class="hook-subtitle" id="hookSub">Analyse automatisée · RGPD · AI Act · Secret Professionnel</div>
    </div>
  </div>

  <!-- SCENE 2: Company + Keywords -->
  <div class="scene" id="scene2">
    <div class="company-section">
      <div class="company-card" id="companyCard">
        <div class="company-top">
          <div class="company-icon">{icon}</div>
          <div class="company-info">
            <div class="company-name">{company}</div>
            <div class="company-vertical">{vertical.upper()}</div>
          </div>
        </div>
        <div class="company-divider"></div>
        <div class="mac-window" id="macWindow">
          <div class="mac-dots"><div class="mac-dot red"></div><div class="mac-dot yellow"></div><div class="mac-dot green"></div></div>
          <div class="mac-content">
            > cortex audit --vertical <span class="highlight">{vertical}</span><br>
            > scanning {company}...<br>
            > <span class="danger">⚠ RISQUE DÉTECTÉ</span>: {risk[:40]}...<br>
            > score conformité: <span class="danger">72/100</span>
          </div>
        </div>
        <div class="keywords" id="keywords">
          {"".join(f'<div class="keyword" id="kw{i}">{k}</div>' for i, k in enumerate(kw))}
        </div>
      </div>
    </div>
  </div>

  <!-- SCENE 3: Risk + Karaoke -->
  <div class="scene" id="scene3">
    <div class="risk-section">
      <div class="risk-card" id="riskCard">
        <div class="risk-badge" id="riskBadge">🔍 Risque détecté par Cortex Leman</div>
        <div class="risk-title" id="riskTitle">{risk}</div>
        <div class="karaoke" id="karaoke">
          {"".join(f'<span class="karaoke-word" id="kw_k{i}">{w}</span>' for i, w in enumerate(
            ["Conformité", "RGPD", "et", "AI", "Act", "—", "audit", "gratuit", "par", "Cortex", "Léman"]
          ))}
        </div>
      </div>
    </div>
  </div>

  <!-- SCENE 4: CTA -->
  <div class="scene" id="scene4">
    <div class="cta-section">
      <div class="cta-logo" id="ctaLogo">🌊</div>
      <div style="font-size:28px;font-weight:800;margin-top:12px" id="ctaTitle">Cortex Leman</div>
      <div class="cta-tagline" id="ctaTag">Conformité IA par design pour professions régulées</div>
      <div class="cta-btn" id="ctaBtn">Audit gratuit →</div>
      <div class="cta-url" id="ctaUrl">cortex-leman.com</div>
    </div>
  </div>

  <script>
    var tl = gsap.timeline({{ paused: false }});
    window.__tl = tl;
    var dur = {duration};
    var t1 = {s1_end}, t2 = {s2_end}, t3 = {s3_end};
    var tf = 0.4; // transition fade duration

    // ── Progress bar ──
    tl.to("#progressFill", {{ width: "100%", duration: dur, ease: "none" }}, 0);

    // ══════════════════════════════
    // SCENE 1: Hook (0 → t1)
    // ══════════════════════════════
    tl.fromTo("#hookBadge", {{ scale: 0.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.7)" }}, 0.2);
    tl.fromTo("#hookTitle", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.7, ease: "power3.out" }}, 0.5);
    tl.fromTo("#hookSub", {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power2.out" }}, 0.9);
    // Crossfade out scene1
    tl.to("#scene1", {{ opacity: 0, duration: tf, ease: "power2.inOut" }}, t1 - tf);

    // ══════════════════════════════
    // SCENE 2: Company + Keywords (t1 → t2)
    // ══════════════════════════════
    tl.set("#scene2", {{ opacity: 1 }}, t1 - tf);
    tl.fromTo("#companyCard", {{ y: 60, opacity: 0, scale: 0.95 }}, {{ y: 0, opacity: 1, scale: 1, duration: 0.8, ease: "power3.out" }}, t1);
    tl.fromTo("#macWindow", {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power2.out" }}, t1 + 0.6);
    // Keywords stagger
    tl.fromTo(".keyword", {{ y: 15, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3, stagger: 0.1, ease: "power2.out" }}, t1 + 1.0);
    // Crossfade out scene2
    tl.to("#scene2", {{ opacity: 0, duration: tf, ease: "power2.inOut" }}, t2 - tf);

    // ══════════════════════════════
    // SCENE 3: Risk + Karaoke (t2 → t3)
    // ══════════════════════════════
    tl.set("#scene3", {{ opacity: 1 }}, t2 - tf);
    tl.fromTo("#riskCard", {{ scale: 0.9, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.7, ease: "back.out(1.4)" }}, t2);
    // Karaoke: word-by-word activation
    var karaokeStart = t2 + 0.8;
    var kwTotal = 11; // nombre de mots karaoke
    var kwDelay = 0.25;
    for (var i = 0; i < kwTotal; i++) {{
      tl.set("#kw_k" + i, {{ className: "karaoke-word active" }}, karaokeStart + i * kwDelay);
      tl.set("#kw_k" + i, {{ className: "karaoke-word past" }}, karaokeStart + i * kwDelay + kwDelay);
    }}
    // Risk pulse
    tl.to("#riskCard", {{ scale: 1.02, duration: 0.4, yoyo: true, repeat: 1, ease: "power2.inOut" }}, t2 + 0.5);
    // Crossfade out
    tl.to("#scene3", {{ opacity: 0, duration: tf, ease: "power2.inOut" }}, t3 - tf);

    // ══════════════════════════════
    // SCENE 4: CTA (t3 → end)
    // ══════════════════════════════
    tl.set("#scene4", {{ opacity: 1 }}, t3 - tf);
    tl.fromTo("#ctaLogo", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.6, ease: "back.out(2)" }}, {s4_start});
    tl.fromTo("#ctaTitle", {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, {s4_start} + 0.2);
    tl.fromTo("#ctaTag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {s4_start} + 0.5);
    tl.fromTo("#ctaBtn", {{ scale: 0.9, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.5)" }}, {s4_start} + 0.8);
    tl.fromTo("#ctaUrl", {{ y: 10, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.3 }}, {s4_start} + 1.1);
  </script>
</body>
</html>'''


# ═══════════════════════════════════════════════════
# LISTICLE — N risques avec counter, 
# keyword cards, scènes chainées
# ═══════════════════════════════════════════════════

def listicle_html(args: dict) -> str:
    items = args.get("items", ["Risque #1", "Risque #2", "Risque #3"])
    truncated = items[:5]
    vertical = args.get("vertical", "comptable")
    duration = args.get("duration", 15)
    fmt = args.get("format", "9:16")
    brand = args.get("brand_color", CORTEX["primary"])
    icon = ICONS.get(vertical, "⚠️")

    w, h = ("1080", "1920") if fmt == "9:16" else ("1920", "1080")

    # Timing
    scene_dur = (duration - 3) / len(truncated)  # temps par item, 3s pour CTA
    cta_start = duration - 3.0

    # Generate scenes HTML
    scenes_html = ""
    scenes_css = ""
    scenes_anim = ""
    
    for i, item in enumerate(truncated):
        s_start = i * scene_dur
        s_end = (i + 1) * scene_dur
        
        scenes_css += f'''
    #scene_item{i} {{ z-index: {i + 2}; opacity: 0; }}
    .item-outer{i} {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
      display: flex; flex-direction: column; justify-content: center; }}
    .item-card{i} {{ background: rgba(15,23,42,0.85); border: 1px solid rgba(255,255,255,0.08);
      border-radius: 20px; padding: 40px; backdrop-filter: blur(10px); }}
    .item-num{i} {{ font-size: 14px; font-weight: 800; color: {brand};
      background: rgba(13,148,136,0.15); padding: 8px 16px; border-radius: 10px;
      display: inline-block; margin-bottom: 20px; }}
    .item-text{i} {{ font-size: 26px; font-weight: 700; line-height: 1.3; }}
    .item-icon{i} {{ font-size: 32px; margin-bottom: 16px; }}
'''
        scenes_html += f'''
    <div class="scene" id="scene_item{i}">
      <div class="item-outer{i}">
        <div class="item-card{i}">
          <div class="item-icon{i}" id="itemIcon{i}">{icon}</div>
          <div class="item-num{i}" id="itemNum{i}">{i+1} / {len(truncated)}</div>
          <div class="item-text{i}" id="itemText{i}">{item}</div>
        </div>
      </div>
    </div>'''
        
        # Animation with crossfade transitions
        scenes_anim += f'''
    // ── Item {i+1} ({s_start:.1f}s → {s_end:.1f}s) ──
    tl.set("#scene_item{i}", {{ opacity: 1 }}, {s_start});
    tl.fromTo("#itemIcon{i}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {s_start} + 0.1);
    tl.fromTo("#itemNum{i}", {{ x: -30, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.4, ease: "power3.out" }}, {s_start} + 0.3);
    tl.fromTo("#itemText{i}", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, {s_start} + 0.5);
    tl.to("#scene_item{i}", {{ opacity: 0, duration: 0.35, ease: "power2.inOut" }}, {s_end} - 0.35);
'''

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<script src="{GSAP_CDN}"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {w}px; height: {h}px; overflow: hidden; background: {CORTEX["dark"]};
    font-family: 'Inter', sans-serif; color: {CORTEX["text"]}; }}

  .progress {{ position: absolute; top: 0; left: 0; right: 0; height: 4px; z-index: 100; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, {brand}, {CORTEX["accent"]}); }}

  .scene {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
  #scene_header {{ z-index: 1; }}
  #scene_cta {{ z-index: {len(truncated) + 2}; opacity: 0; }}
  {scenes_css}

  /* CTA */
  .cta-section {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  .cta-logo {{ font-size: 48px; font-weight: 900; color: {brand}; }}
  .cta-btn {{ margin-top: 24px; font-size: 17px; font-weight: 700; color: {CORTEX["dark"]};
    background: {brand}; padding: 16px 40px; border-radius: 14px; }}
  .cta-url {{ margin-top: 12px; font-size: 13px; color: {CORTEX["text2"]}; }}

  /* Header scene */
  .header-section {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; }}
  .header-icon {{ font-size: 40px; }}
  .header-title {{ font-size: 36px; font-weight: 900; margin-top: 16px; letter-spacing: -0.5px; }}
  .header-sub {{ font-size: 14px; color: {CORTEX["text2"]}; margin-top: 8px; font-weight: 500; }}
</style>
</head>
<body>
  <div class="progress"><div class="progress-fill" id="progressFill"></div></div>

  <!-- Header scene -->
  <div class="scene" id="scene_header">
    <div class="header-section">
      <div class="header-icon" id="hIcon">{icon}</div>
      <div class="header-title" id="hTitle">{len(truncated)} risques IA pour {vertical}</div>
      <div class="header-sub" id="hSub">Conformité RGPD / AI Act — Analyse Cortex Leman</div>
    </div>
  </div>

  {scenes_html}

  <!-- CTA scene -->
  <div class="scene" id="scene_cta">
    <div class="cta-section">
      <div class="cta-logo" id="ctaLogo">🌊</div>
      <div style="font-size:24px;font-weight:800;margin-top:8px" id="ctaTitle">Cortex Leman</div>
      <div class="cta-btn" id="ctaBtn">Audit gratuit →</div>
      <div class="cta-url" id="ctaUrl">cortex-leman.com</div>
    </div>
  </div>

  <script>
    var tl = gsap.timeline({{ paused: false }});
    window.__tl = tl;
    var dur = {duration};

    // Progress
    tl.to("#progressFill", {{ width: "100%", duration: dur, ease: "none" }}, 0);

    // Header (0 → 2s)
    tl.fromTo("#hIcon", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2)" }}, 0.2);
    tl.fromTo("#hTitle", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }}, 0.4);
    tl.fromTo("#hSub", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.8);
    tl.to("#scene_header", {{ opacity: 0, duration: 0.35, ease: "power2.inOut" }}, 1.8);

    {scenes_anim}

    // CTA
    tl.set("#scene_cta", {{ opacity: 1 }}, {cta_start});
    tl.fromTo("#ctaLogo", {{ scale: 0 }}, {{ scale: 1, duration: 0.5, ease: "back.out(2)" }}, {cta_start} + 0.1);
    tl.fromTo("#ctaTitle", {{ y: 15, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4 }}, {cta_start} + 0.3);
    tl.fromTo("#ctaBtn", {{ scale: 0.9, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.5)" }}, {cta_start} + 0.6);
    tl.fromTo("#ctaUrl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {cta_start} + 0.9);
  </script>
</body>
</html>'''


# ═══════════════════════════════════════════════════
# COMPLIANCE REPORT — Score animé, gauge, 
# findings, Karaoke, keyword cards
# ═══════════════════════════════════════════════════

def compliance_report_html(args: dict) -> str:
    company = args.get("company_name", "Entreprise")
    vertical = args.get("vertical", "comptable")
    duration = args.get("duration", 14)
    fmt = args.get("format", "9:16")
    brand = args.get("brand_color", CORTEX["primary"])
    icon = ICONS.get(vertical, "⚠️")
    score = 72

    w, h = ("1080", "1920") if fmt == "9:16" else ("1920", "1080")

    # Timing
    s1_end = 3.0    # Logo + company
    s2_end = 7.0    # Score gauge
    s3_end = duration - 3.0  # Findings
    s4_start = duration - 3.0  # CTA

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<script src="{GSAP_CDN}"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {w}px; height: {h}px; overflow: hidden; background: {CORTEX["dark"]};
    font-family: 'Inter', sans-serif; color: {CORTEX["text"]}; }}

  .progress {{ position: absolute; top: 0; left: 0; right: 0; height: 4px; z-index: 100; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, {brand}, {CORTEX["accent"]}); }}

  .scene {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
  #scene1 {{ z-index: 1; }}
  #scene2 {{ z-index: 2; opacity: 0; }}
  #scene3 {{ z-index: 3; opacity: 0; }}
  #scene4 {{ z-index: 4; opacity: 0; }}

  /* Scene 1: Logo + Company */
  .s1-content {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; padding: 40px; }}
  .s1-logo {{ font-size: 24px; font-weight: 900; color: {brand}; }}
  .s1-date {{ font-size: 13px; color: {CORTEX["text2"]}; margin-top: 4px; }}
  .s1-divider {{ height: 1px; background: rgba(255,255,255,0.06); margin: 32px 0; }}
  .s1-label {{ font-size: 11px; color: {CORTEX["text2"]}; text-transform: uppercase; letter-spacing: 2px; }}
  .s1-company {{ font-size: 36px; font-weight: 800; margin-top: 8px; letter-spacing: -0.5px; }}
  .s1-badge {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 12px;
    font-size: 12px; font-weight: 700; color: {brand}; background: rgba(13,148,136,0.1);
    padding: 6px 14px; border-radius: 8px; }}
  .s1-mac {{ background: rgba(15,23,42,0.9); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 16px 20px; margin-top: 24px; }}
  .s1-mac-dots {{ display: flex; gap: 6px; margin-bottom: 10px; }}
  .s1-mac-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
  .s1-mac-content {{ font-family: 'JetBrains Mono', monospace; font-size: 12px;
    color: {CORTEX["text2"]}; line-height: 1.7; }}
  .s1-mac-content .hl {{ color: {brand}; font-weight: 700; }}

  /* Scene 2: Score gauge */
  .s2-content {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .s2-label {{ font-size: 12px; color: {CORTEX["text2"]}; text-transform: uppercase; letter-spacing: 2px; }}
  .s2-score {{ font-size: 120px; font-weight: 900; color: {brand}; margin-top: 16px;
    font-variant-numeric: tabular-nums; }}
  .s2-max {{ font-size: 24px; color: {CORTEX["text2"]}; font-weight: 400; }}
  .s2-bar-bg {{ width: 70%; height: 10px; background: rgba(255,255,255,0.06);
    border-radius: 5px; margin-top: 28px; overflow: hidden; }}
  .s2-bar {{ height: 100%; width: 0%; border-radius: 5px;
    background: linear-gradient(90deg, {CORTEX["danger"]}, {CORTEX["warning"]}, {brand}); }}
  .s2-status {{ font-size: 14px; font-weight: 700; margin-top: 16px;
    color: {CORTEX["warning"]}; background: rgba(245,158,11,0.1);
    padding: 8px 20px; border-radius: 8px; }}
  .s2-keywords {{ display: flex; gap: 10px; margin-top: 28px; }}
  .s2-kw {{ font-size: 12px; font-weight: 700; padding: 6px 14px; border-radius: 8px;
    background: rgba(239,68,68,0.1); color: {CORTEX["danger"]}; border: 1px solid rgba(239,68,68,0.15); }}

  /* Scene 3: Findings */
  .s3-content {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; justify-content: center; padding: 20px 0; }}
  .s3-title {{ font-size: 18px; font-weight: 700; margin-bottom: 24px; }}
  .s3-finding {{ background: rgba(239,68,68,0.08); border-left: 3px solid {CORTEX["danger"]};
    padding: 16px 20px; margin-bottom: 14px; border-radius: 0 12px 12px 0; }}
  .s3-finding-icon {{ font-size: 14px; margin-right: 8px; }}
  .s3-finding-text {{ font-size: 15px; font-weight: 600; line-height: 1.4; }}
  .s3-severity {{ display: inline-block; font-size: 10px; font-weight: 800; padding: 3px 8px;
    border-radius: 4px; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; }}
  .s3-severity.high {{ background: rgba(239,68,68,0.15); color: {CORTEX["danger"]}; }}
  .s3-severity.medium {{ background: rgba(245,158,11,0.15); color: {CORTEX["warning"]}; }}

  /* Scene 4: CTA */
  .s4-content {{ position: absolute; top: 120px; left: 40px; right: 80px; bottom: 200px;
    display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .s4-logo {{ font-size: 56px; }}
  .s4-title {{ font-size: 28px; font-weight: 800; margin-top: 12px; }}
  .s4-tag {{ font-size: 16px; color: {CORTEX["text2"]}; margin-top: 12px; text-align: center; }}
  .s4-btn {{ margin-top: 28px; font-size: 17px; font-weight: 700; color: {CORTEX["dark"]};
    background: {brand}; padding: 16px 40px; border-radius: 14px; }}
  .s4-url {{ margin-top: 12px; font-size: 13px; color: {CORTEX["text2"]}; }}
</style>
</head>
<body>
  <div class="progress"><div class="progress-fill" id="pFill"></div></div>

  <div class="scene" id="scene1">
    <div class="s1-content">
      <div class="s1-logo" id="s1Logo">🌊 CORTEX LEMAN</div>
      <div class="s1-date" id="s1Date">Rapport Conformité IA — 2026</div>
      <div class="s1-divider"></div>
      <div class="s1-label">Rapport pour</div>
      <div class="s1-company" id="s1Company">{company}</div>
      <div class="s1-badge" id="s1Badge">{icon} {vertical.upper()}</div>
      <div class="s1-mac" id="s1Mac">
        <div class="s1-mac-dots"><div class="s1-mac-dot" style="background:#ff5f57"></div><div class="s1-mac-dot" style="background:#febc2e"></div><div class="s1-mac-dot" style="background:#28c840"></div></div>
        <div class="s1-mac-content">
          > <span class="hl">cortex audit</span> --vertical {vertical} --client "{company}"<br>
          > analysing... <span class="hl">{score} risques potentiels</span> détectés<br>
          > generating DPIA / AI Act checklist...
        </div>
      </div>
    </div>
  </div>

  <div class="scene" id="scene2">
    <div class="s2-content">
      <div class="s2-label" id="s2Label">Score de conformité IA</div>
      <div><span class="s2-score" id="s2Score">0</span><span class="s2-max"> /100</span></div>
      <div class="s2-bar-bg"><div class="s2-bar" id="s2Bar"></div></div>
      <div class="s2-status" id="s2Status">⚠️ Conformité partielle — Action requise</div>
      <div class="s2-keywords" id="s2Kw">
        <div class="s2-kw" id="s2Kw0">DPIA</div>
        <div class="s2-kw" id="s2Kw1">Consentement</div>
        <div class="s2-kw" id="s2Kw2">Transfert</div>
      </div>
    </div>
  </div>

  <div class="scene" id="scene3">
    <div class="s3-content">
      <div class="s3-title" id="s3Title">🔍 Constats principaux</div>
      <div class="s3-finding" id="s3f0">
        <div class="s3-finding-text">Chatbot sans consentement RGPD</div>
        <div class="s3-severity high">CRITIQUE</div>
      </div>
      <div class="s3-finding" id="s3f1">
        <div class="s3-finding-text">Pas de DPIA pour le modèle de scoring</div>
        <div class="s3-severity high">CRITIQUE</div>
      </div>
      <div class="s3-finding" id="s3f2">
        <div class="s3-finding-text">Données transférées hors UE</div>
        <div class="s3-severity medium">MODÉRÉ</div>
      </div>
    </div>
  </div>

  <div class="scene" id="scene4">
    <div class="s4-content">
      <div class="s4-logo" id="s4Logo">🌊</div>
      <div class="s4-title" id="s4Title">Cortex Leman</div>
      <div class="s4-tag" id="s4Tag">Conformité IA par design<br>pour professions régulées</div>
      <div class="s4-btn" id="s4Btn">📋 Rapport complet →</div>
      <div class="s4-url" id="s4Url">cortex-leman.com</div>
    </div>
  </div>

  <script>
    var tl = gsap.timeline({{ paused: false }});
    window.__tl = tl;
    var dur = {duration};
    var tf = 0.4;
    var t1 = {s1_end}, t2 = {s2_end}, t3 = {s3_end};
    var score = {score};

    // Progress
    tl.to("#pFill", {{ width: "100%", duration: dur, ease: "none" }}, 0);

    // ═══ Scene 1: Logo + Company ═══
    tl.fromTo("#s1Logo", {{ x: -30, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5 }}, 0.3);
    tl.fromTo("#s1Date", {{ x: 30, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5 }}, 0.5);
    tl.fromTo("#s1Company", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }}, 0.8);
    tl.fromTo("#s1Badge", {{ scale: 0.8, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.5)" }}, 1.2);
    tl.fromTo("#s1Mac", {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5 }}, 1.5);
    tl.to("#scene1", {{ opacity: 0, duration: tf }}, t1 - tf);

    // ═══ Scene 2: Score gauge ═══
    tl.set("#scene2", {{ opacity: 1 }}, t1 - tf);
    tl.fromTo("#s2Label", {{ y: -20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4 }}, t1);
    tl.fromTo("#s2Score", {{ scale: 0.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.6, ease: "back.out(1.5)" }}, t1 + 0.2);
    // Score counter
    tl.to("#s2Score", {{ innerText: score, duration: 1.8, snap: {{ innerText: 1 }}, ease: "power2.out" }}, t1 + 0.3);
    tl.to("#s2Bar", {{ width: score + "%", duration: 1.8, ease: "power2.out" }}, t1 + 0.3);
    tl.fromTo("#s2Status", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, t1 + 2.0);
    tl.fromTo("#s2Kw0", {{ x: -20, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3 }}, t1 + 2.3);
    tl.fromTo("#s2Kw1", {{ x: -20, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3 }}, t1 + 2.5);
    tl.fromTo("#s2Kw2", {{ x: -20, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.3 }}, t1 + 2.7);
    tl.to("#scene2", {{ opacity: 0, duration: tf }}, t2 - tf);

    // ═══ Scene 3: Findings ═══
    tl.set("#scene3", {{ opacity: 1 }}, t2 - tf);
    tl.fromTo("#s3Title", {{ y: -20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4 }}, t2);
    tl.fromTo("#s3f0", {{ x: -40, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, t2 + 0.3);
    tl.fromTo("#s3f1", {{ x: -40, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, t2 + 0.7);
    tl.fromTo("#s3f2", {{ x: -40, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: "power3.out" }}, t2 + 1.1);
    tl.to("#scene3", {{ opacity: 0, duration: tf }}, t3 - tf);

    // ═══ Scene 4: CTA ═══
    tl.set("#scene4", {{ opacity: 1 }}, t3 - tf);
    tl.fromTo("#s4Logo", {{ scale: 0 }}, {{ scale: 1, duration: 0.5, ease: "back.out(2)" }}, {s4_start});
    tl.fromTo("#s4Title", {{ y: 20, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.4 }}, {s4_start} + 0.2);
    tl.fromTo("#s4Tag", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {s4_start} + 0.5);
    tl.fromTo("#s4Btn", {{ scale: 0.9, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(1.5)" }}, {s4_start} + 0.8);
    tl.fromTo("#s4Url", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {s4_start} + 1.1);
  </script>
</body>
</html>'''


# ═══════════════════════════════════════════════════
# COMPOSE — Sélection de template
# ═══════════════════════════════════════════════════

def compose(args: dict) -> dict:
    template = args.get("template", "lead_card")
    comp_id = _comp_id()

    template_map = {
        "lead_card": lead_card_html,
        "listicle": listicle_html,
        "compliance_report": compliance_report_html,
        "cta_only": lead_card_html,
        "custom": lead_card_html,
    }

    generator = template_map.get(template, lead_card_html)
    html_content = generator(args)

    return {
        "composition_id": comp_id,
        "template": template,
        "status": "composed",
        "format": args.get("format", "9:16"),
        "duration": args.get("duration", 10),
        "html_length": len(html_content),
        "html_preview": html_content[:500] + "..." if len(html_content) > 500 else html_content,
        "html_full": html_content,
        "render_hint": "Pour render: hyperframe_render ou node render-v3.js",
        "socialpulse_use": {
            "platform": "instagram" if args.get("format") == "9:16" else "linkedin",
            "content_type": template,
            "vertical": args.get("vertical", "unknown"),
        },
    }
