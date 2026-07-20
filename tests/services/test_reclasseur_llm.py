import json

from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
)
from services.reclasseur import ReclasseurLLM


def test_envoie_les_candidats_et_ne_conserve_que_les_preuves_principales(
    un_constructeur_de_paragraphe,
):
    client = ClientAlbertMemoire()
    paragraphe_sans_reponse = (
        un_constructeur_de_paragraphe()
        .avec_rang_initial(3)
        .avec_contenu("Passage dans la thématique, sans réponse")
        .construis()
    )
    paragraphe_preuve_principale = (
        un_constructeur_de_paragraphe()
        .avec_rang_initial(1)
        .avec_contenu("R50 Stocker les mots de passe dans un coffre-fort.")
        .construis()
    )
    paragraphe_element_de_reponse = (
        un_constructeur_de_paragraphe()
        .avec_rang_initial(2)
        .avec_contenu("Une recommandation complémentaire utile.")
        .construis()
    )
    client.avec_les_propositions_par_appel(
        [
            [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    json.dumps(
                        {
                            "evaluations": [
                                {
                                    "id": 1,
                                    "categorie": "dans_la_thematique_sans_apport",
                                },
                                {"id": 2, "categorie": "preuve_principale"},
                                {"id": 3, "categorie": "element_de_reponse"},
                            ],
                            "ids_retenus": [3, 2],
                        }
                    )
                )
                .construis()
            ]
        ]
    )

    reponse = ReclasseurLLM(client, "Un prompt {QUESTION} {CANDIDATS}").reclasse(
        "Une question ?",
        [
            paragraphe_sans_reponse,
            paragraphe_preuve_principale,
            paragraphe_element_de_reponse,
        ],
    )

    assert len(reponse.paragraphes_retenus) == 1
    assert len(reponse.tous_les_candidats) == 3
    assert (
        reponse.paragraphes_retenus[0].contenu
        == "R50 Stocker les mots de passe dans un coffre-fort."
    )
    assert reponse.paragraphes_retenus[0].score_reclassement == 1.0
    assert client.temperatures_recues == [0]
    assert (
        "[PASSAGE id=1"
        in client.messages_envoyes_pour_les_propositions[0][0]["content"]
    )
    assert (
        "rang_initial=1"
        in client.messages_envoyes_pour_les_propositions[0][0]["content"]
    )
    assert (
        "R50 Stocker les mots de passe dans un coffre-fort."
        in client.messages_envoyes_pour_les_propositions[0][0]["content"]
    )
    assert (
        "Passage dans la thématique, sans réponse"
        in client.messages_envoyes_pour_les_propositions[0][0]["content"]
    )
    assert (
        "Une recommandation complémentaire utile."
        in client.messages_envoyes_pour_les_propositions[0][0]["content"]
    )
