from openai.types.chat import ChatCompletionMessageParam

from services.service_albert import ClientAlbert


class ReformulateurDeQuestion:
    def __init__(self, client_albert: ClientAlbert, prompt_de_reformulation: str):
        self.client_albert = client_albert
        self.prompt_de_reformulation = prompt_de_reformulation

    def reformule(self, question: str) -> str | None:
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.prompt_de_reformulation},
            {"role": "user", "content": question},
        ]
        reponse = self.client_albert.recupere_propositions(messages)
        return reponse[0].message.content
