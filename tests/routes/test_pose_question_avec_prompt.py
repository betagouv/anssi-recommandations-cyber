from fastapi.testclient import TestClient

from configuration import Mode
from schemas.albert import Paragraphe, ReponseQuestion
from serveur_de_test import (
    ConstructeurAdaptateurBaseDeDonnees,
    ConstructeurServiceAlbert,
)


def test_route_pose_question_avec_prompt_repond_correctement_en_developpement(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
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

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        service_albert=service_albert,
    )

    client: TestClient = TestClient(serveur)
    r = client.post(
        "/api/pose_question_avec_prompt",
        json={
            "question": "Qui es-tu ?",
            "prompt": "Vous êtes un assistant virtuel.",
        },
    )

    assert r.status_code == 200
    service_albert.pose_question.assert_called_once()


def test_route_pose_question_avec_prompt_n_est_pas_exposee_en_production(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION, adaptateur_chiffrement=un_adaptateur_de_chiffrement()
    )
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/pose_question_avec_prompt",
        json={"question": "Qui es-tu ?", "prompt": "Vous êtes un assistant virtuel."},
    )

    code_attendu = 404

    assert reponse.status_code == code_attendu
    assert reponse.json() == {"detail": "Not Found"}
