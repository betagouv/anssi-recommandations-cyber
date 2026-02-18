import datetime as dt
import os
import uuid

import psycopg2
import pytest

from adaptateurs import (
    AdaptateurBaseDeDonneesEnMemoire,
    AdaptateurBaseDeDonneesPostgres,
)
from adaptateurs.connecteur import ConnecteurPostgresql
from adaptateurs.horloge import Horloge
from adaptateurs.migrateur import Migrateur
from configuration import recupere_configuration_postgres, BaseDeDonnees
from infra.chiffrement.chiffrement import ServiceDeChiffrementEnClair
from schemas.retour_utilisatrice import (
    RetourPositif,
    TagPositif,
    Interaction,
    Conversation,
)


def cree_connexion_postgres(postgres) -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=postgres.hote,
        database=postgres.nom,
        user=postgres.utilisateur,
        password=postgres.mot_de_passe,
        port=postgres.port,
    )


def cree_adaptateur_memoire():
    yield AdaptateurBaseDeDonneesEnMemoire()


def cree_adaptateur_postgres():
    nom_bdd_test = f"test_anssi_{str(uuid.uuid4()).replace('-', '_')}"
    configuration_postgres = recupere_configuration_postgres("postgres")
    connecteur_postgresql = ConnecteurPostgresql(configuration_postgres)
    connecteur_postgresql.auto_commit()
    with connecteur_postgresql.cursor() as cursor:
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{nom_bdd_test}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {nom_bdd_test}")
    connecteur_postgresql.close()

    connecteur_migration = ConnecteurPostgresql(
        BaseDeDonnees(
            hote=configuration_postgres.hote,
            nom=nom_bdd_test,
            utilisateur=configuration_postgres.utilisateur,
            mot_de_passe=configuration_postgres.mot_de_passe,
            port=configuration_postgres.port,
        )
    )
    migrateur = Migrateur(connecteur_migration, "migrations")
    migrateur.execute_migrations()
    connecteur_migration.close()
    adaptateur = AdaptateurBaseDeDonneesPostgres(
        nom_bdd_test, ServiceDeChiffrementEnClair()
    )

    yield adaptateur

    adaptateur.ferme_connexion()
    conn_cleanup = ConnecteurPostgresql(configuration_postgres)
    conn_cleanup.auto_commit()
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


def test_ajout_retour_utilisatrice(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("Test réponse")
        .avec_une_question("Test question")
        .construis()
    )
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)
    retour = RetourPositif(commentaire="Très utile")
    interaction.retour_utilisatrice = retour

    adaptateur_test.sauvegarde_interaction(interaction)

    resultat = adaptateur_test.recupere_interaction(interaction.id)
    assert resultat.retour_utilisatrice == retour


def test_recupere_interaction_existante(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("Réponse test")
        .avec_une_question("Question test")
        .construis()
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


def test_recupere_interaction_avec_retour_utilisatrice(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("Réponse test")
        .avec_une_question("Question test")
        .construis()
    )

    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)
    id_interaction = interaction.id

    retour = RetourPositif(commentaire="Excellent", tags=[TagPositif.Complete])
    interaction.retour_utilisatrice = retour
    adaptateur_test.sauvegarde_interaction(interaction)

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


def test_supprime_retour_existant(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("Réponse test")
        .avec_une_question("Question test")
        .construis()
    )
    retour = RetourPositif(commentaire="Excellent", tags=[TagPositif.Complete])
    interaction = Interaction(
        reponse_question=reponse_question, retour_utilisatrice=retour, id=uuid.uuid4()
    )
    adaptateur_test.sauvegarde_interaction(interaction)

    interaction.retour_utilisatrice = None
    adaptateur_test.sauvegarde_interaction(interaction)

    interaction_recuperee = adaptateur_test.recupere_interaction(interaction.id)
    assert interaction_recuperee.retour_utilisatrice is None


def test_la_date_d_une_interaction_est_persistee(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    date_creation = dt.datetime(2026, 2, 15, 3, 4, 5)
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("test")
        .avec_une_question("test")
        .construis()
    )
    Horloge.frise(date_creation)
    interaction = Interaction(id=uuid.uuid4(), reponse_question=reponse_question)

    adaptateur_test.sauvegarde_interaction(interaction)
    Horloge.frise(dt.datetime(2026, 6, 7, 3, 4, 6))

    interaction_recuperee = adaptateur_test.recupere_interaction(interaction.id)
    assert interaction_recuperee.date_creation == interaction.date_creation


