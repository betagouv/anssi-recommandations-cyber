from unittest.mock import Mock
import pytest
from main import route_pose_question
from schemas.requetes import QuestionRequete
from schemas.reponses import ReponseQuestion
from adaptateurs import AdaptateurBaseDeDonnees
from client_albert import ClientAlbert
from tests.integration.test_adaptateur_postgres_retour_utilisatrice import (
    adaptateur_test,
)


@pytest.mark.integration
def test_route_pose_question_avec_objet_gestionnaire_en_parametre_retoure_la_reponse():
    mock_client_albert = Mock(spec=ClientAlbert)
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)

    reponse_attendue = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )
    mock_client_albert.pose_question.return_value = reponse_attendue
    mock_adaptateur.sauvegarde_interaction.return_value = "test-id-123"

    requete = QuestionRequete(question="Test question")

    resultat = route_pose_question(requete, mock_client_albert, mock_adaptateur)

    assert resultat == reponse_attendue
    mock_client_albert.pose_question.assert_called_once_with("Test question")
    mock_adaptateur.sauvegarde_interaction.assert_called_once_with(reponse_attendue)


@pytest.mark.integration
def test_route_pose_question_sauvegarde_interaction(adaptateur_test):
    mock_client_albert = Mock(spec=ClientAlbert)

    reponse_attendue = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )
    mock_client_albert.pose_question.return_value = reponse_attendue

    requete = QuestionRequete(question="Test question")

    _ = route_pose_question(requete, mock_client_albert, adaptateur_test)

    stats = adaptateur_test.obtient_statistiques()
    assert stats["total_interactions"] == 1
    assert stats["total_retours"] == 0


@pytest.mark.integration
def test_gestionnaire_lit_interactions_sauvegardees(adaptateur_test):
    gestionnaire = adaptateur_test

    reponse_question = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )

    id_interaction = gestionnaire.sauvegarde_interaction(reponse_question)

    interaction_lue = gestionnaire.lit_interaction(id_interaction)

    assert interaction_lue is not None
    assert interaction_lue.reponse_question.question == "Test question"
    assert interaction_lue.reponse_question.reponse == "Test réponse"
    assert interaction_lue.retour_utilisatrice is None
