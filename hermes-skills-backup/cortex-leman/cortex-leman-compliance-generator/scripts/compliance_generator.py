#!/usr/bin/env python3
"""
Compliance Generator - Workflow principal
Orchestre le Narrateur, le Gardien et les API pour générer des posts de conformité
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from scripts.openrouter_client import OpenRouterClient, create_openrouter_client
from scripts.kieai_client import KieAIClient, create_kieai_client
from scripts.gardien_validator import GardienValidator, create_gardien_validator
from scripts.arxiv_fetcher import fetch_latest_arxiv_papers

# Configuration
logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """Requête de génération"""
    brief: str
    platforms: List[str]
    image_count: int = 2
    tone: str = "professional"
    enable_validation: bool = True
    use_arxiv: bool = True


@dataclass
class GenerationResult:
    """Résultat de génération"""
    success: bool
    posts: Dict[str, str]
    images: List[Dict]
    validation: Dict[str, dict]
    metadata: Dict
    error: Optional[str] = None


class ComplianceGenerator:
    """Générateur de posts de conformité"""

    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        kieai_client: KieAIClient,
        gardien_validator: Optional[GardienValidator] = None
    ):
        self.openrouter_client = openrouter_client
        self.kieai_client = kieai_client
        self.gardien_validator = gardien_validator or create_gardien_validator()

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Génère des posts de conformité

        Args:
            request: Requête de génération

        Returns:
            Résultat de génération
        """
        logger.info("=" * 60)
        logger.info("🚀 DÉMARRAGE GÉNÉRATION COMPLIANCE")
        logger.info("=" * 60)
        logger.info(f"Brief: {request.brief}")
        logger.info(f"Platforms: {', '.join(request.platforms)}")
        logger.info(f"Images: {request.image_count}")
        logger.info(f"Tone: {request.tone}")

        # Phase 0: Récupération arXiv si demandé
        arxiv_context = ""
        if request.use_arxiv:
            try:
                fetch_latest_arxiv_papers(days=7)
                if os.path.exists("/tmp/arxiv_latest.md"):
                    with open("/tmp/arxiv_latest.md", "r") as f:
                        arxiv_context = f.read()
                else:
                    logger.warning("[!] Pas de fichier arXiv trouvé à /tmp/arxiv_latest.md")
            except Exception as e:
                logger.error(f"[!] Échec récupération arXiv: {e}")
                request.use_arxiv = False
                arxiv_context = ""

        try:
            # Phase 1: Génération des posts (Le Narrateur)
            logger.info("\n📝 PHASE 1: GÉNÉRATION DES POSTS (Le Narrateur)")
            posts = self._generate_posts(request, arxiv_context)

            if not posts:
                return GenerationResult(
                    success=False,
                    posts={},
                    images=[],
                    validation={},
                    metadata={},
                    error="Échec génération des posts"
                )

            # Phase 2: Validation (Le Gardien)
            validation = {}
            if request.enable_validation and self.gardien_validator:
                logger.info("\n🔍 PHASE 2: VALIDATION (Le Gardien)")
                validation = self._validate_posts(posts, request.platforms)

            # Phase 3: Génération des images (Kie.ai)
            logger.info("\n🖼️ PHASE 3: GÉNÉRATION DES IMAGES (Kie.ai)")
            images = self._generate_images(request)

            # Compilation du résultat
            result = GenerationResult(
                success=True,
                posts=posts,
                images=images,
                validation=validation,
                metadata=self._build_metadata(request)
            )

            logger.info("\n✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 60)

            return result

        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            return GenerationResult(
                success=False,
                posts={},
                images=[],
                validation={},
                metadata={},
                error=str(e)
            )

    def _generate_posts(self, request: GenerationRequest, arxiv_context: str = "") -> Dict[str, str]:
        """
        Génère les posts de réseaux sociaux
        
        Args:
            request: Requête de génération
            arxiv_context: Contexte arXiv (optionnel)
        
        Returns:
            Dictionnaire {platforme: texte}
        """
        posts = {}

        try:
            # Enrichir le brief avec le contexte arXiv
            enhanced_brief = request.brief
            if arxiv_context:
                enhanced_brief = f"{arxiv_context}\n\n--- BRIEF ---\n{request.brief}"

            posts = self.openrouter_client.generate_all_posts(
                brief=enhanced_brief,
                platforms=request.platforms,
                tone=request.tone
            )

            for platform, text in posts.items():
                if text:
                    logger.info(f"✅ Post {platform}: {len(text)} caractères")
                else:
                    logger.warning(f"⚠️ Post {platform}: vide ou échec")

        except Exception as e:
            logger.error(f"❌ Erreur génération posts: {e}")

        return posts

    def _validate_posts(self, posts: Dict[str, str], platforms: List[str]) -> Dict[str, dict]:
        """
        Valide les posts

        Args:
            posts: Posts générés
            platforms: Plateformes visées

        Returns:
            Résultats de validation
        """
        validation_results = {}

        for platform in platforms:
            if platform in posts:
                validation_results[platform] = self.gardien_validator.validate_post(
                    posts[platform],
                    platform
                )

                result = validation_results[platform]
                if result.is_valid:
                    logger.info(f"✅ Validation {platform}: OK (confiance: {result.confidence:.2f})")
                else:
                    logger.warning(f"⚠️ Validation {platform}: {len(result.issues)} issues")
                    for issue in result.issues[:3]:  # Afficher les 3 premières
                        logger.warning(f"  - {issue['severity']}: {issue['issue']}")

        return validation_results

    def _generate_images(self, request: GenerationRequest) -> List[Dict]:
        """
        Génère les images

        Args:
            request: Requête de génération

        Returns:
            Liste d'images
        """
        images = []

        try:
            images = self.kieai_client.generate_compliance_images(
                brief=request.brief,
                image_count=request.image_count
            )

            logger.info(f"✅ Images générées: {len(images)}/{request.image_count}")

            for img in images:
                logger.info(f"  - Image {img['index']} ({img['type']}): {img['url']}")

        except Exception as e:
            logger.error(f"❌ Erreur génération images: {e}")

        return images

    def _build_metadata(self, request: GenerationRequest) -> Dict:
        """
        Construit les métadonnées

        Args:
            request: Requête de génération

        Returns:
            Métadonnées
        """
        return {
            "brief": request.brief,
            "platforms": request.platforms,
            "image_count": request.image_count,
            "tone": request.tone,
            "validation_enabled": request.enable_validation
        }


def create_compliance_generator(
    openrouter_api_key: str,
    kieai_api_key: str,
    enable_validation: bool = True
) -> Optional[ComplianceGenerator]:
    """
    Crée un générateur de conformité

    Args:
        openrouter_api_key: Clé API OpenRouter
        kieai_api_key: Clé API Kie.ai
        enable_validation: Activer la validation

    Returns:
        Instance de ComplianceGenerator ou None
    """
    try:
        # Créer les clients
        openrouter_client = create_openrouter_client(openrouter_api_key)
        kieai_client = create_kieai_client(kieai_api_key)

        if not openrouter_client or not kieai_client:
            return None

        # Créer le validateur
        gardien = create_gardien_validator() if enable_validation else None

        # Créer le générateur
        return ComplianceGenerator(
            openrouter_client=openrouter_client,
            kieai_client=kieai_client,
            gardien_validator=gardien
        )

    except Exception as e:
        logger.error(f"❌ Erreur création générateur: {e}")
        return None


if __name__ == "__main__":
    # Test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Clés API
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    kieai_key = os.getenv("KIEAI_API_KEY", "[REDACTED-KIEAI-KEY]")

    if not openrouter_key:
        print("❌ OPENROUTER_API_KEY non définie")
        exit(1)

    # Créer le générateur
    generator = create_compliance_generator(
        openrouter_api_key=openrouter_key,
        kieai_api_key=kieai_key,
        enable_validation=True
    )

    if not generator:
        print("❌ Erreur création générateur")
        exit(1)

    # Test génération
    request = GenerationRequest(
        brief="Nouvelle obligation RGPD pour IA générative",
        platforms=["linkedin", "twitter"],
        image_count=2,
        tone="professional",
        enable_validation=True
    )

    result = generator.generate(request)

    print("\n" + "=" * 60)
    print("📊 RÉSULTAT")
    print("=" * 60)

    if result.success:
        print(f"\n✅ Succès!")

        print("\n📝 POSTS:")
        for platform, text in result.posts.items():
            print(f"\n{platform.upper()}:")
            print(text)

        print("\n🖼️ IMAGES:")
        for img in result.images:
            print(f"\n  Image {img['index']} ({img['type']}):")
            print(f"  URL: {img['url']}")

        print("\n🔍 VALIDATION:")
        for platform, validation in result.validation.items():
            print(f"\n{platform.upper()}:")
            print(f"  Valid: {validation.is_valid}")
            print(f"  Confidence: {validation.confidence:.2f}")
            print(f"  Issues: {len(validation.issues)}")
    else:
        print(f"\n❌ Erreur: {result.error}")
