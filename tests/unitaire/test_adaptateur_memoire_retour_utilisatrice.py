import pytest
from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from schemas.retour_utilisatrice import RetourUtilisatrice
from schemas.reponses import ReponseQuestion, Paragraphe


@pytest.fixture
def adaptateur_test():
    return AdaptateurBaseDeDonneesEnMemoire()


def test_initialisation_adaptateur_base_de_donnees(adaptateur_test):
    assert adaptateur_test is not None


def test_sauvegarde_interaction(adaptateur_test):
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

    id_interaction = adaptateur_test.sauvegarde_interaction(reponse_question)

    assert id_interaction is not None
    assert isinstance(id_interaction, str)


def test_ajout_retour_utilisatrice(adaptateur_test):
    reponse_question = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )
    id_interaction = adaptateur_test.sauvegarde_interaction(reponse_question)

    retour = RetourUtilisatrice(pouce_leve=True, commentaire="Très utile")

    resultat = adaptateur_test.ajoute_retour_utilisatrice(id_interaction, retour)
    assert resultat is True


def test_recuperation_statistiques(adaptateur_test):
    reponse1 = ReponseQuestion(
        reponse="Réponse 1", paragraphes=[], question="Question 1"
    )
    reponse2 = ReponseQuestion(
        reponse="Réponse 2", paragraphes=[], question="Question 2"
    )

    id1 = adaptateur_test.sauvegarde_interaction(reponse1)
    id2 = adaptateur_test.sauvegarde_interaction(reponse2)

    adaptateur_test.ajoute_retour_utilisatrice(id1, RetourUtilisatrice(pouce_leve=True))
    adaptateur_test.ajoute_retour_utilisatrice(
        id2, RetourUtilisatrice(pouce_leve=False)
    )

    stats = adaptateur_test.obtient_statistiques()

    assert "total_interactions" in stats
    assert "total_retours" in stats
    assert "pouces_leves" in stats
    assert stats["total_interactions"] == 2
    assert stats["total_retours"] == 2
    assert stats["pouces_leves"] == 1