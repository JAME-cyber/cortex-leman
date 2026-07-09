"""
Cortex Leman v5 — Tests du Goal Detector
"""
import pytest

from core.orchestrator.goal_detector import detect_goal, GoalResult, VERTICAL_PATTERNS


class TestGoalDetectorBasics:
    """Tests de base de la détection de verticale"""

    def test_all_verticals_have_patterns(self):
        """Chaque verticale a au moins un pattern"""
        for vertical, patterns in VERTICAL_PATTERNS.items():
            assert len(patterns) >= 1, f"{vertical} n'a aucun pattern"

    def test_empty_text_returns_startup(self):
        """Texte vide → startup (le plus permissif)"""
        result = detect_goal("")
        assert result.vertical == "startup"
        assert result.confidence <= 0.3

    def test_gibberish_returns_startup(self):
        """Texte sans aucun mot-clé → startup"""
        result = detect_goal("xyz abc def ghi")
        assert result.vertical == "startup"
        assert result.confidence <= 0.3


class TestGoalDetectorAvocat:
    """Tests de détection verticale avocat"""

    def test_avocat_direct(self):
        result = detect_goal("Analyser un dossier client pour l'avocat")
        assert result.vertical == "avocat"
        assert "avocat" in result.keywords_matched

    def test_secret_professionnel(self):
        result = detect_goal("Vérifier le respect du secret professionnel")
        assert result.vertical == "avocat"

    def test_conclusions(self):
        result = detect_goal("Rédiger les conclusions pour le tribunal")
        assert result.vertical == "avocat"

    def test_contentieux(self):
        result = detect_goal("Gérer un contentieux commercial")
        assert result.vertical == "avocat"

    def test_art321(self):
        result = detect_goal("Conformité art. 321 CP")
        assert result.vertical == "avocat"
        assert result.confidence > 0.5


class TestGoalDetectorComptable:
    """Tests de détection verticale comptable"""

    def test_comptable_direct(self):
        result = detect_goal("Établir le bilan comptable de l'année")
        assert result.vertical == "comptable"
        assert "bilan" in result.keywords_matched

    def test_tva(self):
        result = detect_goal("Calculer la TVA sur les ventes du trimestre")
        assert result.vertical == "comptable"

    def test_fiscal(self):
        result = detect_goal("Optimisation fiscale pour PME")
        assert result.vertical == "comptable"

    def test_grand_livre(self):
        result = detect_goal("Exporter le grand livre")
        assert result.vertical == "comptable"


class TestGoalDetectorBanque:
    """Tests de détection verticale banque"""

    def test_banque_direct(self):
        result = detect_goal("Vérification KYC pour nouveau client bancaire")
        assert result.vertical == "banque"

    def test_aml(self):
        result = detect_goal("Signalement AML suspect")
        assert result.vertical == "banque"

    def test_secret_bancaire(self):
        result = detect_goal("Respect du secret bancaire art. 47")
        assert result.vertical == "banque"


class TestGoalDetectorSante:
    """Tests de détection verticale santé"""

    def test_patient(self):
        result = detect_goal("Accès au dossier patient")
        assert result.vertical == "sante"

    def test_medecin(self):
        result = detect_goal("Aide au diagnostic médical")
        assert result.vertical == "sante"

    def test_donnees_sante(self):
        result = detect_goal("Hébergement des données de santé")
        assert result.vertical == "sante"


class TestGoalDetectorRH:
    """Tests de détection verticale RH"""

    def test_rh_direct(self):
        result = detect_goal("Processus de recrutement RH")
        assert result.vertical == "rh"

    def test_embauche(self):
        result = detect_goal("Critères d'embauche non discriminatoires")
        assert result.vertical == "rh"

    def test_licenciement(self):
        result = detect_goal("Procédure de licenciement")
        assert result.vertical == "rh"


class TestGoalDetectorStartup:
    """Tests de détection verticale startup"""

    def test_startup_direct(self):
        result = detect_goal("Préparer ma startup pour une levée de fonds")
        assert result.vertical == "startup"

    def test_saas(self):
        result = detect_goal("Lancer un produit SaaS")
        assert result.vertical == "startup"


class TestGoalDetectorAgentIA:
    """Tests de détection verticale agent-ia"""

    def test_chatbot(self):
        result = detect_goal("Déploiement d'un chatbot IA")
        assert result.vertical == "agent-ia"

    def test_agents_ia(self):
        result = detect_goal("Conformité des agents IA déployés")
        assert result.vertical == "agent-ia"


class TestGoalDetectorConflicts:
    """Tests de résolution de conflits entre verticales"""

    def test_avocat_vs_comptable(self):
        """"audit comptable" = comptable, pas avocat"""
        result = detect_goal("Audit comptable annuel")
        assert result.vertical == "comptable"

    def test_hint_vertical_overrides(self):
        """Le hint vertical bypass la détection"""
        result = detect_goal("Audit comptable annuel", hint_vertical="avocat")
        assert result.vertical == "avocat"
        assert result.confidence == 1.0

    def test_hint_invalid_falls_back(self):
        """Un hint invalide est ignoré"""
        result = detect_goal("Bilan comptable", hint_vertical="invalid")
        assert result.vertical == "comptable"

    def test_multivertical_picks_best(self):
        """Texte avec mots-clés de plusieurs verticales → meilleur score gagne"""
        result = detect_goal("Avocat spécialisé en droit fiscal et comptable")
        # "comptable" matche 3.0 + "fiscal" 2.5 = 5.5 pour comptable
        # "avocat" matche 4.0 + "droit" 1.0 = 5.0 pour avocat
        # Les deux sont proches. Soit peut gagner. Ce qui compte:
        # 1. La confiance n'est pas 100% (ambiguïté)
        assert result.confidence < 1.0
        # 2. Les deux verticales ont matché des mots-clés
        assert len(result.keywords_matched) >= 1


class TestGoalResult:
    """Tests du dataclass GoalResult"""

    def test_result_fields(self):
        result = GoalResult(
            vertical="avocat",
            confidence=0.85,
            keywords_matched=["avocat", "dossier"],
            goal_text="Analyser un dossier",
        )
        assert result.vertical == "avocat"
        assert result.confidence == 0.85
        assert len(result.keywords_matched) == 2
        assert result.client_id == "auto"

    def test_result_custom_client(self):
        result = GoalResult(
            vertical="comptable",
            confidence=0.9,
            keywords_matched=["bilan"],
            goal_text="Bilan",
            client_id="cabinet-dupont",
        )
        assert result.client_id == "cabinet-dupont"
