---
name: alconst-deployment
description: Deploy or update the AlConst website infra.
---

# AlConst Website Deployment

## Architecture
- **Source**: GitHub `koussek/alconst-website` (PAT scopes: `repo` + `workflow`)
- **Hosting**: Cloudflare Pages → `alconst-website.pages.dev`
- **Domain**: `alconstdigital.ch` @ Infomaniak (NS `ns11/ns12.infomaniak.ch`)
- **Auto-deploy**: GitHub Actions `cloudflare/wrangler-action@v3` on push to `main`
- **Local**: `/home/tars/alconst-digital/` (branch `main`)

## Identifiants (en mémoire)
- GitHub PAT: `ghp_NN...3q62` (scopes repo+workflow)
- Cloudflare token: `cfat_3...` (Pages Write, Domains Write)
- Infomaniak login: `alconst@protonmail.com`

## IDs Infomaniak
- account_id: `743498`
- domain_id: `2228448`
- DNS zone URL directe: `https://manager.infomaniak.com/v3/743498/ng/domain/2228448/dns/manage-zone/add`

## Procédures

### Déployer une mise à jour du site
```bash
cd /home/tars/alconst-digital
git add -A && git commit -m "description" && git push origin main
# Si GitHub Actions ne déclenche pas (ToS non acceptées), déployer manuellement:
npx wrangler pages deploy . --project-name=alconst-website
```

### Ajouter un domaine custom sur Cloudflare
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{cf_account_id}/pages/projects/alconst-website/domains" \
  -H "Authorization: Bearer cfat_3..." \
  -H "Content-Type: application/json" \
  -d '{"name":"alconstdigital.ch"}'
```

### Créer le CNAME chez Infomaniak
1. Aller à l'URL DNS directe (ci-dessus)
2. **Login**: utiliser `browser_type(@ref)` pour le mot de passe — `execCommand` et native setters React ÉCHOUENT
3. **Sélectionner CNAME**: cliquer sur `div.body-type-key-cell` contenant "CNAME" (PAS le `<input type="radio">`)
4. Le bouton "Suivant" s'active après le bon clic
5. Remplir: **Source** = `www`, **Valeur** = `alconst-website.pages.dev`
6. Valider

## Pitfalls
- **Infomaniak login React**: `execCommand` et native setters échouent. Utiliser `browser_type(@ref)`.
- **Angular Material radio**: Cliquer `div.body-type-key-cell` avec MouseEvent (mousedown+mouseup+click), PAS le radio directement.
- **GitHub Actions ToS**: Si les Actions ne s'exécutent pas, accepter les ToS sur `github.com/koussek/alconst-website/actions`.
- **GH PAT scopes**: `workflow` est une case SÉPARÉE de `repo`.
- **CF dashboard**: Protégé par Turnstile → Wrangler CLI + API uniquement.
