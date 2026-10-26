import pytest

from question.reclassement.unites_source import unites_du_paragraphe
from schemas.albert import UniteSource


@pytest.mark.parametrize(
    ("contenu", "contenus_attendus"),
    [("Texte.\n\nSuite.", ["Texte.\n\nSuite."]), (" \n\t ", [])],
)
def test_sans_chunks_enrichis_un_paragraphe_forme_une_seule_unite_source(
        un_constructeur_de_paragraphe, contenu, contenus_attendus
):
    paragraphe = un_constructeur_de_paragraphe().avec_contenu(contenu).construis()

    unites = unites_du_paragraphe(paragraphe)

    assert [unite.contenu for unite in unites] == contenus_attendus


def test_un_paragraphe_enrichi_garde_ses_unites_source(un_constructeur_de_paragraphe):
    unites = [
        UniteSource(contenu=contenu, url="https://exemple.test", numero_page=1)
        for contenu in ("Première unité", "Seconde unité")
    ]
    paragraphe = un_constructeur_de_paragraphe().construis()
    paragraphe = paragraphe.model_copy(update={"unites_source": unites})

    assert unites_du_paragraphe(paragraphe) == unites