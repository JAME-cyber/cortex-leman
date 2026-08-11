#!/usr/bin/env python3
"""
Kie.ai Client pour Cortex Leman Compliance Generator
Utilise NanoBanana pour la génération d'images (infographies, diagrammes)
"""

import os
import requests
import logging
import time
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum

# Configuration
logger = logging.getLogger(__name__)


class ImagePromptType(Enum):
    """Types de prompts pour images"""
    INFOGRAPHY = "infography"
    DIAGRAM = "diagram"
    ILLUSTRATION = "illustration"
    ICON = "icon"


@dataclass
class KieAIConfig:
    """Configuration pour Kie.ai"""
    api_key: str
    base_url: str = "https://api.kie.ai"
    model: str = "nano-banana"
    timeout: int = 120  # 2 minutes pour la génération
    poll_interval: int = 5  # Vérifier toutes les 5 secondes
    max_poll_attempts: int = 24  # Max 2 minutes (24 * 5s)


class KieAIClient:
    """Client Kie.ai pour Cortex Leman"""
    
    def __init__(self, config: KieAIConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        })
    
    def _create_prompt(self, brief: str, prompt_type: ImagePromptType) -> str:
        """
        Crée un prompt optimisé pour NanoBanana
        
        Args:
            brief: Description du sujet
            prompt_type: Type d'image voulu
        
        Returns:
            Prompt optimisé
        """
        prompts = {
            ImagePromptType.INFOGRAPHY: f"""Professional compliance infographic about: "{brief}".
Design: Clean, modern, corporate style. Flat design with subtle gradients.
Colors: Blue, white, gray (trustworthy corporate colors).
Elements: Icons representing data protection, security, compliance, GDPR.
Text: Minimal, readable sans-serif fonts.
Style: Similar to Canva business infographics.
Background: Clean, light gray or white.
Aspect ratio: 16:9.""",

            ImagePromptType.DIAGRAM: f"""Compliance flowchart or process diagram about: "{brief}".
Design: Professional, clear, structured.
Elements: Boxes, arrows, process steps, decision points.
Style: Clean, modern, business documentation style.
Colors: Blue accent on white background.
Aspect ratio: 16:9.""",

            ImagePromptType.ILLUSTRATION: f"""Business illustration about: "{brief}".
Design: Professional vector illustration.
Style: Flat, modern, corporate.
Elements: Business people, technology icons, data protection symbols.
Colors: Blue, white, gray corporate palette.
Background: Subtle or white.
Aspect ratio: 16:9.""",

            ImagePromptType.ICON: f"""Professional icon representing: "{brief}".
Design: Minimal, clean, scalable.
Style: Line art or flat design.
Colors: Blue or monochrome.
Background: Transparent or white.
Aspect ratio: 1:1."""
        }
        
        return prompts.get(prompt_type, prompts[ImagePromptType.INFOGRAPHY])
    
    def generate_single_image(self, prompt: str) -> Optional[Dict]:
        """
        Génère une seule image
        
        Args:
            prompt: Prompt de génération
        
        Returns:
            Dictionnaire avec l'URL de l'image ou None
        """
        try:
            # Lancer la génération
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "num_images": 1,
                "aspect_ratio": "16:9"
            }
            
            logger.info(f"📤 Lancement génération image...")
            response = self.session.post(
                f"{self.config.base_url}/images/generate",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get("task_id")
                
                if not task_id:
                    logger.error("❌ Pas de task_id dans la réponse")
                    return None
                
                # Polling pour obtenir le résultat
                return self._poll_result(task_id)
            else:
                logger.error(f"❌ Erreur génération: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout Kie.ai ({self.config.timeout}s)")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur Kie.ai: {e}")
            return None
    
    def generate_compliance_images(self, brief: str, image_count: int = 2) -> List[Dict]:
        """
        Génère des images pour la conformité RGPD/IA
        
        Args:
            brief: Description du sujet
            image_count: Nombre d'images à générer (1-4)
        
        Returns:
            Liste de dictionnaires {url, type}
        """
        if image_count < 1 or image_count > 4:
            image_count = 2
            logger.warning(f"⚠️ Nombre d'images ajusté à {image_count}")
        
        # Types d'images à générer
        prompt_types = [
            ImagePromptType.INFOGRAPHY,
            ImagePromptType.DIAGRAM,
            ImagePromptType.ILLUSTRATION,
            ImagePromptType.ICON
        ]
        
        images = []
        
        for i in range(image_count):
            prompt_type = prompt_types[i % len(prompt_types)]
            prompt = self._create_prompt(brief, prompt_type)
            
            logger.info(f"🖼️ Génération image {i+1}/{image_count} ({prompt_type.value})...")
            
            result = self.generate_single_image(prompt)
            
            if result and result.get("image_url"):
                images.append({
                    "url": result["image_url"],
                    "type": prompt_type.value,
                    "index": i + 1
                })
                logger.info(f"✅ Image {i+1} générée: {result['image_url']}")
            else:
                logger.warning(f"⚠️ Échec génération image {i+1}")
        
        return images
    
    def _poll_result(self, task_id: str) -> Optional[Dict]:
        """
        Poll pour obtenir le résultat de la génération
        
        Args:
            task_id: ID de la tâche
        
        Returns:
            Dictionnaire avec l'URL de l'image ou None
        """
        for attempt in range(self.config.max_poll_attempts):
            try:
                response = self.session.get(
                    f"{self.config.base_url}/images/result/{task_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status == "completed":
                        image_url = data.get("result", {}).get("image_url")
                        if image_url:
                            logger.info(f"✅ Génération terminée")
                            return {"image_url": image_url, "task_id": task_id}
                    
                    elif status == "failed":
                        logger.error(f"❌ Génération échouée: {data.get('error')}")
                        return None
                    
                    elif status in ["pending", "processing"]:
                        # Continuer polling
                        logger.info(f"⏳ En attente... (tentative {attempt+1}/{self.config.max_poll_attempts})")
                        time.sleep(self.config.poll_interval)
                
                else:
                    logger.error(f"❌ Erreur polling: {response.status_code}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"⚠️ Timeout polling")
            except Exception as e:
                logger.error(f"❌ Erreur polling: {e}")
                return None
        
        logger.error(f"❌ Timeout après {self.config.max_poll_attempts} tentatives")
        return None


# Fonction utilitaire
def create_kieai_client(api_key: str) -> Optional[KieAIClient]:
    """
    Crée un client Kie.ai
    
    Args:
        api_key: Clé API Kie.ai
    
    Returns:
        Instance de KieAIClient ou None
    """
    if not api_key:
        logger.error("❌ Clé API Kie.ai non fournie")
        return None
    
    config = KieAIConfig(api_key=api_key)
    return KieAIClient(config)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("KIEAI_API_KEY")
    if not api_key:
        print("❌ KIEAI_API_KEY non définie")
        exit(1)
    
    client = create_kieai_client(api_key)
    
    # Test génération
    brief = "Nouvelle obligation RGPD pour IA générative"
    images = client.generate_compliance_images(brief, image_count=2)
    
    print("\n=== IMAGES GÉNÉRÉES ===")
    for img in images:
        print(f"\nImage {img['index']} ({img['type']}):")
        print(f"URL: {img['url']}")
