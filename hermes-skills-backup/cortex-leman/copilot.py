def generate_personalized_post(brief, client_name, context=""):
    """
    Génère un post personnalisé pour un client, avec contexte arXiv
    
    Args:
        brief: Brief principal
        client_name: Nom du client (ex: "Innovatech")
        context: Contexte arXiv (optionnel)
    
    Returns:
        Prompt enrichi
    """
    enhanced_brief = f""
    {context}

    --- BRIEF ---
    Réel client : {client_name}
    {brief}

    Style : Professionnel, humain, engageant, avec 5-7 hashtags.
    Message final : \"Pourquoi vous devriez le savoir : [lien]\".
    ""
    return enhanced_brief

# Exemple d'usage
if __name__ == "__main__":
    context = "# Derniers papiers arXiv (last 7 days)\n## Mise à jour: 2026-04-14 10:00\n\n### [\"AI Regulation 2026: Key Risks for Enterprises\"](https://arxiv.org/pdf/2407.12345.pdf)\n**Publié:** 2026-04-10\n**Résumé:** New draft proposes binding rules for generative AI in EU.""
    
    prompt = generate_personalized_post(
        brief="Nouvelle régulation IA pour les PME",
        client_name="Innovatech",
        context=context
    )
    
    print(prompt)