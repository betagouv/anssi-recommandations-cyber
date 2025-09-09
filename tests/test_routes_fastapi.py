from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app, fabrique_client_albert
from client_albert import ClientAlbert
from schemas.reponses import ReponseQuestion


def test_route_sante() -> None:
    """Vérifie que l'application FastAPI fonctionne"""
    client: TestClient = TestClient(app)

    response = client.get("/sante")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_route_recherche_repond_correctement() -> None:
    """Vérifie que l'endpoint recherche fonctionne"""
    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.recherche_paragraphes.return_value = {"paragraphes": []}

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/recherche", json={"question": "Ma question test"})

        assert response.status_code == 200
        mock_client.recherche_paragraphes.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_route_recherche_donnees_correctes() -> None:
    """Vérifie que l'endpoint recherche fonctionne"""
    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.recherche_paragraphes.return_value = {"paragraphes": []}

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/recherche", json={"question": "Ma question test"})
        resultat = response.json()
        assert isinstance(resultat, dict)
        assert "paragraphes" in resultat

        mock_client.recherche_paragraphes.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_route_pose_question_repond_correctement() -> None:
    """Vérifie que l'endpoint recherche fonctionne"""
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
        question="Qui es-tu",
    )

    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = mock_reponse

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/pose_question", json={"question": "Qui es-tu"})

        assert response.status_code == 200
        mock_client.pose_question.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_route_pose_question_retourne_donnees_correctes() -> None:
    """Vérifie que l'endpoint retourne un objet ReponseQuestion avec paragraphes structurés"""

    mock_reponse = ReponseQuestion(
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

    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = mock_reponse

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/pose_question", json={"question": "Qui es-tu"})
        resultat = response.json()

        # Vérifier la structure ReponseQuestion avec paragraphes structurés
        assert "reponse" in resultat
        assert "paragraphes" in resultat
        assert "question" in resultat
        assert resultat["reponse"] == "Réponse de test d'Albert"
        assert isinstance(resultat["paragraphes"], list)
        assert len(resultat["paragraphes"]) == 2

        # Vérifier le premier paragraphe
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
    finally:
        app.dependency_overrides.clear()


def test_route_recherche_retourne_la_bonne_structure_d_objet() -> None:
    """Vérifie que l'endpoint recherche retourne toutes les métadonnées pour chaque paragraphe"""
    mock_result = {
        "paragraphes": [
            {
                "content": "Contenu du paragraphe 1",
                "source_url": "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "score": 0.75,
                "page": 29,
                "document_name": "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
            },
        ]
    }

    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.recherche_paragraphes.return_value = mock_result

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/recherche", json={"question": "Ma question test"})

        resultat = response.json()
        assert "paragraphes" in resultat
        assert len(resultat["paragraphes"]) == 1
        p1 = resultat["paragraphes"][0]
        assert p1["content"] == "Contenu du paragraphe 1"
        assert (
            p1["source_url"]
            == "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
        )
        assert p1["score"] == 0.75
        assert p1["page"] == 29
        assert (
            p1["document_name"]
            == "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
        )

        mock_client.recherche_paragraphes.assert_called_once()
    finally:
        app.dependency_overrides.clear()
