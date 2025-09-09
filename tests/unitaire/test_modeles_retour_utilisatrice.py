from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.reponses import ReponseQuestion, Paragraphe
import pytest


def test_creation_retour_utilisatrice_complet():
    retour = RetourUtilisatrice(
        pouce_leve=True, commentaire="Réponse très claire et précise"
    )

    assert retour.pouce_leve is True
    assert retour.commentaire == "Réponse très claire et précise"
    assert retour.horodatage is not None


def test_creation_retour_utilisatrice_pouce_seul():
    retour = RetourUtilisatrice(pouce_leve=True)

    assert retour.pouce_leve is True
    assert retour.commentaire is None
    assert retour.horodatage is not None


def test_creation_retour_utilisatrice_commentaire_seul():
    retour = RetourUtilisatrice(commentaire="Très utile")

    assert retour.pouce_leve is None
    assert retour.commentaire == "Très utile"
    assert retour.horodatage is not None


def test_creation_retour_utilisatrice_vide_echoue():
    with pytest.raises(
        ValueError, match="Au moins 'pouce_leve' ou 'commentaire' doit être renseigné"
    ):
        RetourUtilisatrice()


def test_creation_retour_utilisatrice_commentaire_vide_echoue():
    with pytest.raises(
        ValueError, match="Au moins 'pouce_leve' ou 'commentaire' doit être renseigné"
    ):
        RetourUtilisatrice(commentaire="")


def test_creation_interaction_evaluee():
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

    retour_utilisatrice = RetourUtilisatrice(pouce_leve=True, commentaire="Très utile")

    interaction_evaluee = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=retour_utilisatrice
    )

    assert (
        interaction_evaluee.reponse_question.question
        == "Quelle est la longueur recommandée pour un mot de passe ?"
    )
    assert interaction_evaluee.retour_utilisatrice.pouce_leve is True
    assert interaction_evaluee.retour_utilisatrice.commentaire == "Très utile"
