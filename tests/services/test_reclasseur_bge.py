from client_albert_de_test import ClientAlbertMemoire
from schemas.albert import ReclasseReponse, ResultatReclasse
from services.reclasseur import ReclasseurBGE


def test_reclasse_les_paragraphes(un_constructeur_de_paragraphe):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(
        ReclasseReponse(
            data=[
                ResultatReclasse(object="rerank", score=0.5, index=1),
                ResultatReclasse(object="rerank", score=0.4, index=0),
            ],
        )
    )

    reclasseur = ReclasseurBGE(
        client_albert_memoire, "un-modele", "un-prompt", 2
    ).reclasse(
        "une question",
        [
            un_constructeur_de_paragraphe().avec_contenu("texte1").construis(),
            un_constructeur_de_paragraphe().avec_contenu("texte2").construis(),
        ],
    )

    assert reclasseur.paragraphes_retenus[0].contenu == "texte2"
    assert reclasseur.paragraphes_retenus[1].contenu == "texte1"
