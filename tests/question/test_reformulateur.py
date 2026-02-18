from configuration import Albert
from infra.albert.client_albert import ClientAlbertApi
from question.reformulateur_de_question import ReformulateurDeQuestion
from client_albert_de_test import ClientAlbertMemoire, ConstructeurDeChoix

from client_albert_de_test import (
    ConstructeurClientHttp,
    ConstructeurRetourRouteSearch,
    ConstructeurClientOpenai,
)


def test_reformule_une_question():
    question = "ma question ?"
    mon_choix = (
        ConstructeurDeChoix().ayant_pour_contenu("Ma question reformulee").construis()
    )
    client_albert = ClientAlbertMemoire()
    client_albert.avec_les_propositions([mon_choix])

    question_reformulee = ReformulateurDeQuestion(
        client_albert=client_albert,
        prompt_de_reformulation="Mon prompt",
        modele_reformulation="albert-small",
    ).reformule(question)

    assert question_reformulee == "Ma question reformulee"


def test_reformule_la_question_avec_un_prompt_de_reformulation():
    question = "ma question ?"
    le_prompt = "Mon prompt de reformulation"
    mon_choix = (
        ConstructeurDeChoix().ayant_pour_contenu("Ma question reformulee").construis()
    )
    client_albert = ClientAlbertMemoire()
    client_albert.avec_les_propositions([mon_choix])

    ReformulateurDeQuestion(
        client_albert=client_albert,
        prompt_de_reformulation=le_prompt,
        modele_reformulation="albert-small",
    ).reformule(question)

    assert len(client_albert.messages_recus) == 2
    assert client_albert.messages_recus[0]["role"] == "system"
    assert client_albert.messages_recus[0]["content"] == le_prompt
    assert client_albert.messages_recus[1]["role"] == "user"
    assert client_albert.messages_recus[1]["content"] == "ma question ?"


def test_reformule_la_question_avec_l_historique_de_conversation(
    un_constructeur_de_conversation, un_constructeur_d_interaction
):
    interaction = (
        un_constructeur_d_interaction()
        .avec_question("Qu'est-ce que le défacement ?")
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation().avec_interaction(interaction).construis()
    )

    mon_choix = (
        ConstructeurDeChoix()
        .ayant_pour_contenu(
            "Quelles sont les bonnes pratiques pour se protéger du défacement ?"
        )
        .construis()
    )
    client_albert = ClientAlbertMemoire()
    client_albert.avec_les_propositions([mon_choix])

    ReformulateurDeQuestion(
        client_albert=client_albert,
        prompt_de_reformulation="Mon prompt",
        modele_reformulation="albert-small",
    ).reformule(question="Comment s'en protéger ?", conversation=conversation)

    assert len(client_albert.messages_recus) == 4
    assert client_albert.messages_recus[0]["role"] == "system"
    assert client_albert.messages_recus[1]["role"] == "user"
    assert client_albert.messages_recus[1]["content"] == "Qu'est-ce que le défacement ?"
    assert client_albert.messages_recus[2]["role"] == "assistant"
    assert client_albert.messages_recus[3]["role"] == "user"
    assert client_albert.messages_recus[3]["content"] == "Comment s'en protéger ?"


def test_reformulateur_utilise_le_modele_de_reformulation_de_la_configuration():
    client_http = (
        ConstructeurClientHttp()
        .qui_retourne(ConstructeurRetourRouteSearch().construis())
        .construis()
    )
    client_openai = (
        ConstructeurClientOpenai().qui_complete_avec("Question reformulee").construis()
    )

    configuration = Albert.Client(
        api_key="test-key",
        base_url="https://test.api",
        modele_reponse="albert-large",
        modele_reformulation="modele-reformulation",
        temps_reponse_maximum_pose_question=15.0,
        temps_reponse_maximum_recherche_paragraphes=3.0,
        utilise_recherche_hybride=False,
        decalage_index_Albert_et_numero_de_page_lecteur=0,
    )

    client_albert = ClientAlbertApi(client_openai, client_http, configuration)

    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert,
        prompt_de_reformulation="Mon prompt",
        modele_reformulation="modele-reformulation",
    )

    reformulateur.reformule("Ma question ?")

    client_openai.chat.completions.create.assert_called_once()
    call_kwargs = client_openai.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "modele-reformulation"
