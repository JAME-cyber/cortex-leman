# Video AI Intelligence Brief — État connu (baseline)

**Dernière mise à jour:** 2026-08-11
**Rôle:** Référence pour le cron "Video AI Radar". Si une web search retourne quelque chose de NOUVEAU vs cette baseline → alerter Tars.

## Modèles surveillés

### Seedance (ByteDance) — Provider Pricing Reference
- **Higgsfield** (BEST): €39/mo = 1K credits + UNLIMITED images. 4K natif. CLI+MCP. higgsfield.ai
- **Flova AI** (CHEAPEST): $0.03/s 480p. Skills vidéo + CLI. 300 credits free. flova.ai
- **kie.ai** (LEGACY): $0.315/s 720p. ABANDONNÉ (10x trop cher)
- **OpenArt**: Unlimited 480p Seedance 2.5. À vérifier.
- **Version actuelle:** 2.5 sur kie.ai
- **Prix:** 720p T2V $0.315/s, 480p $0.140/s
- **Features clés:** 30s max, 50 refs multimodales, first/last frame chaining, audio natif, @Image syntax
- **Détection nouveauté:** "Seedance 3.0" OR "Seedance 2.6" OR nouveau sur kie.ai

### Kamo-1 (Kinetix / Philip Belhassen)
- **Statut:** Open beta depuis déc 2025
- **USP:** 3D-conditioned video, motion control + camera 3D
- **Prix:** Inconnu (beta)
- **Détection nouveauté:** API publique, pricing, version 2, features cartoon/animation

### Google Veo
- **Version actuelle:** Veo 3
- **Features:** Audio natif, 1080p, 4K
- **Détection nouveauté:** Veo 4, nouveaux features, prix changé, disponibilité élargie

### Kling (Kuaishou)
- **Version actuelle:** Kling 2.0
- **Détection nouveauté:** Kling 2.5/3.0, prix, nouveaux modes

### Wan Video (Alibaba)
- **Version actuelle:** Wan 2.6
- **Features:** Multi-shot storytelling, 15s, 720p/1080p
- **Détection nouveauté:** Wan 3.0, API publique

### Hailuo / Minimax
- **Disponible via:** kie.ai
- **Détection nouveauté:** Nouveau modèle sur kie.ai, prix changé

### Runway
- **Version actuelle:** Gen-4
- **Détection nouveauté:** Gen-5, nouveau pricing

### Sora (OpenAI)
- **Statut:** Disponible ChatGPT Pro/Plus
- **Détection nouveauté:** Sora 2, API publique, prix

## Sources à surveiller
- kie.ai changelog/blog
- kinetix.tech blog
- x.com comptes: @matchaman11, @Diplomeme, @0x_fokki, @LiorNsnd
- GitHub: SamurAIGPT/Seedance-2.5-API
- Reddit: r/aivideo, r/StableDiffusion
