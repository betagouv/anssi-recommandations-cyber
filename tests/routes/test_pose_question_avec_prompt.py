from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from serveur import (
    fabrique_serveur,
)

from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from client_albert import ClientAlbert, fabrique_client_albert
from schemas.reponses import ReponseQuestion
from adaptateurs import AdaptateurBaseDeDonnees
from configuration import Mode


def test_route_pose_question_repond_correctement_en_developpement() -> None:
    serveur = fabrique_serveur(Mode.DEVELOPPEMENT)

    mock_reponse = ReponseQuestion(
        reponse="Réponse de test d'Albert",
        paragraphes=[
            {
                "score_similarite": 0.75,
                "numero_page": 29,
                "url": "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "nom_document": "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "contenu": "Contenu du paragraphe 1",
            }
        ],
        question="Qui es-tu ?",
    )

    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = mock_reponse

    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.sauvegarde_interaction.return_value = "id-interaction-test"

    serveur.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    serveur.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    with patch("main.recupere_configuration") as mock_conf:
        mock_conf.return_value = {
            "NOM_BDD": "test",
        }

        try:
            client: TestClient = TestClient(serveur)
            response = client.post(
                "/pose_question_avec_prompt",
                json={
                    "question": "Qui es-tu ?",
                    "prompt": "Vous êtes un assistant virtuel.",
                },
            )

            assert response.status_code == 200
            mock_client.pose_question.assert_called_once()

        finally:
            serveur.dependency_overrides.clear()


def test_route_pose_question_avec_prompt_n_est_pas_exposee_en_production():
    serveur = fabrique_serveur(Mode.PRODUCTION)
    client: TestClient = TestClient(serveur)

    response = client.post(
        "/pose_question_avec_prompt",
        json={"question": "Qui es-tu ?", "prompt": "Vous êtes un assistant virtuel."},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