def test_persiste_une_conversation(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("test")
        .avec_une_question("test")
        .construis()
    )
    conversation = Conversation(
        Interaction(
            id=uuid.uuid4(),
            reponse_question=reponse_question,
        )
    )

    adaptateur_test.sauvegarde_conversation(conversation)

    conversation_recuperee = adaptateur_test.recupere_conversation(
        conversation.id_conversation
    )
    assert conversation_recuperee is not None
    assert conversation_recuperee.__dict__ == conversation.__dict__


def test_persiste_une_conversation_avec_toutes_ses_interactions(
    adaptateur_test, un_constructeur_de_reponse_question
) -> None:
    conversation = Conversation(
        Interaction(
            id=uuid.uuid4(),
            reponse_question=(
                un_constructeur_de_reponse_question()
                .donnant_en_reponse("réponse 1")
                .avec_une_question("question 1")
                .construis()
            ),
        )
    )
    conversation.interactions.append(
        Interaction(
            id=uuid.uuid4(),
            reponse_question=(
                un_constructeur_de_reponse_question()
                .donnant_en_reponse("réponse 2")
                .avec_une_question("question 2")
                .construis()
            ),
        )
    )

    adaptateur_test.sauvegarde_conversation(conversation)

    conversation_recuperee = adaptateur_test.recupere_conversation(
        conversation.id_conversation
    )
    assert conversation_recuperee is not None
    assert len(conversation_recuperee.interactions) == 2
    assert conversation_recuperee.__dict__ == conversation.__dict__


def test_retourne_none_poure_une_conversation_inexistante(adaptateur_test) -> None:
    conversation = adaptateur_test.recupere_conversation(uuid.uuid4())

    assert conversation is None


def test_mets_a_jour_une_conversation(
    adaptateur_test, un_constructeur_de_reponse_question
):
    conversation = Conversation(
        Interaction(
            id=uuid.uuid4(),
            reponse_question=(
                un_constructeur_de_reponse_question()
                .donnant_en_reponse("réponse 1")
                .avec_une_question("question 1")
                .construis()
            ),
        )
    )
    adaptateur_test.sauvegarde_conversation(conversation)

    interaction = Interaction(
        id=uuid.uuid4(),
        reponse_question=un_constructeur_de_reponse_question()
        .donnant_en_reponse("réponse 2")
        .avec_une_question("question 2")
        .construis(),
    )
    conversation.ajoute_interaction(interaction)
    adaptateur_test.sauvegarde_conversation(conversation)

    conversation_recuperee = adaptateur_test.recupere_conversation(
        conversation.id_conversation
    )
    assert conversation_recuperee is not None
    assert len(conversation_recuperee.interactions) == 2
    assert conversation_recuperee.__dict__ == conversation.__dict__


def test_mets_a_jour_une_interaction_d_une_conversation(
    adaptateur_test, un_constructeur_de_reponse_question
):
    Horloge.frise(dt.datetime(2026, 2, 15, 3, 4, 5))
    interaction_a_mettre_a_jour = Interaction(
        id=uuid.uuid4(),
        reponse_question=un_constructeur_de_reponse_question()
        .donnant_en_reponse("réponse 1")
        .avec_une_question("question 1")
        .construis(),
    )
    conversation = Conversation(interaction_a_mettre_a_jour)
    conversation.interactions.append(
        Interaction(
            id=uuid.uuid4(),
            reponse_question=un_constructeur_de_reponse_question()
            .donnant_en_reponse("réponse 2")
            .avec_une_question("question 2")
            .construis(),
        )
    )
    adaptateur_test.sauvegarde_conversation(conversation)

    interaction_a_mettre_a_jour.retour_utilisatrice = RetourPositif(
        commentaires="Un commentaire"
    )
    adaptateur_test.sauvegarde_conversation(conversation)

    conversation_recuperee = adaptateur_test.recupere_conversation(
        conversation.id_conversation
    )
    assert conversation_recuperee.interactions[0].retour_utilisatrice == RetourPositif(
        commentaires="Un commentaire"
    )
