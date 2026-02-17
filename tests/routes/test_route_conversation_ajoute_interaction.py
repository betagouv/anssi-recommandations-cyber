from fastapi.testclient import TestClient

from adaptateurs.journal import TypeEvenement
from schemas.api import QuestionRequete
from schemas.type_utilisateur import TypeUtilisateur


def test_route_conversation_ajoute_interaction_repond_201(
    un_serveur_de_test_complet,
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
):
    serveur, _, adaptateur_base_de_donnees, _, service_albert = (
        un_serveur_de_test_complet()
    )
    conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(
            un_constructeur_d_interaction()
            .avec_question("Qu’est-ce que le défacement ?")
            .construis()
        )
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    client: TestClient = TestClient(serveur)
    r = client.post(
        f"/api/conversation/{conversation.id_conversation}",
        json={"question": "Comment s’en prémunir ?"},
    )

    assert r.status_code == 201


def test_route_conversation_ajoute_interaction_retourne_un_resultat_de_conversation(
    un_serveur_de_test_complet,
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_constructeur_de_reponse_question,
    un_constructeur_de_paragraphe,
):
    serveur, _, adaptateur_base_de_donnees, _, service_albert = (
        un_serveur_de_test_complet()
    )
    conversation = (
        un_constructeur_de_conversation()
        .ajoute_interaction(
            un_constructeur_d_interaction()
            .avec_question("Qu’est-ce que le défacement ?")
            .construis()
        )
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    requete_question = QuestionRequete(question="Comment s’en prémunir ?")
    reponse = (
        un_constructeur_de_reponse_question()
        .a_partir_d_une_requete(requete_question)
        .donnant_en_reponse("Faire les choses correctement")
        .avec_les_paragraphes(
            [
                un_constructeur_de_paragraphe()
                .avec_contenu("Contenu du paragraphe 1")
                .ayant_comme_score(0.75)
                .a_la_page(29)
                .dans_le_document(
                    "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
                )
                .construis(),
                un_constructeur_de_paragraphe()
                .avec_contenu("Contenu du paragraphe 2")
                .ayant_comme_score(0.72)
                .a_la_page(15)
                .dans_le_document("guide_hygiene_informatique_anssi.pdf")
                .construis(),
            ]
        )
        .construis()
    )
    service_albert.ajoute_reponse(reponse)

    client: TestClient = TestClient(serveur)
    r = client.post(
        f"/api/conversation/{conversation.id_conversation}",
        json={"question": "Comment s’en prémunir ?"},
    )

    corps_de_reponse = r.json()
    assert corps_de_reponse["id_interaction"]
    assert corps_de_reponse["question"] == "Comment s’en prémunir ?"
    assert corps_de_reponse["reponse"] == "Faire les choses correctement"
    assert len(corps_de_reponse["paragraphes"]) == 2


def test_route_conversation_ajoute_interaction_emets_un_evenement_dans_le_journal(
    un_serveur_de_test_complet,
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
):
    (
        serveur,
        adaptateur_de_chiffrement,
        adaptateur_base_de_donnees,
        adaptateur_journal,
        _,
    ) = un_serveur_de_test_complet()
    conversation = un_constructeur_de_conversation().construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    adaptateur_de_chiffrement.qui_hache("id-interaction")

    client = TestClient(serveur)
    client.post(
        f"/api/conversation/{conversation.id_conversation}?type_utilisateur=ABCD",
        json={"question": "Une question"},
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.INTERACTION_CREEE
    assert evenements[0]["donnees"].id_interaction == "id-interaction"
    assert evenements[0]["donnees"].longueur_question == 12
    assert evenements[0]["donnees"].longueur_reponse == 0
    assert evenements[0]["donnees"].longueur_paragraphes == 0
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.INCONNU


def test_route_conversation_ajoute_interaction_retourne_une_reponse_en_erreur(
    un_serveur_de_test_complet,
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
):
    serveur, _, adaptateur_base_de_donnees, _, service_albert = (
        un_serveur_de_test_complet()
    )
    service_albert.qui_leve_une_erreur_sur_pose_question()
    conversation = un_constructeur_de_conversation().construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    client = TestClient(serveur)
    reponse = client.post(
        f"/api/conversation/{conversation.id_conversation}?type_utilisateur=ABCD",
        json={"question": "Une question"},
    )

    assert reponse.status_code == 422
    assert reponse.json() == {"detail": {"message": "Erreur lors de l’appel à Albert"}}
