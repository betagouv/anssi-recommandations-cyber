from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional
from schemas.reponses import ReponseQuestion


class RetourUtilisatrice(BaseModel):
    pouce_leve: Optional[bool] = None
    commentaire: Optional[str] = None
    horodatage: datetime = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def valide_au_moins_un_champ(self):
        if self.pouce_leve is None and (
            self.commentaire is None or self.commentaire.strip() == ""
        ):
            raise ValueError(
                "Au moins 'pouce_leve' ou 'commentaire' doit être renseigné"
            )
        return self


class Interaction(BaseModel):
    reponse_question: ReponseQuestion
    retour_utilisatrice: Optional[RetourUtilisatrice] = None
