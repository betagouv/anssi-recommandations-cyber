import pytest

from adaptateurs.horloge import Horloge
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import RetourPositif, TagPositif
import datetime as dt


@pytest.fixture()
def une_reponse_question():
    return ReponseQuestion(
        reponse="Une réponse", question="Une question", paragraphes=[], violation=None
    )


@pytest.fixture()
def un_retour_positif():
    Horloge.frise(dt.datetime(2024, 1, 2, 3, 4, 5))
    return RetourPositif(
        commentaire="Très utile",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
