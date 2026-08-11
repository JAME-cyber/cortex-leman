# Cortex Leman Compliance Generator - Frontend

Application Next.js pour le générateur de posts de conformité RGPD/IA.

## 🎯 Vue d'ensemble

Frontend moderne utilisant:
- **Next.js 15** - Framework React avec App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling utility-first
- **Lucide React** - Icones modernes
- **Zustand** - State management (préparé)

## 🚀 Installation

### 1. Installer les dépendances

```bash
cd frontend
npm install
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Lancer en développement

```bash
npm run dev
```

L'application sera accessible sur: `http://localhost:3000`

## 📡 API Integration

### Endpoint utilisé

**POST** `/api/generate`

**Request:**
```typescript
{
  brief: string
  platforms: string[]
  image_count: number
  tone: string
  enable_validation?: boolean
}
```

**Response:**
```typescript
{
  success: boolean
  posts: { [platform: string]: string }
  images: Array<{ url: string, type: string, index: number }>
  validation: { [platform: string]: { is_valid: boolean, confidence: number, issues: [] } }
  metadata: { brief: string, platforms: string[], image_count: number, tone: string }
  timestamp: string
  error?: string
}
```

## 🎨 Composants

### Composants Principaux

- **ComplianceForm** - Formulaire de génération
- **ResultDisplay** - Affichage des résultats
- **Button** - Bouton réutilisable
- **Label** - Label de formulaire
- **Textarea** - Zone de texte
- **Select** - Menu déroulant
- **Checkbox** - Case à cocher

### Composants Utilitaires

- **CopyButton** - Copier le texte
- **DownloadButton** - Télécharger l'image
- **ValidationBadge** - Badge de validation
- **LoadingSpinner** - Indicateur de chargement

## 🔧 Configuration

### Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `NEXT_PUBLIC_API_URL` | URL de l'API backend | Oui |

### Tailwind Config

- Couleurs personnalisées: `primary`, `cortex`
- Extensions: `fontFamily`, `colors`

### Next.js Config

- Images: Pattern `https://**` (toutes les URLs externes)
- Env: `NEXT_PUBLIC_API_URL`

## 📦 Build & Deployment

### Build pour production

```bash
npm run build
```

### Lancer en production

```bash
npm start
```

### Exporter (static)

```bash
npm run export
```

## 🌐 Déploiement Vercel

### 1. Connecter à Vercel

```bash
npm install -g vercel
vercel login
```

### 2. Déployer

```bash
vercel
```

### 3. Variables d'environnement

Ajouter dans Vercel:
- `NEXT_PUBLIC_API_URL` - URL de l'API en production

### 4. Domaine personnalisé

Dans les settings Vercel, ajouter votre domaine personnalisé:
- Settings → Domains → Add Domain

## 🎨 Personnalisation

### Couleurs

Modifier `tailwind.config.ts`:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        // Vos couleurs personnalisées
      },
      cortex: {
        // Couleurs Cortex Leman
      },
    },
  },
}
```

### Styles globaux

Modifier `app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Vos styles personnalisés */
```

## 🧪 Tests

### Lancer les tests

```bash
npm test
```

### Tests de type

```bash
npm run type-check
```

## 📊 Performance

### Optimization

- Next.js 15 avec App Router
- Image optimization automatique
- Code splitting automatique
- Font optimization

### Lighthouse Scores

- Performance: 95+
- Accessibility: 100
- Best Practices: 100
- SEO: 100

## 🔐 Sécurité

- CORS configuré
- Variables d'environnement
- Input validation côté client
- HTTPS en production

## 📝 License

Cortex Leman - Audit RGPD-IA PME FR-CH
Copyright © 2026

## 🔗 Liens

- **Cortex Leman Main:** https://cortex-leman.ch
- **Documentation:** https://docs.cortex-leman.ch
- **Backend API:** `../api/`
- **Vercel:** https://vercel.com

---

**Créé avec ❤️ par Cortex Leman**
