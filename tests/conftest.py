import random

import pytest

from schemas.albert import Paragraphe


class ConstructeurDeParagraphe:
    def __init__(self):
        self.url = "http://mondocument.local"
        self.score_similarite = random.uniform(0, 1)
        self.contenu = "un contenu"
        self.numero_page = random.randint(1, 100)
        self.nom_document = "Mon document"

    def construis(self) -> Paragraphe:
        return Paragraphe(
            nom_document=self.nom_document,
            numero_page=self.numero_page,
            contenu=self.contenu,
            score_similarite=self.score_similarite,
            url=self.url,
        )

    def avec_contenu(self, contenu: str):
        self.contenu = contenu
        return self


@pytest.fixture()
def un_constructeur_de_paragraphe() -> ConstructeurDeParagraphe:
    return ConstructeurDeParagraphe()
