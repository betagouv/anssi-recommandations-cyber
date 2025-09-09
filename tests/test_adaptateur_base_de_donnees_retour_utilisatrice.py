import uuid
import psycopg2
import pytest
from adaptateur_base_de_donnees import AdaptateurBaseDeDonnees
from schemas.retour_utilisatrice import RetourUtilisatrice
from schemas.reponses import ReponseQuestion, Paragraphe


@pytest.fixture
def adaptateur_test():
    HOTE_BD_TEST: str = "localhost"
    PORT_BD_TEST: int = 5432
    UTILISATEUR_BD_TEST: str = "postgres"
    MOT_DE_PASSE_BD_TEST: str = "password"
    NOM_BD_TEST: str = f"test_anssi_{str(uuid.uuid4()).replace('-', '_')}"
    conn_admin = psycopg2.connect(
        host=HOTE_BD_TEST,
        database="postgres",
        user=UTILISATEUR_BD_TEST,
        password=MOT_DE_PASSE_BD_TEST,
        port=PORT_BD_TEST,
    )
    conn_admin.autocommit = True

    with conn_admin.cursor() as cursor:
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{NOM_BD_TEST}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {NOM_BD_TEST}")
    conn_admin.close()

    adaptateur = AdaptateurBaseDeDonnees(NOM_BD_TEST)

    yield adaptateur

    adaptateur.ferme_connexion()

    conn_cleanup = psycopg2.connect(
        host=HOTE_BD_TEST,
        database="postgres",
        user=UTILISATEUR_BD_TEST,
        password=MOT_DE_PASSE_BD_TEST,
        port=PORT_BD_TEST,
    )
    conn_cleanup.autocommit = True

    with conn_cleanup.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS {NOM_BD_TEST}")
    conn_cleanup.close()


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
