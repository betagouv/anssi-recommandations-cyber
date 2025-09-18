from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import (
    app,
    fabrique_client_albert,
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from client_albert import ClientAlbert
from schemas.reponses import ReponseQuestion
from adaptateurs import AdaptateurBaseDeDonnees


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

    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.sauvegarde_interaction.return_value = "id-interaction-test"

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    with patch("main.recupere_configuration") as mock_conf:
        mock_conf.return_value = {
            "NOM_BDD": "test",
        }

        try:
            client: TestClient = TestClient(app)
            response = client.post("/pose_question", json={"question": "Qui es-tu"})

            assert response.status_code == 200
            mock_client.pose_question.assert_called_once()

        finally:
            app.dependency_overrides.clear()


def test_route_pose_question_retourne_donnees_correctes() -> None:
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

    mock_client = Mock(spec=ClientAlbert)
    mock_client.pose_question.return_value = mock_reponse

    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.sauvegarde_interaction.return_value = "id-interaction-test"

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    with patch("main.recupere_configuration") as mock_conf:
        mock_conf.return_value = {
            "NOM_BDD": "test",
        }

        try:
            client_http = TestClient(app)
            response = client_http.post(
                "/pose_question", json={"question": "Qui es-tu"}
            )
            resultat = response.json()

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
            mock_adaptateur.sauvegarde_interaction.assert_called_once()
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


def test_route_retour_avec_mock_retourne_succes_200():
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.ajoute_retour_utilisatrice.return_value = True

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload = {
            "id_interaction_rattachee": "id-123",
            "retour": {
                "pouce_leve": True,
                "commentaire": "Très utile",
            },
        }
        reponse = client.post("/retour", json=payload)

        assert reponse.status_code == 200
        mock_adaptateur.ajoute_retour_utilisatrice.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_route_retour_avec_mock_retourne_donnees_attendues():
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.ajoute_retour_utilisatrice.return_value = True

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload = {
            "id_interaction_rattachee": "id-123",
            "retour": {
                "pouce_leve": True,
                "commentaire": "Très utile !",
            },
        }

        reponse = client.post("/retour", json=payload)
        data = reponse.json()

        assert data["succes"] is True
        assert data["commentaire"] == "Très utile !"
        args, _ = mock_adaptateur.ajoute_retour_utilisatrice.call_args
    finally:
        app.dependency_overrides.clear()


def test_route_retour_avec_interaction_inexistante_retourne_404():
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.ajoute_retour_utilisatrice.return_value = False

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload = {
            "id_interaction_rattachee": "id-123",
            "retour": {
                "pouce_leve": True,
                "commentaire": "Très utile",
            },
        }

        resp = client.post("/retour", json=payload)

        assert resp.status_code == 404
        assert resp.json() == {"detail": "Interaction non trouvée"}

        mock_adaptateur.ajoute_retour_utilisatrice.assert_called_once()

    finally:
        app.dependency_overrides.clear()


def test_route_retour_avec_payload_invalide_rejette_la_requete():
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload = {
            "id": 23,
            "retour": {
                "pouce_leve": True,
                "commentaire": "Très utile",
            },
        }
        resp = client.post("/retour", json=payload)

        assert resp.status_code == 422
        mock_adaptateur.ajoute_retour_utilisatrice.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_pose_question_retourne_id_dans_body():
    reponse = ReponseQuestion(reponse="ok", paragraphes=[], question="Q?")
    mock_client = Mock()
    mock_client.pose_question.return_value = reponse
    mock_db = Mock(spec=AdaptateurBaseDeDonnees)
    mock_db.sauvegarde_interaction.return_value = "id-123"

    app.dependency_overrides[fabrique_client_albert] = lambda: mock_client
    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_db
    try:
        client = TestClient(app)
        r = client.post("/pose_question", json={"question": "Q?"})
        j = r.json()
        assert r.status_code == 200
        assert j["reponse"] == "ok"
        assert j["interaction_id"] == "id-123"
    finally:
        app.dependency_overrides.clear()
