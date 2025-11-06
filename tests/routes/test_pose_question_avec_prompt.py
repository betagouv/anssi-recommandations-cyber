from fastapi.testclient import TestClient
from serveur import (
    fabrique_serveur,
)

from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from schemas.client_albert import Paragraphe, ReponseQuestion
from configuration import Mode

from serveur_de_test import (
    ConstructeurAdaptateurBaseDeDonnees,
    ConstructeurServiceAlbert,
    ConstructeurServeur,
)


def test_route_pose_question_avec_prompt_repond_correctement_en_developpement() -> None:
    reponse = ReponseQuestion(
        reponse="Réponse de test d'Albert",
        paragraphes=[
            Paragraphe(
                score_similarite=0.75,
                numero_page=29,
                url="https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                nom_document="anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                contenu="Contenu du paragraphe 1",
            )
        ],
        question="Qui es-tu ?",
        violation=None,
    )

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construit()
    )
    serveur = (
        ConstructeurServeur(mode=Mode.DEVELOPPEMENT)
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client: TestClient = TestClient(serveur)
    response = client.post(
        "/api/pose_question_avec_prompt",
        json={
            "question": "Qui es-tu ?",
            "prompt": "Vous êtes un assistant virtuel.",
        },
    )

    assert response.status_code == 200
    service_albert.pose_question.assert_called_once()


def test_route_pose_question_avec_prompt_n_est_pas_exposee_en_production() -> None:
    serveur = fabrique_serveur(Mode.PRODUCTION, fabrique_adaptateur_chiffrement())
    client: TestClient = TestClient(serveur)

    response = client.post(
        "/api/pose_question_avec_prompt",
        json={"question": "Qui es-tu ?", "prompt": "Vous êtes un assistant virtuel."},
    )

    code_attendu = 404

    assert response.status_code == code_attendu
    assert response.json() == {"detail": "Not Found"}
