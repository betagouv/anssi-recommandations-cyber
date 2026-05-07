import uuid

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement
from fastapi.testclient import TestClient


def test_redirige_vers_le_document_source(
    un_serveur_de_test,
    un_constructeur_d_interaction,
    un_constructeur_de_paragraphe,
    un_constructeur_de_conversation,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=AdaptateurJournalMemoire(),
    )
    paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(30)
        .dans_le_document("anssi-guide-gestion_crise_cyber.pdf")
        .construis()
    )
    une_interaction = (
        un_constructeur_d_interaction()
        .avec_une_reponse_contenant_les_paragraphes([paragraphe])
        .construis()
    )
    une_conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(une_interaction)
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(une_conversation)
    client_http = TestClient(serveur, follow_redirects=False)

    reponse = client_http.get(
        f"/source/?document=anssi-guide-gestion_crise_cyber.pdf&page=30&interaction={str(une_interaction.id)}"
    )

    assert reponse.status_code == 301
    assert (
        reponse.headers["Location"]
        == "http://mondocument.local/anssi-guide-gestion_crise_cyber.pdf#page=30"
    )


def test_redirige_vers_le_bon_document_source(
    un_serveur_de_test,
    un_constructeur_d_interaction,
    un_constructeur_de_paragraphe,
    un_constructeur_de_conversation,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=AdaptateurJournalMemoire(),
    )
    premier_paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(30)
        .dans_le_document("anssi-guide-gestion_crise_cyber.pdf")
        .construis()
    )
    deuxieme_paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(25)
        .dans_le_document("anssi-guide-gestion_crise_cyber.pdf")
        .construis()
    )
    une_interaction = (
        un_constructeur_d_interaction()
        .avec_une_reponse_contenant_les_paragraphes(
            [premier_paragraphe, deuxieme_paragraphe]
        )
        .construis()
    )
    une_conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(une_interaction)
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(une_conversation)
    client_http = TestClient(serveur, follow_redirects=False)

    reponse = client_http.get(
        f"/source/?document=anssi-guide-gestion_crise_cyber.pdf&page=25&interaction={str(une_interaction.id)}"
    )

    assert reponse.status_code == 301
    assert (
        reponse.headers["Location"]
        == "http://mondocument.local/anssi-guide-gestion_crise_cyber.pdf#page=25"
    )


def test_retourne_une_erreur_404_si_l_interaction_n_est_pas_trouvee(
    un_serveur_de_test, un_constructeur_d_interaction, un_constructeur_de_paragraphe
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=AdaptateurJournalMemoire(),
    )
    client_http = TestClient(serveur, follow_redirects=False)

    reponse = client_http.get(
        f"/source/?document=anssi-guide-gestion_crise_cyber.pdf&page=25&interaction={str(uuid.uuid4())}"
    )

    assert reponse.status_code == 404


def test_genere_une_erreur_404_si_le_document_n_est_pas_trouve(
    un_serveur_de_test,
    un_constructeur_d_interaction,
    un_constructeur_de_paragraphe,
    un_constructeur_de_conversation,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=AdaptateurJournalMemoire(),
    )
    paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(30)
        .dans_le_document("anssi-guide-gestion_crise_cyber.pdf")
        .construis()
    )
    une_interaction = (
        un_constructeur_d_interaction()
        .avec_une_reponse_contenant_les_paragraphes([paragraphe])
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(une_interaction)
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    client_http = TestClient(serveur, follow_redirects=False)

    reponse = client_http.get(
        f"/source/?document=un_document_inconnu.pdf&page=42&interaction={str(une_interaction.id)}"
    )

    assert reponse.status_code == 404


def test_retourne_erreur_404_si_le_numero_de_page_ne_correspond_pas(
    un_serveur_de_test,
    un_constructeur_d_interaction,
    un_constructeur_de_paragraphe,
    un_constructeur_de_conversation,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=AdaptateurJournalMemoire(),
    )
    premier_paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(30)
        .dans_le_document("anssi-guide-gestion_crise_cyber.pdf")
        .construis()
    )
    une_interaction = (
        un_constructeur_d_interaction()
        .avec_une_reponse_contenant_les_paragraphes([premier_paragraphe])
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(une_interaction)
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    client_http = TestClient(serveur, follow_redirects=False)

    reponse = client_http.get(
        f"/source/?document=anssi-guide-gestion_crise_cyber.pdf&page=42&interaction={str(une_interaction.id)}"
    )

    assert reponse.status_code == 404


def test_journalise_le_document_source_demande(
    un_serveur_de_test,
    un_constructeur_d_interaction,
    un_constructeur_de_paragraphe,
    un_constructeur_de_conversation,
):
    adaptateur_journal = AdaptateurJournalMemoire()
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )
    paragraphe = (
        un_constructeur_de_paragraphe()
        .a_la_page(25)
        .dans_le_document("anssi-guide-gestion_crise_cyber.pdf")
        .construis()
    )
    une_interaction = (
        un_constructeur_d_interaction()
        .avec_une_reponse_contenant_les_paragraphes([paragraphe])
        .construis()
    )
    une_conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(une_interaction)
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(une_conversation)
    client_http = TestClient(serveur, follow_redirects=False)

    client_http.get(
        f"/source/?document=anssi-guide-gestion_crise_cyber.pdf&page=25&interaction={str(une_interaction.id)}"
    )

    evenements = adaptateur_journal.les_evenements()
    assert len(evenements) == 1
    assert evenements[0]["type"] == TypeEvenement.DOCUMENT_SOURCE_VISIONNE
    assert evenements[0]["donnees"].id_interaction == une_interaction.id
    assert evenements[0]["donnees"].id_conversation == une_conversation.id_conversation
    assert (
        evenements[0]["donnees"].nom_document == "anssi-guide-gestion_crise_cyber.pdf"
    )
    assert evenements[0]["donnees"].numero_page == 25
    assert (
        evenements[0]["donnees"].url_document
        == "http://mondocument.local/anssi-guide-gestion_crise_cyber.pdf"
    )
