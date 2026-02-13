import uuid

from schemas.retour_utilisatrice import (
    RetourNegatif,
    RetourPositif,
    RetourUtilisatrice,
    TagNegatif,
    TagPositif,
)
from conversation.conversation import Interaction
from schemas.albert import ReponseQuestion, Paragraphe
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

    def test_retour_utilisatrice_negatif_peut_avoir_des_tags(self) -> None:
        commentaire = "c'est pas terrible..."
        tags = [TagNegatif.TropComplexe, TagNegatif.SourcesPeuUtiles]
        retour = RetourNegatif(commentaire=commentaire, tags=tags)

        assert retour.tags == tags

    def test_retour_utilisatrice_positif_peut_avoir_des_tags(self) -> None:
        commentaire = "c'est super !"
        tags = [TagPositif.FacileAComprendre, TagPositif.Complete]
        retour = RetourPositif(commentaire=commentaire, tags=tags)

        assert retour.tags == tags

    def test_retour_utilisatrice_negatif_sans_tags_a_des_tags_vide_par_default(
        self,
    ) -> None:
        retour = RetourNegatif(commentaire="c'est pas terrible...")
        assert retour.tags == []

    def test_retour_utilisatrice_positif_sans_tags_a_des_tags_vide_par_default(
        self,
    ) -> None:
        retour = RetourPositif(commentaire="c'est super !")
        assert retour.tags == []


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
            violation=None,
        )

        retour_utilisatrice = RetourPositif(
            commentaire="Très utile", tags=[TagPositif.FacileAComprendre]
        )

        interaction = Interaction(
            reponse_question=reponse_question,
            retour_utilisatrice=retour_utilisatrice,
            id=uuid.uuid4(),
        )

        assert (
            interaction.reponse_question.question
            == "Quelle est la longueur recommandée pour un mot de passe ?"
        )
        assert interaction.retour_utilisatrice is not None
        assert interaction.retour_utilisatrice.commentaire == "Très utile"
        assert interaction.retour_utilisatrice.tags == [TagPositif.FacileAComprendre]

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
            violation=None,
        )

        interaction = Interaction(reponse_question=reponse_question, id=uuid.uuid4())

        assert (
            interaction.reponse_question.question
            == "Comment sécuriser mes mots de passe ?"
        )
        assert interaction.retour_utilisatrice is None
