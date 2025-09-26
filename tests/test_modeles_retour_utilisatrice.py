from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.client_albert import ReponseQuestion, Paragraphe
import pytest


class TestRetourUtilisatrice:
    def test_creation_complet(self):
        retour = RetourUtilisatrice(
            pouce_leve=True, commentaire="Réponse très claire et précise"
        )

        assert retour.pouce_leve is True
        assert retour.commentaire == "Réponse très claire et précise"
        assert retour.horodatage is not None

    def test_creation_pouce_seul(self):
        retour = RetourUtilisatrice(pouce_leve=True)

        assert retour.pouce_leve is True
        assert retour.commentaire is None
        assert retour.horodatage is not None

    def test_creation_commentaire_seul(self):
        retour = RetourUtilisatrice(commentaire="Très utile")

        assert retour.pouce_leve is None
        assert retour.commentaire == "Très utile"
        assert retour.horodatage is not None

    def test_creation_vide_echoue(self):
        with pytest.raises(
            ValueError,
            match="Au moins 'pouce_leve' ou 'commentaire' doit être renseigné",
        ):
            RetourUtilisatrice()

    def test_creation_commentaire_vide_echoue(self):
        with pytest.raises(
            ValueError,
            match="Au moins 'pouce_leve' ou 'commentaire' doit être renseigné",
        ):
            RetourUtilisatrice(commentaire="")

    def test_creation_avec_valeurs_nulles_echoue(self):
        with pytest.raises(
            ValueError,
            match="Au moins 'pouce_leve' ou 'commentaire' doit être renseigné",
        ):
            RetourUtilisatrice(pouce_leve=None, commentaire=None)


class TestInteraction:
    def test_creation_interaction(self):
        paragraphe = Paragraphe(
            score_similarite=0.95,
            numero_page=10,
            url="https://example.com/doc.pdf",
            nom_document="Guide ANSSI",
            contenu="Contenu du paragraphe",
        )

        reponse_question = ReponseQuestion(
            reponse="Il est recommandé d'utiliser au moins 12 caractères.",
            paragraphes=[paragraphe],
            question="Quelle est la longueur recommandée pour un mot de passe ?",
        )

        retour_utilisatrice = RetourUtilisatrice(
            pouce_leve=True, commentaire="Très utile"
        )

        interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=retour_utilisatrice
        )

        assert (
            interaction.reponse_question.question
            == "Quelle est la longueur recommandée pour un mot de passe ?"
        )
        assert interaction.retour_utilisatrice.pouce_leve is True
        assert interaction.retour_utilisatrice.commentaire == "Très utile"

    def test_creation_interaction_sans_retour_utilisatrice(self):
        paragraphe = Paragraphe(
            score_similarite=0.85,
            numero_page=5,
            url="https://example.com/guide.pdf",
            nom_document="Guide sécurité",
            contenu="Contenu du guide",
        )

        reponse_question = ReponseQuestion(
            reponse="Utilisez des mots de passe complexes.",
            paragraphes=[paragraphe],
            question="Comment sécuriser mes mots de passe ?",
        )

        interaction = Interaction(reponse_question=reponse_question)

        assert (
            interaction.reponse_question.question
            == "Comment sécuriser mes mots de passe ?"
        )
        assert interaction.retour_utilisatrice is None
