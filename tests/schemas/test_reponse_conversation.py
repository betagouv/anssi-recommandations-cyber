from schemas.albert import ReponseQuestion, ParagrapheReponseQuestion
from schemas.api import (
    ReponseDemandeConversationAPI,
    ReponseParagraphe,
    ReponseConversationAjouteInteractionAPI,
)


def test_transforme_une_reponse_albert_en_reponse_conversation():
    reponse_question = ReponseQuestion(
        reponse="Réponse de test",
        question="Question de test",
        paragraphes=[
            ParagrapheReponseQuestion(
                url="http://example.local",
                nom_document="guide-anssi.pdf",
                numero_page=20,
                contenu="Contenu du paragraphe",
                score_similarite=0.95,
                score_reclassement=1.0,
            )
        ],
        question_reformulee="Question reformulée",
        violation=None,
    )
    id_interaction = "id_interaction"
    id_conversation = "id_conversation"

    reponse: ReponseDemandeConversationAPI = (
        ReponseDemandeConversationAPI.depuis_reponse_albert(
            id_interaction=id_interaction,
            id_conversation=id_conversation,
            reponse_question=reponse_question,
        )
    )

    assert reponse.id_interaction == str(id_interaction)
    assert reponse.id_conversation == str(id_conversation)
    assert reponse.reponse == "Réponse de test"
    assert reponse.question == "Question de test"
    assert reponse.paragraphes == [
        ReponseParagraphe(
            url=f"/source/?document=guide-anssi.pdf&page=20&interaction={id_interaction}",
            nom_document="guide-anssi.pdf",
            numero_page=20,
            contenu="Contenu du paragraphe",
        )
    ]


def test_transforme_une_reponse_albert_en_reponse_conversation_ajoute_interaction():
    reponse_question = ReponseQuestion(
        reponse="Réponse de test",
        question="Question de test",
        paragraphes=[
            ParagrapheReponseQuestion(
                url="http://example.local",
                nom_document="guide-anssi.pdf",
                numero_page=20,
                contenu="Contenu du paragraphe",
                score_similarite=0.95,
                score_reclassement=1.0,
            )
        ],
        question_reformulee="Question reformulée",
        violation=None,
    )
    id_interaction = "id_interaction"

    reponse: ReponseConversationAjouteInteractionAPI = (
        ReponseConversationAjouteInteractionAPI.depuis_reponse_albert(
            id_interaction=id_interaction, reponse_question=reponse_question
        )
    )

    assert reponse.id_interaction == str(id_interaction)
    assert reponse.reponse == "Réponse de test"
    assert reponse.question == "Question de test"
    assert reponse.paragraphes == [
        ReponseParagraphe(
            url=f"/source/?document=guide-anssi.pdf&page=20&interaction={id_interaction}",
            nom_document="guide-anssi.pdf",
            numero_page=20,
            contenu="Contenu du paragraphe",
        )
    ]
