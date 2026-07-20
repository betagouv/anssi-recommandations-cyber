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


def test_fournit_le_prompt_de_reclassement():
    client_albert_memoire = ClientAlbertMemoire()

    ReclasseurBGE(
        client_albert_memoire,
        "un-modele",
        "Prompt de reclassement :\n\n{QUESTION}\n\n, fin prompt",
        2,
    ).reclasse("Une question de test ?", [])

    assert (
        client_albert_memoire.payload_reclassement_recu.query
        == "Prompt de reclassement :\n\nUne question de test ?\n\n, fin prompt"
    )


def test_lis_le_nom_du_modele_de_reclassement(un_reclasseur):
    client_albert_memoire = ClientAlbertMemoire()

    ReclasseurBGE(client_albert_memoire, "rerank-small", "Prompt", 2).reclasse(
        "Une question", []
    )

    assert client_albert_memoire.payload_reclassement_recu.model == "rerank-small"


def test_retourne_au_maximum_5_paragraphes_meme_si_le_reclassement_echoue(
    un_constructeur_de_paragraphe,
):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.reclassement_vide()

    paragraphes = ReclasseurBGE(
        client_albert_memoire, "rerank-small", "Prompt", 5
    ).reclasse(
        "Une question",
        [
            un_constructeur_de_paragraphe().avec_contenu("texte1").construis(),
            un_constructeur_de_paragraphe().avec_contenu("texte2").construis(),
            un_constructeur_de_paragraphe().avec_contenu("texte3").construis(),
            un_constructeur_de_paragraphe().avec_contenu("texte4").construis(),
            un_constructeur_de_paragraphe().avec_contenu("texte5").construis(),
            un_constructeur_de_paragraphe().avec_contenu("texte6").construis(),
        ],
    )

    assert len(paragraphes.paragraphes_retenus) == 5
