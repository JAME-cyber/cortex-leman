# CTA Unification — Carte CTA standardisée multi-vidéo

## Problème

Session juil. 2026 (Culture en Saveur): 7 vidéos produites avec des CTA différents selon les scripts. Certaines affichaient juste "85 CHF", d'autres "10-14 AOUT 2025" (année périmée), d'autres oubliaient les horaires, la promo fratrie, ou la tranche d'âge. L'utilisateur a dû demander explicitement "rajoute les horaires, les 10% dès le 2e enfant".

## Principe

**Un seul bloc CTA, répliqué à l'identique sur toutes les vidéos d'information.** Ne pas improviser par vidéo — définir le CTA une fois, le coder comme fonction/helper, et l'appeler partout.

## Le CTA unifié standard (FR-CH événementiel)

```
[Titre de la vidéo]

4-12 ans  •  10-14 AOUT 2026
Petit-Lancy, Genève

JOURNÉE 8h30-18h30: 85 CHF
Demi-journée: 55 CHF
-10% dès le 2e enfant !

Places limitées à 12 enfants
INSCRIVEZ-VOUS !

+41 76 756 22 82
email@association.ch
@instagram_handle
```

## Champs obligatoires (à valider avec le brief AVANT de coder)

| Champ | Source | Erreur fréquente |
|-------|--------|------------------|
| Tranche d'âge | Brief | Oubli total |
| Dates complètes | Brief | Année périmée (2025→2026) |
| Lieu + ville | Brief | Ville oubliée (juste "Petit-Lancy") |
| Tarif journée + horaires | Brief tarif | Horaires manquants (juste "85 CHF") |
| Tarif demi-journée | Brief tarif | Omission totale |
| Promo fratrie | Brief | Oubli ("10% dès le 2e enfant") |
| Places limitées | Brief | Mention floue |
| Téléphone | Brief contact | Format incohérent |
| Email | Brief contact | Avec/sans S dans le nom |
| Instagram | Brief contact | **Underscore oublié** (`@culture_ensaveurs` ≠ `@cultureensaveurs`) |

## Pattern PIL pour CTA card (reusable)

```python
def generate_cta_card(title_text, W=720, H=1280):
    """Generate a standardized CTA end card with full pricing info."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (W, H), (38, 30, 27))  # Terracotta dark
    draw = ImageDraw.Draw(img)

    C_SAFFRON = '#D88A22'
    C_TEAL = '#5BA897'
    C_CREAM = '#F5E6D3'
    C_OCHRE = '#C4956C'

    # Title
    draw.text((W//2, 200), title_text, fill=C_CREAM, font=font(34, bold=True), anchor='mt')
    # Bandeau info
    draw.text((W//2, 350), "4-12 ans  •  10-14 AOUT 2026", fill=C_SAFFRON, font=font(28, bold=True), anchor='mt')
    draw.text((W//2, 400), "Petit-Lancy, Geneve", fill=C_CREAM, font=font(26, bold=False), anchor='mt')
    # Tarifs
    draw.text((W//2, 490), "JOURNEE 8h30-18h30", fill=C_TEAL, font=font(28, bold=True), anchor='mt')
    draw.text((W//2, 530), "85 CHF / semaine", fill=C_CREAM, font=font(42, bold=True), anchor='mt')
    draw.text((W//2, 600), "Demi-journee: 55 CHF", fill=C_CREAM, font=font(26, bold=False), anchor='mt')
    # Promo fratrie
    draw.text((W//2, 680), "-10% des le 2e enfant !", fill=C_SAFFRON, font=font(32, bold=True), anchor='mt')
    draw.text((W//2, 740), "Places limitees a 12 enfants", fill=C_CREAM, font=font(26, bold=True), anchor='mt')
    # Contact
    draw.text((W//2, 850), "INSCRIVEZ-VOUS !", fill=C_CREAM, font=font(32, bold=True), anchor='mt')
    for i, c in enumerate(["+41 76 756 22 82", "email@example.com", "@handle"]):
        draw.text((W//2, 920 + i*42), c, fill=C_OCHRE, font=font(24, bold=False), anchor='mt')

    return img  # caller saves to file
```

## Quand utiliser

- **Toutes les vidéos d'information** d'une campagne (T1, T2, T3, T4, Programme) → CTA complet avec tarifs
- **Teaser** → CTA condensé (1 ligne tarifs, pas le détail)
- **Catering/stand-alone** → CTA spécifique au service (réservation stand, pas inscription stage)

## Compression TG pour vidéos >40s

Les vidéos de 50s+ dépassent souvent la limite TG confortable (<5MB). Recette:

