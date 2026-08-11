#!/usr/bin/env python3
"""
API FastAPI pour Cortex Leman Compliance Generator
Intégration dans l'infrastructure Docker existante
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import sys
import logging
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.compliance_generator import (
    ComplianceGenerator,
    create_compliance_generator,
    GenerationRequest,
    GenerationResult
)

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration API
app = FastAPI(
    title="Cortex Leman Compliance Generator API",
    description="API pour générer des posts de conformité RGPD/IA pour PME FR-CH",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, restreindre aux origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clés API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
KIEAI_API_KEY = os.getenv("KIEAI_API_KEY", "[REDACTED-KIEAI-KEY]")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Générateur (lazy initialization)
_generator: Optional[ComplianceGenerator] = None


# Modèles Pydantic
class GenerateRequest(BaseModel):
    """Requête de génération"""
    brief: str = Field(..., description="Brief sur le sujet (ex: 'Nouvelle obligation RGPD pour IA')")
    platforms: List[str] = Field(default=["linkedin", "twitter"], description="Plateformes visées")
    image_count: int = Field(default=2, ge=1, le=4, description="Nombre d'images à générer")
    tone: str = Field(default="professional", description="Ton des posts")
    enable_validation: bool = Field(default=True, description="Activer la validation")


class GenerateResponse(BaseModel):
    """Réponse de génération"""
    success: bool
    posts: dict
    images: list
    validation: dict
    metadata: dict
    timestamp: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Réponse de santé"""
    status: str
    api_key_openrouter: bool
    api_key_kieai: bool
    generator_ready: bool
    timestamp: str


# Fonctions utilitaires
def get_generator() -> ComplianceGenerator:
    """Récupère ou crée le générateur"""
    global _generator
    
    if _generator is None:
        logger.info("🏗️ Initialisation du générateur...")
        _generator = create_compliance_generator(
            openrouter_api_key=OPENROUTER_API_KEY,
            kieai_api_key=KIEAI_API_KEY,
            enable_validation=True
        )
        
        if _generator:
            logger.info("✅ Générateur initialisé avec succès")
        else:
            logger.error("❌ Erreur initialisation du générateur")
            raise HTTPException(
                status_code=500,
                detail="Erreur initialisation du générateur (clés API manquantes?)"
            )
    
    return _generator


# Routes
@app.get("/", response_model=dict)
async def root():
    """Route racine"""
    return {
        "name": "Cortex Leman Compliance Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Vérifie la santé de l'API"""
    try:
        generator = None
        generator_ready = False
        
        if OPENROUTER_API_KEY and KIEAI_API_KEY:
            try:
                generator = get_generator()
                generator_ready = True
            except:
                pass
        
        return HealthResponse(
            status="healthy",
            api_key_openrouter=bool(OPENROUTER_API_KEY),
            api_key_kieai=bool(KIEAI_API_KEY),
            generator_ready=generator_ready,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Erreur health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Génère des posts de conformité RGPD/IA
    
    Args:
        request: Requête de génération
        background_tasks: Tâches de fond
    
    Returns:
        Résultat de génération
    """
    try:
        logger.info(f"📥 Requête de génération reçue: {request.brief}")
        
        # Récupérer le générateur
        generator = get_generator()
        
        # Créer la requête de génération
        gen_request = GenerationRequest(
            brief=request.brief,
            platforms=request.platforms,
            image_count=request.image_count,
            tone=request.tone,
            enable_validation=request.enable_validation
        )
        
        # Exécuter la génération
        logger.info("🚀 Lancement de la génération...")
        result = generator.generate(gen_request)
        
        # Préparer la réponse
        response = GenerateResponse(
            success=result.success,
            posts=result.posts,
            images=result.images,
            validation={
                platform: {
                    "is_valid": val.is_valid,
                    "confidence": val.confidence,
                    "issues": [
                        {
                            "rule": issue["rule"],
                            "severity": issue["severity"],
                            "description": issue["description"],
                            "issue": issue["issue"],
                            "correction": issue.get("correction")
                        }
                        for issue in val.issues
                    ],
                    "corrected_text": val.corrected_text
                }
                for platform, val in result.validation.items()
            },
            metadata=result.metadata,
            timestamp=datetime.utcnow().isoformat(),
            error=result.error
        )
        
        logger.info(f"✅ Génération terminée: {result.success}")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur génération: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@app.get("/api/stats")
async def get_stats():
    """Récupère les statistiques de l'API"""
    return {
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/api/generate",
            "health": "/health",
            "docs": "/docs"
        },
        "config": {
            "openrouter_configured": bool(OPENROUTER_API_KEY),
            "kieai_configured": bool(KIEAI_API_KEY),
            "validation_enabled": True
        }
    }


# Démarrage
if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Démarrage de l'API Cortex Leman Compliance Generator...")

    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
