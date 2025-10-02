from schemas.retour_utilisatrice import (
    RetourNegatif,
    RetourPositif,
    RetourUtilisatrice,
    Interaction,
)
from schemas.client_albert import ReponseQuestion, Paragraphe
import pytest


class TestRetourUtilisatrice:
    def test_creation_retour_negatif_sans_commentaire_est_horodate(self) -> None:
        retour = RetourPositif()
        assert retour.horodatage is not None

    def test_creation_retour_positif_sans_commentaire_est_horodate(self) -> None:
        retour = RetourPositif()
        assert retour.horodatage is not None

    def test_creation_retour_negatif_avec_commentaire_contient_commentaire_et_est_horodate(
        self,
    ) -> None:
        commentaire = "c'est pas terrible..."
        retour = RetourNegatif(commentaire=commentaire)

        assert retour.commentaire == commentaire
        assert retour.horodatage is not None

    def test_creation_retour_positif_avec_commentaire_contient_commentaire_et_est_horodate(
        self,
    ) -> None:
        commentaire = "c'est super !"
        retour = RetourPositif(commentaire=commentaire)

        assert retour.commentaire == commentaire
        assert retour.horodatage is not None

    def test_creation_retour_utilisatrice_directement_echoue(self) -> None:
        with pytest.raises(TypeError):
            RetourUtilisatrice()  # type: ignore [operator]


class TestInteraction:
    def test_creation_interaction(self) -> None:
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

        retour_utilisatrice = RetourPositif(commentaire="Très utile")

        interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=retour_utilisatrice
        )

        assert (
            interaction.reponse_question.question
            == "Quelle est la longueur recommandée pour un mot de passe ?"
        )
        assert interaction.retour_utilisatrice is not None
        assert interaction.retour_utilisatrice.commentaire == "Très utile"

    def test_creation_interaction_sans_retour_utilisatrice(self) -> None:
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