```bash
# Standard (OK pour <40s): 720x1280, CRF 26
ffmpeg -y -i input.mp4 -crf 26 -maxrate 3200k -vf "scale=720:1280" \
  -c:a aac -b:a 128k -movflags +faststart output_TG.mp4

# Heavy (pour 50s+): 540x960, CRF 30
ffmpeg -y -i input.mp4 -crf 30 -maxrate 2000k -bufsize 4000k \
  -vf "scale=540:960" -c:a aac -b:a 96k -movflags +faststart output_TG.mp4
```

Le scale 540:960 + CRF 30 réduit une vidéo de 55s de 17MB → 4.3MB sans perte de lisibilité sur mobile.

---

## CTA Segment Swap depuis vidéo de référence

### Principe clé : CUT > RECREATE

**Quand l'utilisateur fournit une vidéo de référence et dit "j'aime bien cette partie"** → couper l'extrait et l'incorporer directement. NE PAS recréer programmatiquement (PIL, canvas, etc.) ce qui existe déjà en footage.

**Exemple session (juil. 2026, T4 Culture en Saveur):** L'utilisateur a envoyé une vidéo de référence et pointé le segment 15-19s (silhouettes enfants au coucher de soleil + CTA complet). L'agent a d'abord construit une recréation PIL (`build_sunset_cta.py`) — l'utilisateur a corrigé : "En fait tu peux pas couper la vidéo c'est ça". Solution : couper le segment et le concaténer.

### Technique : remplacer le CTA d'une vidéo existante

```bash
# Inputs: video originale (avec vieux CTA), vidéo référence (avec bon CTA), musique
ffmpeg -y \
  -i original.mp4 \
  -i reference.mp4 \
  -i music.mp3 \
  -filter_complex "
    # 1. Body: garder tout sauf l'ancien CTA (cut avant le CTA)
    [0:v]trim=0:CUT_POINT,setpts=PTS-STARTPTS,scale=720:1280,fps=30[v1];
    # 2. Nouveau CTA: extraire le segment de la vidéo de référence
    [1:v]trim=START:END,setpts=PTS-STARTPTS,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,fps=30[v2];
    # 3. Audio body: garder la VO
    [0:a]atrim=0:CUT_POINT,asetpts=PTS-STARTPTS[a1];
    # 4. Audio CTA: musique en fade-out (pas de VO sur le CTA)
    [2:a]atrim=OFFSET:OFFSET+CTA_DUR,asetpts=PTS-STARTPTS,afade=t=out:st=FADE_START:d=0.7,volume=0.3[a2];
    # 5. Concat vidéo + audio
    [v1][v2]concat=n=2:v=1:a=0[vout];
    [a1][a2]concat=n=2:v=0:a=1[aout]
  " \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -crf 20 -pix_fmt yuv420p -preset fast \
  -c:a aac -b:a 128k -r 30 \
  output_v2.mp4
```

**Variables à déterminer:**
- `CUT_POINT` : où commence l'ancien CTA (duration totale - durée ancien CTA)
- `START:END` : segment désiré dans la vidéo de référence
- `OFFSET` : position dans le morceau de musique pour le fade-out
- `CTA_DUR` : durée du nouveau CTA (= END - START)

### Checklist swap CTA

1. ✅ Identifier le `CUT_POINT` (où commence l'ancien CTA dans la vidéo originale)
2. ✅ Extraire le segment désiré de la vidéo de référence (`ffprobe` pour les timestamps exacts)
3. ✅ Vérifier la résolution cible (720×1280 pour 9:16)
4. ✅ Gérer l'audio : VO pour le body, musique fade-out pour le CTA
5. ✅ Compresser pour livraison TG (`-crf 26 -maxrate 3200k -preset fast`)
6. ✅ Valider durée finale (`ffprobe`)

### Vision analysis workaround (GLM-5.2)

GLM-5.2 n'accepte pas les images dans les messages (erreur 1210 : `messages.content.type is invalid, allowed values: ['text']`). Pour analyser des frames vidéo/images :

```bash
# 1. Extraire frames ou contact sheet
ffmpeg -y -i video.mp4 -vf "fps=2,scale=240:427,tile=4x2" -frames:v 1 -update 1 /tmp/contact.jpg

# 2. Envoyer à Qwen 2.5 VL 72B via OpenRouter
python3.12 -c "
import json, base64
with open('/tmp/contact.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()
payload = json.dumps({
    'model': 'qwen/qwen2.5-vl-72b-instruct',
    'messages': [{'role': 'user', 'content': [
        {'type': 'text', 'text': 'Describe each frame...'},
        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{img_b64}'}}
    ]}]
})
with open('/tmp/vl_payload.json', 'w') as f: f.write(payload)
"
curl -s --max-time 90 -X POST 'https://openrouter.ai/api/v1/chat/completions' \
  -H 'Authorization: Bearer $OPENROUTER_API_KEY' \
  -H 'Content-Type: application/json' \
  -d @/tmp/vl_payload.json
```

Alternative : extraire des frames individuelles à plus haute résolution pour les détails précis.
