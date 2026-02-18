from question.reformulateur_de_question import ReformulateurDeQuestion
from client_albert_de_test import ClientAlbertMemoire, ConstructeurDeChoix


def test_reformule_une_question():
    question = "ma question ?"
    mon_choix = (
        ConstructeurDeChoix().ayant_pour_contenu("Ma question reformulee").construis()
    )
    client_albert = ClientAlbertMemoire()
    client_albert.avec_les_propositions([mon_choix])

    question_reformulee = ReformulateurDeQuestion(
        client_albert=client_albert, prompt_de_reformulation="Mon prompt"
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
        client_albert=client_albert, prompt_de_reformulation=le_prompt
    ).reformule(question)

    assert len(client_albert.messages_recus) == 2
    assert client_albert.messages_recus[0]["role"] == "system"
    assert client_albert.messages_recus[0]["content"] == le_prompt
    assert client_albert.messages_recus[1]["role"] == "user"
    assert client_albert.messages_recus[1]["content"] == "ma question ?"
