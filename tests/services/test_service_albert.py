import pytest
from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
    un_choix_de_proposition,
    un_constructeur_de_reponse_de_reclassement,
)
from configuration import Albert
from schemas.albert import ReclasseReponse, ResultatReclasse, ReclassePayload
from schemas.violations import (
    REPONSE_PAR_DEFAUT,
    Violation,
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)
from services.service_albert import ServiceAlbert

FAUSSE_CONFIGURATION_ALBERT_SERVICE = Albert.Service(  # type: ignore [attr-defined]
    collection_nom_anssi_lab="",
    collection_id_anssi_lab=42,
)
PROMPT_SYSTEME_ALTERNATIF = (
    "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n{chunks}"
)
QUESTION = "Quelle est la recette de la tartiflette ?"
REPONSE = "Patates et reblochon"
FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."


def test_pose_question_retourne_une_reponse():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu(REPONSE).construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client_albert_memoire,
        PROMPT_SYSTEME_ALTERNATIF,
        False,
    )

    reponse = service_albert.pose_question(QUESTION)

    assert reponse.reponse == REPONSE
    assert len(reponse.paragraphes) == 1
    assert reponse.question == QUESTION
    assert reponse.violation is None


def test_pose_question_separe_la_question_de_l_utilisatrice_des_instructions_systeme():
    client_albert_memoire = ClientAlbertMemoire()
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client_albert_memoire,
        PROMPT_SYSTEME_ALTERNATIF,
        False,
    )

    service_albert.pose_question(QUESTION)

    messages = client_albert_memoire.messages_recus
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert (
        messages[0]["content"]
        == "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n"
    )
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == f"Question :\n{QUESTION}"


def test_pose_question_les_documents_sont_ajoutes_aux_instructions_systeme():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu(FAUX_CONTENU).construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(FAUX_CONTENU).construis(),
        ]
    )
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client_albert_memoire,
        PROMPT_SYSTEME_ALTERNATIF,
        False,
    )

    service_albert.pose_question(QUESTION)

    messages = client_albert_memoire.messages_recus
    messages_systeme = list(filter(lambda m: m["role"] == "system", messages))
    assert len(messages_systeme) == 1
    assert FAUX_CONTENU in messages_systeme[0]["content"]


def test_pose_question_retourne_une_reponse_generique_et_pas_de_violation_si_albert_ne_retourne_rien():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.sans_resultats()
    client_albert_memoire.sans_propositions()
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client_albert_memoire,
        PROMPT_SYSTEME_ALTERNATIF,
        False,
    )

    retour = service_albert.pose_question(QUESTION)

    assert retour.reponse == REPONSE_PAR_DEFAUT
    assert retour.paragraphes == []
    assert retour.violation is None


@pytest.mark.parametrize(
    "erreur,violation_attendue",
    [
        pytest.param(
            "ERREUR_MALVEILLANCE",
            ViolationMalveillance(),
            id="si_question_malveillante_retourne_message_malveillant_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_THÉMATIQUE",
            ViolationThematique(),
            id="si_question_mauvaise_thematique_retourne_message_thematique_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_IDENTITÉ",
            ViolationIdentite(),
            id="si_question_identite_retourne_message_identite_avec_paragraphes_vides",
        ),
    ],
)
def test_pose_question_illegale(erreur: str, violation_attendue: Violation):
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu("Un contenu").construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(erreur).construis(),
        ]
    )
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client_albert_memoire,
        PROMPT_SYSTEME_ALTERNATIF,
        False,
    )

    retour = service_albert.pose_question("question illégale ?")

    assert retour.reponse == violation_attendue.reponse
    assert retour.paragraphes == []
    assert retour.violation == violation_attendue


def test_reclasse_les_paragraphes():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(
        ReclasseReponse(
            id="test",
            object="list",
            data=[
                ResultatReclasse(object="rerank", score=0.5, index=1),
                ResultatReclasse(object="rerank", score=0.4, index=0),
            ],
        )
    )

    payload = ReclassePayload(
        prompt="un prompt", input=["texte1", "texte2"], model="albert_rerank"
    )
    reclassement = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_memoire,
        prompt_systeme="",
        utilise_recherche_hybride=False,
    ).reclasse(payload)

    assert reclassement == {"paragraphes_tries": ["texte2", "texte1"]}


def test_en_cas_de_reclassement_recherche_paragraphes_retourne_les_5_paragraphes_les_mieux_classes_parmi_les_20_retournes():
    reponse = (
        un_constructeur_de_reponse_de_reclassement()
        .avec_les_paragraphes_les_mieux_classes(
            [
                {"titre": "paragraphe 1", "indice": 1, "score": 0.9},
                {"titre": "paragraphe 4", "indice": 4, "score": 0.8},
                {"titre": "paragraphe 7", "indice": 7, "score": 0.7},
                {"titre": "paragraphe 19", "indice": 19, "score": 0.66},
                {"titre": "paragraphe 3", "indice": 3, "score": 0.63},
            ]
        )
        .construis()
    )
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    reponse_de_pose_question = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_memoire,
        prompt_systeme="",
        utilise_recherche_hybride=False,
    ).pose_question("Une question de test ?")

    assert list(map(lambda p: p.contenu, reponse_de_pose_question.paragraphes)) == [
        "paragraphe 1",
        "paragraphe 4",
        "paragraphe 7",
        "paragraphe 19",
        "paragraphe 3",
    ]
