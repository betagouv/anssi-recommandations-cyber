import os
import uuid
import pytest
import psycopg2
from adaptateurs import (
    AdaptateurBaseDeDonneesEnMemoire,
    AdaptateurBaseDeDonneesPostgres,
)
from schemas.retour_utilisatrice import RetourUtilisatrice
from schemas.reponses import ReponseQuestion, Paragraphe
from config import recupere_configuration_postgres


def cree_connexion_postgres() -> psycopg2.extensions.connection:
    return psycopg2.connect(**recupere_configuration_postgres("postgres"))


def cree_adaptateur_memoire():
    yield AdaptateurBaseDeDonneesEnMemoire()


def cree_adaptateur_postgres():
    nom_bdd_test = f"test_anssi_{str(uuid.uuid4()).replace('-', '_')}"

    conn_admin = cree_connexion_postgres()
    conn_admin.autocommit = True
    with conn_admin.cursor() as cursor:
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{nom_bdd_test}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {nom_bdd_test}")
    conn_admin.close()

    adaptateur = AdaptateurBaseDeDonneesPostgres(nom_bdd_test)

    yield adaptateur

    adaptateur.ferme_connexion()
    conn_cleanup = cree_connexion_postgres()
    conn_cleanup.autocommit = True
    with conn_cleanup.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS {nom_bdd_test}")
    conn_cleanup.close()


def obtient_adaptateurs():
    return [cree_adaptateur_memoire] + (
        [] if os.getenv("CI") else [cree_adaptateur_postgres]
    )


@pytest.fixture(params=obtient_adaptateurs())
def adaptateur_test(request):
    yield from request.param()


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


def test_recuperation_statistiques_sans_retour_utilisateur(adaptateur_test):
    reponse1 = ReponseQuestion(
        reponse="Réponse 1", paragraphes=[], question="Question 1"
    )

    adaptateur_test.sauvegarde_interaction(reponse1)

    stats = adaptateur_test.obtient_statistiques()

    assert stats["total_interactions"] == 1
    assert stats["total_retours"] == 0
    assert stats["pouces_leves"] == 0
