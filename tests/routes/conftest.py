import pytest
import uuid

from adaptateurs.horloge import Horloge
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import RetourPositif, TagPositif, Interaction
import datetime as dt


@pytest.fixture()
def une_reponse_question():
    return ReponseQuestion(
        reponse="Une réponse", question="Une question", paragraphes=[], violation=None
    )


@pytest.fixture()
def une_interaction(une_reponse_question):
    return Interaction(
        reponse_question=une_reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
    )


@pytest.fixture()
def un_retour_positif():
    Horloge.frise(dt.datetime(2024, 1, 2, 3, 4, 5))
    return RetourPositif(
        commentaire="Très utile",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
