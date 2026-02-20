from enum import StrEnum

from pydantic import BaseModel, model_serializer
from pydantic.config import ExtraValues
from typing import Any, cast
from typing_extensions import Self


class Reponse(StrEnum):
    IDENTITE = "Je suis un service développé par l'ANSSI afin de répondre aux questions en cybersécurité et informatique, en m'appuyant sur les guides officiels disponibles sur le site de l'agence."
    THEMATIQUE = "Cette thématique n'entre pas dans le cadre de mes compétences et des sources disponibles. Reformulez votre question autour d'un enjeu cybersécurité ou informatique."
    MALVEILLANCE = (
        "Désolé, nous n'avons pu générer aucune réponse correspondant à votre question."
    )
    MECONNAISSANCE = "Les sources actuellement disponibles ne me permettent pas de répondre à la question."
    QUESTION_NON_COMPRISE = "Désolé, je n'ai pas compris votre demande. Pourriez-vous reformuler votre question ? Pour rappel, je suis un service développé par l'ANSSI afin de répondre aux questions en cybersécurité et informatique"


REPONSE_PAR_DEFAUT = Reponse.MALVEILLANCE


class Violation(BaseModel):
    reponse: str = REPONSE_PAR_DEFAUT

    @model_serializer
    def to_json_structure(self) -> dict:
        return {"reponse": self.reponse}

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        match obj:
            case Reponse.IDENTITE:
                return cast(Self, ViolationIdentite())
            case Reponse.THEMATIQUE:
                return cast(Self, ViolationThematique())
            case Reponse.MALVEILLANCE:
                return cast(Self, ViolationMalveillance())
            case Reponse.MECONNAISSANCE:
                return cast(Self, ViolationMeconnaissance())
            case Reponse.QUESTION_NON_COMPRISE:
                return cast(Self, ViolationQuestionNonComprise())
        return cast(Self, Violation())


class ViolationIdentite(Violation):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.reponse = Reponse.IDENTITE


class ViolationMalveillance(Violation):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.reponse = Reponse.MALVEILLANCE


class ViolationThematique(Violation):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.reponse = Reponse.THEMATIQUE


class ViolationMeconnaissance(Violation):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.reponse = Reponse.MECONNAISSANCE


class ViolationQuestionNonComprise(Violation):
    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.reponse = Reponse.QUESTION_NON_COMPRISE
