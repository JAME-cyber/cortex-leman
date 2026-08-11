---
name: compliance-content-generator
title: Compliance Content Generator
description: Build AI-powered content generators with automatic regulatory compliance validation in 60 seconds
category: cortex-leman
tags: [fastapi, nextjs, openrouter, kie-ai, rgpd, compliance, ai-generation, validation]
version: 1.0.0
author: Cortex Leman
---

# Compliance Content Generator Skill

Create AI-powered content generators with automatic validation for regulatory compliance (RGPD/AI/OWASP GenAI) in 60 seconds.

## Overview

Build complete SaaS applications that generate professional content with multi-modal AI and automatic compliance validation. Based on the Cortex Leman Compliance Generator architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         COMPLIANCE CONTENT GENERATOR                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              FRONTEND (Next.js 15)                  │  │
│  │  - React + TypeScript                              │  │
│  │  - Tailwind CSS                                    │  │
│  │  - Vercel deployment                                │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              BACKEND (FastAPI)                      │  │
│  │  - REST API                                        │  │
│  │  - OpenRouter integration (text)                   │  │
│  │  - Kie.ai integration (images)                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────┬──────────────────────────────┐    │
│  │                  │                              │    │
│  │  CONTENT         │         VALIDATION           │    │
│  │  - Narrateur     │         - Gardien             │    │
│  │  (generation)    │         (compliance)          │    │
│  └──────────────────┴──────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Use Cases

- **Social Media Posts**: Generate LinkedIn/Twitter posts for compliance topics
- **Blog Articles**: Generate long-form articles with compliance validation
- **Marketing Content**: Generate product descriptions with legal review
- **Documentation**: Generate technical docs with accuracy validation
- **Email Campaigns**: Generate outreach emails with privacy compliance

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- OpenRouter (text generation - DeepSeek, Claude, GPT-4, etc.)
- Kie.ai (image generation - NanoBanana, Flux, etc.)
- Docker

### Frontend
- Next.js 15
- TypeScript
- Tailwind CSS
- React Hook Form
- Zustand (optional for state management)

### Deployment
- Backend: Docker
- Frontend: Vercel (or alternative)

## Workflow

1. **User Input**: Brief, platforms, tone, image count
2. **Content Generation**: OpenRouter generates text posts
3. **Validation**: Custom validator checks compliance
4. **Image Generation**: Kie.ai generates visual content
5. **Result Display**: Posts + images + validation report
6. **Publish**: Copy/paste or auto-publish

## Implementation Steps

### Phase 1: Backend Setup

1. Create project structure:
```bash
mkdir compliance-generator
cd compliance-generator
mkdir -p scripts api frontend/types frontend/components
```

2. Create backend scripts:

**OpenRouter Client** (`scripts/openrouter_client.py`):
```python
import os
import requests
from typing import Dict, List

class OpenRouterClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourdomain.com",
            "X-Title": "Your App"
        })
    
    def generate_content(self, prompt: str, model: str = "deepseek/deepseek-chat") -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert content creator..."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        response = self.session.post(self.base_url, json=payload)
        return response.json()["choices"][0]["message"]["content"]
```

**Kie.ai Client** (`scripts/kieai_client.py`):
```python
import requests

class KieAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.kie.ai"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate_image(self, prompt: str, model: str = "nano-banana"):
        payload = {
            "model": model,
            "prompt": prompt,
            "num_images": 1,
            "aspect_ratio": "16:9"
        }
        response = self.session.post(f"{self.base_url}/images/generate", json=payload)
        return response.json()["result"]["image_url"]
```

**Validator** (`scripts/validator.py`):
```python
from typing import Dict, List

class ComplianceValidator:
    def validate(self, text: str, rules: List[callable]) -> Dict:
        issues = []
        for rule in rules:
            result = rule(text)
            if result.get("has_issue", False):
                issues.append(result)
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "confidence": 1.0 - (len(issues) * 0.1)
        }
```

3. Create API (`api/main.py`):
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scripts.openrouter_client import OpenRouterClient
from scripts.kieai_client import KieAIClient

app = FastAPI(title="Compliance Content Generator API")

class GenerateRequest(BaseModel):
    brief: str
    platforms: List[str]
    image_count: int = 2
    tone: str = "professional"

@app.post("/api/generate")
async def generate_content(request: GenerateRequest):
    # Generate content
    # Validate
    # Generate images
    return {"success": True, "posts": {...}, "images": [...], "validation": {...}}
```

### Phase 2: Frontend Setup

1. Initialize Next.js:
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind
```

2. Create components:

