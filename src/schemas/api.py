from pydantic import BaseModel, Field

from schemas.albert import ReponseQuestion


class QuestionRequete(BaseModel):
    question: str = Field(
        max_length=5000,
        description="Votre question d'une longueur maximale de 5000 caractères.",
    )


class ReponseParagraphe(BaseModel):
    url: str
    numero_page: int
    nom_document: str


def _mappe_une_reponse_albert(
    id_interaction, reponse_question: ReponseQuestion
) -> tuple[list[ReponseParagraphe], str, str]:
    question = reponse_question.question
    reponse = reponse_question.reponse
    paragraphes: list[ReponseParagraphe] = list(
        map(
            lambda p: ReponseParagraphe(
                url=f"/source/?document={p.nom_document}&page={p.numero_page}&interaction={str(id_interaction)}",
                nom_document=p.nom_document,
                numero_page=p.numero_page,
            ),
            reponse_question.paragraphes,
        )
    )
    return paragraphes, question, reponse


class ReponseDemandeConversationAPI(BaseModel):
    reponse: str
    paragraphes: list[ReponseParagraphe]
    question: str
    id_interaction: str
    id_conversation: str

    @staticmethod
    def depuis_reponse_albert(
        id_interaction: str, id_conversation: str, reponse_question: ReponseQuestion
    ) -> "ReponseDemandeConversationAPI":
        paragraphes, question, reponse = _mappe_une_reponse_albert(
            id_interaction, reponse_question
        )
        return ReponseDemandeConversationAPI(
            id_interaction=id_interaction,
            id_conversation=id_conversation,
            question=question,
            reponse=reponse,
            paragraphes=paragraphes,
        )


class ReponseConversationAjouteInteractionAPI(BaseModel):
    reponse: str
    paragraphes: list[ReponseParagraphe]
    question: str
    id_interaction: str

    @staticmethod
    def depuis_reponse_albert(
        id_interaction: str, reponse_question: ReponseQuestion
    ) -> "ReponseConversationAjouteInteractionAPI":
        paragraphes, question, reponse = _mappe_une_reponse_albert(
            id_interaction, reponse_question
        )
        return ReponseConversationAjouteInteractionAPI(
            id_interaction=id_interaction,
            question=question,
            reponse=reponse,
            paragraphes=paragraphes,
        )
