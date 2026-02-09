import os
import uuid

import psycopg2
import pytest

from adaptateurs import (
    AdaptateurBaseDeDonneesEnMemoire,
    AdaptateurBaseDeDonneesPostgres,
)
from configuration import recupere_configuration_postgres
from infra.chiffrement.chiffrement import ServiceDeChiffrementEnClair
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import RetourPositif, TagPositif, Interaction


def cree_connexion_postgres() -> psycopg2.extensions.connection:
    config_postgres = recupere_configuration_postgres("postgres")
    return psycopg2.connect(
        host=config_postgres.hote,
        database=config_postgres.nom,
        user=config_postgres.utilisateur,
        password=config_postgres.mot_de_passe,
        port=config_postgres.port,
    )


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

    adaptateur = AdaptateurBaseDeDonneesPostgres(
        nom_bdd_test, ServiceDeChiffrementEnClair()
    )

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


def test_initialisation_adaptateur_base_de_donnees(adaptateur_test) -> None:
    assert adaptateur_test is not None


def test_ajout_retour_utilisatrice(adaptateur_test) -> None:
    reponse_question = ReponseQuestion(
        reponse="Test réponse",
        paragraphes=[],
        question="Test question",
        violation=None,
    )
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)
    retour = RetourPositif(commentaire="Très utile")
    interaction.retour_utilisatrice = retour

    resultat = adaptateur_test.ajoute_retour_utilisatrice(interaction)
    assert resultat == retour


def test_recupere_interaction_existante(adaptateur_test) -> None:
    reponse_question = ReponseQuestion(
        reponse="Réponse test",
        paragraphes=[],
        question="Question test",
        violation=None,
    )
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)
    interaction_recuperee = adaptateur_test.recupere_interaction(interaction.id)

    assert interaction_recuperee is not None
    assert interaction_recuperee.reponse_question.reponse == "Réponse test"
    assert interaction_recuperee.reponse_question.question == "Question test"
    assert interaction_recuperee.retour_utilisatrice is None


def test_recupere_interaction_avec_retour_utilisatrice(adaptateur_test) -> None:
    reponse_question = ReponseQuestion(
        reponse="Réponse test",
        paragraphes=[],
        question="Question test",
        violation=None,
    )
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)
    id_interaction = interaction.id

    retour = RetourPositif(commentaire="Excellent", tags=[TagPositif.Complete])
    interaction.retour_utilisatrice = retour
    adaptateur_test.ajoute_retour_utilisatrice(interaction)

    interaction = adaptateur_test.recupere_interaction(id_interaction)
    assert interaction is not None
    assert interaction.reponse_question.reponse == "Réponse test"
    assert interaction.retour_utilisatrice is not None
    assert interaction.retour_utilisatrice.commentaire == "Excellent"
    assert interaction.retour_utilisatrice.tags == [TagPositif.Complete]


def test_recupere_interaction_inexistante(adaptateur_test) -> None:
    id_inexistant = "id-inexistant"

    interaction = adaptateur_test.recupere_interaction(id_inexistant)

    assert interaction is None


def test_supprime_retour_existant(adaptateur_test) -> None:
    reponse_question = ReponseQuestion(
        reponse="Réponse test", paragraphes=[], question="Question test", violation=None
    )
    retour = RetourPositif(commentaire="Excellent", tags=[TagPositif.Complete])
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=retour, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)

    adaptateur_test.supprime_retour_utilisatrice(interaction.id)

    interaction_recuperee = adaptateur_test.recupere_interaction(interaction.id)
    assert interaction_recuperee.retour_utilisatrice is None


def test_supprime_retour_inexistant_echoue(adaptateur_test) -> None:
    reponse_question = ReponseQuestion(
        reponse="Réponse test", paragraphes=[], question="Question test", violation=None
    )
    retour = RetourPositif(commentaire="Excellent", tags=[TagPositif.Complete])
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=retour, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)

    retour = adaptateur_test.supprime_retour_utilisatrice("id-d-une-autre-interaction")

    assert retour is None