**Form Component** (`components/ContentForm.tsx`):
```typescript
'use client'
import { useState } from 'react'

export default function ContentForm({ onSubmit }: { onSubmit: (data: any) => void }) {
  const [brief, setBrief] = useState('')
  const [platforms, setPlatforms] = useState<string[]>(['linkedin'])
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ brief, platforms, image_count: 2, tone: 'professional' })
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <textarea value={brief} onChange={(e) => setBrief(e.target.value)} />
      <button type="submit">Generate</button>
    </form>
  )
}
```

**Result Display** (`components/ResultDisplay.tsx`):
```typescript
'use client'
import { ComplianceResult } from '@/types/compliance'

export default function ResultDisplay({ result }: { result: ComplianceResult }) {
  return (
    <div>
      {Object.entries(result.posts).map(([platform, text]) => (
        <div key={platform}>
          <h3>{platform}</h3>
          <p>{text}</p>
        </div>
      ))}
    </div>
  )
}
```

3. Create page (`app/page.tsx`):
```typescript
'use client'
import ContentForm from '@/components/ContentForm'
import ResultDisplay from '@/components/ResultDisplay'
import { useState } from 'react'

export default function Home() {
  const [result, setResult] = useState(null)
  
  const handleGenerate = async (data: any) => {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    setResult(await response.json())
  }
  
  return (
    <main>
      <ContentForm onSubmit={handleGenerate} />
      <ResultDisplay result={result} />
    </main>
  )
}
```

### Phase 3: Configuration

1. Environment variables (`.env`):
```bash
# Backend
OPENROUTER_API_KEY=sk-or-v1-...
KIEAI_API_KEY=...
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. Docker (`docker-compose.yml`):
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - KIEAI_API_KEY=${KIEAI_API_KEY}
```

3. Vercel deployment (`vercel.json`):
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.yourdomain.com"
  }
}
```

### Phase 4: Deployment

**Backend (Docker)**:
```bash
docker-compose up -d
```

**Frontend (Vercel)**:
```bash
cd frontend
vercel
```

## Configuration Examples

### OpenRouter Models

- `deepseek/deepseek-chat`: Fast, cheap ($0.14/1M tokens)
- `anthropic/claude-sonnet-4`: High quality ($15/1M tokens)
- `openai/gpt-4-turbo`: Balanced ($10/1M tokens)

### Kie.ai Models

- `nano-banana`: Fast image generation
- `flux-kontext`: High quality images
- `runway-aleph`: Advanced video generation

### Validation Rules

```python
# Example rules for RGPD compliance
rules = [
    lambda text: {"has_issue": "GDPR" not in text, "issue": "Missing GDPR mention"},
    lambda text: {"has_issue": "100%" in text, "issue": "Avoid absolute claims"},
    lambda text: {"has_issue": len(text) > 500, "issue": "Too long for platform"}
]
```

## Troubleshooting

### Issue: OpenRouter API key not found
**Solution**: Check environment variables are set:
```bash
echo $OPENROUTER_API_KEY
```

### Issue: Port already in use (error 98)
**Solution**: Kill the process or use different port:
```bash
lsof -i :8000
kill -9 <PID>
export API_PORT=8001
```

### Issue: ModuleNotFoundError for scripts
**Solution**: Add scripts directory to path:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
```

### Issue: Frontend build fails
**Solution**: Check Next.js config and install dependencies:
```bash
cd frontend
npm install
npm run build
```

## Best Practices

1. **API Keys**: Store in environment variables, never commit to repo
2. **Rate Limiting**: Implement rate limiting for production
3. **Caching**: Cache responses to reduce API costs
4. **Validation**: Always validate content before publishing
5. **Testing**: Test all workflows end-to-end before deployment
6. **Monitoring**: Set up logging and monitoring for production

## Cost Estimation

### OpenRouter
- Text generation: ~$0.0001 per post
- 1000 posts: ~$0.10

### Kie.ai
- Image generation: ~$0.01 per image
- 1000 images: ~$10.00

### Total
- Per post (1 image): ~$0.01
- 1000 posts (1000 images): ~$10.10

## Integration with Cortex Leman

This skill integrates seamlessly with the Cortex Leman ecosystem:

- **Le Narrateur Augmenté**: Content generation
- **Le Gardien des Normes**: Compliance validation
- **L'Oeil de Cortex**: Research integration
- **L'Architecte Lémanique**: Strategic alignment
- **L'Ingénieur de Flux**: Technical implementation

## References

- [Cortex Leman Documentation](https://docs.cortex-leman.ch)
- [OpenRouter API](https://openrouter.ai/docs)
- [Kie.ai API](https://kie.ai/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## Version History

- **1.0.0** (2026-04-06): Initial version with OpenRouter + Kie.ai integration

## License

Cortex Leman - Audit RGPD-IA PME FR-CH
Copyright © 2026
