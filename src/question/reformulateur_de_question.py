from typing import Optional

from openai.types.chat import ChatCompletionMessageParam
from schemas.retour_utilisatrice import Conversation
from services.client_albert import ClientAlbert


class ReformulateurDeQuestion:
    def __init__(
        self,
        client_albert: ClientAlbert,
        prompt_de_reformulation: str,
        modele_reformulation: str,
    ):
        self.client_albert = client_albert
        self.prompt_de_reformulation = prompt_de_reformulation
        self.modele_reformulation = modele_reformulation

    def reformule(
        self, question: str, conversation: Optional[Conversation] = None
    ) -> str | None:
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.prompt_de_reformulation},
        ]
        if conversation is not None:
            for interaction in reversed(conversation.interactions_sans_violation):
                messages.extend(
                    [
                        {
                            "role": "user",
                            "content": interaction.reponse_question.question,
                        },
                        {
                            "role": "assistant",
                            "content": interaction.reponse_question.reponse,
                        },
                    ]
                )
        messages.append({"role": "user", "content": question})
        reponse = self.client_albert.recupere_propositions(
            messages, modele=self.modele_reformulation
        )
        return reponse[0].message.content
