from fastapi.testclient import TestClient
from unittest.mock import Mock
from main import app, fabrique_client_albert
from client_albert import ClientAlbert


def test_route_sante() -> None:
    """Vérifie que l'application FastAPI fonctionne"""
    client: TestClient = TestClient(app)

    response = client.get("/sante")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_route_recherche() -> None:
    """Vérifie que l'endpoint recherche fonctionne"""
    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.recherche_paragraphes.return_value = "Réponse de test d'Albert"

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/recherche", json={"question": "Ma question test"})

        assert response.status_code == 200
        resultat = response.json()
        assert isinstance(resultat, str)

        mock_client.recherche_paragraphes.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_route_pose_question_repond_correctement() -> None:
    """Vérifie que l'endpoint recherche fonctionne"""
    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = "Réponse de test d'Albert"

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/pose_question", json={"question": "Qui es-tu"})

        assert response.status_code == 200
        mock_client.pose_question.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_route_pose_question_retourne_donnees_correctes() -> None:
    """Vérifie que l'endpoint recherche fonctionne"""
    mock_client: Mock = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = "Réponse de test d'Albert"

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    try:
        client: TestClient = TestClient(app)
        response = client.post("/pose_question", json={"question": "Qui es-tu"})

        resultat = response.json()
        assert isinstance(resultat, str)
        mock_client.pose_question.assert_called_once()
    finally:
        app.dependency_overrides.clear()
