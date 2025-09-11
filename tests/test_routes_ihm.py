from datetime import datetime, timedelta, UTC
import jwt
import pytest
from fastapi.testclient import TestClient
import main
from main import (
    app,
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
    fabrique_client_albert,
)
from adaptateurs import AdaptateurBaseDeDonnees
from schemas.reponses import ReponseQuestion
from client_albert import ClientAlbert
from unittest.mock import Mock

TEST_JWT_SECRET = "secret-de-test"


@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    def conf_fictive():
        return {
            "NOM_BDD": "test",
            "JWT_CLE_SECRETE": TEST_JWT_SECRET,
            "JWT_HEURE_EXPIRATION": 1,
            "JWT_COOKIES_SECURISE": False,
        }

    monkeypatch.setattr(main, "recupere_configuration", conf_fictive)
    yield


@pytest.fixture
def client_http():
    return TestClient(app)


@pytest.fixture
def adaptateur_bdd_mock():
    mock = Mock(spec=AdaptateurBaseDeDonnees)
    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


def _cookie_jwt(interaction_id: str) -> dict:
    token = jwt.encode(
        {
            "interaction_id": interaction_id,
            "exp": datetime.now(UTC) + timedelta(hours=24),
        },
        TEST_JWT_SECRET,
        algorithm="HS256",
    )
    return {"interaction_token": token}


def test_route_retour_avec_mock_retourne_succes_200(client_http, adaptateur_bdd_mock):
    adaptateur_bdd_mock.ajoute_retour_utilisatrice.return_value = True
    payload = {"pouce_leve": True, "commentaire": "Très utile !"}
    cookies = _cookie_jwt("uuid-test-123")

    reponse = client_http.post("/retour", json=payload, cookies=cookies)

    assert reponse.status_code == 200
    adaptateur_bdd_mock.ajoute_retour_utilisatrice.assert_called_once()


def test_route_retour_avec_mock_retourne_donnees_attendues(
    client_http, adaptateur_bdd_mock
):
    adaptateur_bdd_mock.ajoute_retour_utilisatrice.return_value = True
    payload = {"pouce_leve": True, "commentaire": "Très utile !"}
    cookies = _cookie_jwt("uuid-test-456")

    reponse = client_http.post("/retour", json=payload, cookies=cookies)
    data = reponse.json()

    assert data["succes"] is True
    assert data["commentaire"] == "Très utile !"
    args, _ = adaptateur_bdd_mock.ajoute_retour_utilisatrice.call_args
    assert args[0] == "uuid-test-456"


def test_route_retour_avec_interaction_inexistante_retourne_404(
    client_http, adaptateur_bdd_mock
):
    adaptateur_bdd_mock.ajoute_retour_utilisatrice.return_value = False
    payload = {"pouce_leve": True, "commentaire": "N/A"}
    cookies = _cookie_jwt("uuid-inexistant-123")

    resp = client_http.post("/retour", json=payload, cookies=cookies)

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Interaction non trouvée"}
    adaptateur_bdd_mock.ajoute_retour_utilisatrice.assert_called_once()


def test_route_retour_avec_payload_invalide_rejette_la_requete(
    client_http, adaptateur_bdd_mock
):
    cookies = _cookie_jwt("uuid-test-422")
    payload_invalide = {"pouce_leve": "oui", "commentaire": 123}

    resp = client_http.post("/retour", json=payload_invalide, cookies=cookies)

    assert resp.status_code == 422
    adaptateur_bdd_mock.ajoute_retour_utilisatrice.assert_not_called()


def test_route_pose_question_retourne_donnees_correctes(
    client_http, adaptateur_bdd_mock
) -> None:
    reponse_simulee = ReponseQuestion(
        reponse="Réponse de test d'Albert",
        paragraphes=[
            {
                "score_similarite": 0.75,
                "numero_page": 29,
                "url": "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "nom_document": "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "contenu": "Contenu du paragraphe 1",
            },
            {
                "score_similarite": 0.72,
                "numero_page": 15,
                "url": "https://cyber.gouv.fr/sites/default/files/2017/01/guide_hygiene_informatique_anssi.pdf",
                "nom_document": "guide_hygiene_informatique_anssi.pdf",
                "contenu": "Contenu du paragraphe 2",
            },
        ],
        question="Qui es-tu",
    )

    mock_client = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = reponse_simulee
    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client

    adaptateur_bdd_mock.sauvegarde_interaction.return_value = "id-interaction-test"

    reponse = client_http.post("/pose_question", json={"question": "Qui es-tu"})
    resultat = reponse.json()

    assert reponse.status_code == 200
    assert "reponse" in resultat
    assert "paragraphes" in resultat
    assert "question" in resultat
    assert resultat["reponse"] == "Réponse de test d'Albert"
    assert isinstance(resultat["paragraphes"], list)
    assert len(resultat["paragraphes"]) == 2

    p1 = resultat["paragraphes"][0]
    assert p1["score_similarite"] == 0.75
    assert p1["numero_page"] == 29
    assert (
        p1["url"]
        == "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
    )
    assert (
        p1["nom_document"]
        == "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
    )
    assert p1["contenu"] == "Contenu du paragraphe 1"
    assert resultat["question"] == "Qui es-tu"

    mock_client.pose_question.assert_called_once()
    adaptateur_bdd_mock.sauvegarde_interaction.assert_called_once()


def test_route_pose_question_repond_correctement(
    client_http, adaptateur_bdd_mock
) -> None:
    reponse_simulee = ReponseQuestion(
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
        question="Qui es-tu",
    )

    mock_client = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = reponse_simulee
    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client

    adaptateur_bdd_mock.sauvegarde_interaction.return_value = "id-interaction-test"

    response = client_http.post("/pose_question", json={"question": "Qui es-tu"})

    assert response.status_code == 200
    mock_client.pose_question.assert_called_once()
    adaptateur_bdd_mock.sauvegarde_interaction.assert_called_once()
