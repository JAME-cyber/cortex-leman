#!/usr/bin/env python3
"""
OpenRouter Client pour Cortex Leman Compliance Generator
Utilise DeepSeek v3.2 pour la génération de texte
"""

import os
import requests
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configuration
logger = logging.getLogger(__name__)

@dataclass
class OpenRouterConfig:
    """Configuration pour OpenRouter"""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    model: str = "deepseek/deepseek-chat-v3"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30

class OpenRouterClient:
    """Client OpenRouter pour Cortex Leman"""
    
    def __init__(self, config: OpenRouterConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cortex-leman.ch",
            "X-Title": "Cortex Leman Compliance Generator"
        })
    
    def generate_linkedin_post(self, brief: str, tone: str = "professional") -> str:
        """
        Génère un post LinkedIn pour la conformité RGPD/IA
        
        Args:
            brief: Description du sujet (ex: "Nouvelle obligation RGPD pour IA")
            tone: Ton du post (professional, accessible, urgent)
        
        Returns:
            Texte du post LinkedIn (300-500 caractères)
        """
        system_prompt = """Tu es Le Narrateur Augmenté, un expert en communication pour Cortex Leman.
Ton rôle: Générer des posts LinkedIn professionnels sur la conformité RGPD/IA pour des PME FR-CH.

Style:
- Professional mais accessible
- Informatif et engageant
- 300-500 caractères
- Emojis pertinents (2-3 max)
- 5-7 hashtags pertinents (#RGPD #Compliance #DataProtection #IA #FranceSuisse)

Structure:
1. Hook émotionnel ou question
2. Information clé (une phrase)
3. Action ou réflexion
4. Hashtags

Exemple:
🔒 RGPD & IA: Ce que les PME FR-CH doivent savoir en 2026

L'UE renforce les obligations sur l'IA générative. Pour votre PME: documentation obligatoire, DPIA pour systèmes à haut risque, transparence utilisateurs.

Prêt à évaluer votre conformité ?

#RGPD #Compliance #DataProtection #AI #FranceSuisse"""

        user_prompt = f"""Génère un post LinkedIn sur ce sujet: "{brief}"
Ton: {tone}
Contraintes: 300-500 caractères, professional mais accessible, 5-7 hashtags."""

        return self._generate_text(system_prompt, user_prompt)
    
    def generate_twitter_post(self, brief: str) -> str:
        """
        Génère un post Twitter pour la conformité RGPD/IA
        
        Args:
            brief: Description du sujet
        
        Returns:
            Texte du post Twitter (280 caractères max)
        """
        system_prompt = """Tu es Le Narrateur Augmenté, expert en communication.
Ton rôle: Générer des posts Twitter concis sur la conformité RGPD/IA.

Style:
- Ultra-concis (280 caractères max)
- Direct et informatif
- 2-3 emojis
- 3-5 hashtags

Exemple:
🔒 RGPD & IA: Nouvelles obligations UE 🇪🇺
DPIA pour IA à haut risque, documentation obligatoire.
Les PME FR-CH concernées ? Oui.

#RGPD #AI #FranceSuisse"""

        user_prompt = f"""Génère un post Twitter sur ce sujet: "{brief}"
Contraintes: 280 caractères max, direct, informatif."""

        return self._generate_text(system_prompt, user_prompt)
    
    def _generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Génère du texte avec OpenRouter
        
        Args:
            system_prompt: Prompt système
            user_prompt: Prompt utilisateur
        
        Returns:
            Texte généré
        """
        try:
            payload = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            response = self.session.post(
                self.config.base_url,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                logger.info(f"✅ Texte généré avec succès ({len(text)} caractères)")
                return text
            else:
                logger.error(f"❌ Erreur OpenRouter: {response.status_code} - {response.text}")
                return ""
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout OpenRouter ({self.config.timeout}s)")
            return ""
        except Exception as e:
            logger.error(f"❌ Erreur OpenRouter: {e}")
            return ""
    
    def generate_all_posts(self, brief: str, platforms: List[str], tone: str = "professional") -> Dict[str, str]:
        """
        Génère des posts pour plusieurs platforms
        
        Args:
            brief: Description du sujet
            platforms: Liste des platforms (linkedin, twitter)
            tone: Ton des posts
        
        Returns:
            Dictionnaire {platforme: texte}
        """
        posts = {}
        
        if "linkedin" in platforms:
            posts["linkedin"] = self.generate_linkedin_post(brief, tone)
        
        if "twitter" in platforms:
            posts["twitter"] = self.generate_twitter_post(brief)
        
        return posts


# Fonction utilitaire
def create_openrouter_client(api_key: str) -> Optional[OpenRouterClient]:
    """
    Crée un client OpenRouter
    
    Args:
        api_key: Clé API OpenRouter
    
    Returns:
        Instance de OpenRouterClient ou None
    """
    if not api_key:
        logger.error("❌ Clé API OpenRouter non fournie")
        return None
    
    config = OpenRouterConfig(api_key=api_key)
    return OpenRouterClient(config)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY non définie")
        exit(1)
    
    client = create_openrouter_client(api_key)
    
    # Test LinkedIn
    brief = "Nouvelle obligation RGPD pour IA générative"
    linkedin_post = client.generate_linkedin_post(brief)
    print("\n=== POST LINKEDIN ===")
    print(linkedin_post)
    
    # Test Twitter
    twitter_post = client.generate_twitter_post(brief)
    print("\n=== POST TWITTER ===")
    print(twitter_post)
