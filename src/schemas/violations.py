from abc import ABC, abstractmethod
from pydantic import BaseModel


REPONSE_PAR_DEFAULT = (
    "Désolé, nous n'avons pu générer aucune réponse correspondant à votre question."
)


class Violation(BaseModel, ABC):
    @property
    @abstractmethod
    def reponse(self) -> str: ...


class ViolationIdentite(Violation):
    @property
    def reponse(self):
        return "Je suis un service développé par ou pour l’ANSSI afin de répondre aux questions en cybersécurité et informatique, en m’appuyant sur les guides officiels disponibles sur le site de l’agence."


class ViolationMalveillance(Violation):
    @property
    def reponse(self):
        return REPONSE_PAR_DEFAULT


class ViolationThematique(Violation):
    @property
    def reponse(self):
        return "Cette thématique n’entre pas dans le cadre de mes compétences et des sources disponibles. Reformulez votre question autour d’un enjeu cybersécurité ou informatique."
