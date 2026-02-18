import pytest
from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
    un_choix_de_proposition,
    un_constructeur_de_reponse_de_reclassement,
)
from configuration import Albert
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.albert import ReclasseReponse, ResultatReclasse, ReclassePayload
from schemas.violations import (
    REPONSE_PAR_DEFAUT,
    Violation,
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)
from services.service_albert import ServiceAlbert, Prompts
from client_albert_de_test import ConstructeurDeChoix

FAUSSE_CONFIGURATION_ALBERT_SERVICE = Albert.Service(  # type: ignore [attr-defined]
    collection_nom_anssi_lab="",
    collection_id_anssi_lab=42,
    reclassement_active=False,
    modele_reclassement="modele-reranking-de-test",
    taille_fenetre_historique=2,
)

FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT = Albert.Service(  # type: ignore [attr-defined]
    collection_nom_anssi_lab="",
    collection_id_anssi_lab=42,
    reclassement_active=True,
    modele_reclassement="rerank-small",
    taille_fenetre_historique=2,
)

PROMPT_SYSTEME_ALTERNATIF = (
    "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n{chunks}"
)
PROMPTS = Prompts(
    prompt_systeme=PROMPT_SYSTEME_ALTERNATIF,
    prompt_reclassement="Prompt de reclassement :\n\n{QUESTION}\n\n, fin prompt",
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
        False,
        PROMPTS,
    )

    reponse = service_albert.pose_question(question=QUESTION)

    assert reponse.reponse == REPONSE
    assert len(reponse.paragraphes) == 1
    assert reponse.question == QUESTION
    assert reponse.violation is None


def test_pose_question_separe_la_question_de_l_utilisatrice_des_instructions_systeme():
    client_albert_memoire = ClientAlbertMemoire()
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client_albert_memoire,
        False,
        PROMPTS,
    )

    service_albert.pose_question(question=QUESTION)

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
        False,
        PROMPTS,
    )

    service_albert.pose_question(question=QUESTION)

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
        False,
        PROMPTS,
    )

    retour = service_albert.pose_question(question=QUESTION)

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
        False,
        PROMPTS,
    )

    retour = service_albert.pose_question(question="question illégale ?")

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
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
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
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert list(map(lambda p: p.contenu, reponse_de_pose_question.paragraphes)) == [
        "paragraphe 1",
        "paragraphe 4",
        "paragraphe 7",
        "paragraphe 19",
        "paragraphe 3",
    ]


def test_les_paragraphes_reclasses_sont_envoyes_a_albert():
    reponse = (
        un_constructeur_de_reponse_de_reclassement()
        .avec_5_resultats(
            [
                {"titre": "paragraphe 1", "indice": 0, "score": 0.19},
                {"titre": "paragraphe 2", "indice": 1, "score": 0.48},
                {"titre": "paragraphe 3", "indice": 2, "score": 0.99},
                {"titre": "paragraphe 4", "indice": 3, "score": 0.6},
                {"titre": "paragraphe 5", "indice": 4, "score": 0.63},
            ]
        )
        .construis()
    )

    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_resultats([])
    service_albert = ServiceAlbert(
        FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client_albert_memoire,
        False,
        PROMPTS,
    )

    service_albert.pose_question(question=QUESTION)

    messages = client_albert_memoire.messages_recus
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert (
        "\n\nparagraphe 2\n\n\nparagraphe 4\n\n\nparagraphe 3\n\n\nparagraphe 1\n\n\nparagraphe 0"
        in messages[0]["content"]
    )


def test_retourne_20_paragraphes_en_effectuant_le_reclassement():
    reponse = un_constructeur_de_reponse_de_reclassement().construis()
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert client_albert_memoire.payload_recu.k == 20


def test_appelle_le_reclassement_uniquement_quand_active():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert client_albert_memoire.payload_reclassement_recu is None


def test_l_injection_du_prompt_de_reclassement():
    reponse = un_constructeur_de_reponse_de_reclassement().construis()
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert (
        client_albert_memoire.payload_reclassement_recu.prompt
        == "Prompt de reclassement :\n\nUne question de test ?\n\n, fin prompt"
    )


def test_lis_le_nom_du_modele_de_reclassement():
    reponse = un_constructeur_de_reponse_de_reclassement().construis()
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.avec_le_reclassement(reponse)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert client_albert_memoire.payload_reclassement_recu.model == "rerank-small"


def test_ne_reclasse_pas_si_la_recherche_de_paragraphes_retourne_un_resultat_vide():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.sans_resultats()

    reponse = ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert client_albert_memoire.payload_reclassement_recu is None
    assert reponse.reponse == REPONSE_PAR_DEFAUT


def test_retourne_les_resultats_de_recherche_si_le_reclassement_ne_retourne_pas_de_donnees():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.reclassement_vide()
    client_albert_memoire.avec_les_resultats(
        [
            un_resultat_de_recherche().ayant_pour_contenu("Un contenu").construis(),
        ]
    )
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu("Un contenu").construis(),
        ]
    )

    reponse = ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert reponse.reponse == "Un contenu"
    assert len(reponse.paragraphes) == 1
    assert reponse.question == "Une question de test ?"


def test_retourne_au_maximum_5_paragraphes_meme_si_le_reclassement_echoue():
    client_albert_memoire = ClientAlbertMemoire()
    client_albert_memoire.reclassement_vide()

    resultats_20_paragraphes = [
        un_resultat_de_recherche().ayant_pour_contenu(f"paragraphe {i}").construis()
        for i in range(20)
    ]

    client_albert_memoire.avec_les_resultats(resultats_20_paragraphes)
    client_albert_memoire.avec_les_propositions(
        [
            un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis(),
        ]
    )

    reponse = ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Une question de test ?")

    assert len(reponse.paragraphes) == 5


def test_initie_une_conversation(
    un_constructeur_de_conversation, un_constructeur_d_interaction
):
    client_albert_memoire = ClientAlbertMemoire()
    interaction = (
        un_constructeur_d_interaction()
        .avec_question("Une question de test ?")
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation()
        .avec_interaction(interaction=interaction)
        .ajoute_interaction(
            un_constructeur_d_interaction()
            .avec_question("Une deuxième question de test ?")
            .construis()
        )
        .construis()
    )

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(
        question="Une troisieme question de test ?", conversation=conversation
    )

    messages_recus = client_albert_memoire.messages_recus
    assert messages_recus == [
        {
            "role": "system",
            "content": "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n",
        },
        {
            "role": "user",
            "content": "Question :\nUne question de test ?",
        },
        {
            "role": "assistant",
            "content": "réponse : Une question de test ?",
        },
        {
            "role": "user",
            "content": "Question :\nUne deuxième question de test ?",
        },
        {
            "role": "assistant",
            "content": "réponse : Une deuxième question de test ?",
        },
        {
            "role": "user",
            "content": "Question :\nUne troisieme question de test ?",
        },
    ]


def test_limite_l_historique_a_2_interactions_passees(
    un_constructeur_de_conversation, un_constructeur_d_interaction
):
    client_albert_memoire = ClientAlbertMemoire()
    conversation = un_constructeur_de_conversation().construis()

    for i in range(2, 7):
        conversation.ajoute_interaction(
            un_constructeur_d_interaction().avec_question(f"Question {i} ?").construis()
        )

    configuration_avec_fenetre_limitee = Albert.Service(
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=42,
        reclassement_active=False,
        modele_reclassement="modele-reranking-de-test",
        taille_fenetre_historique=2,
    )

    ServiceAlbert(
        configuration_service_albert=configuration_avec_fenetre_limitee,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    ).pose_question(question="Question actuelle ?", conversation=conversation)

    messages_recus = client_albert_memoire.messages_recus

    assert messages_recus == [
        {
            "role": "system",
            "content": "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n",
        },
        {
            "role": "user",
            "content": "Question :\nQuestion 5 ?",
        },
        {
            "role": "assistant",
            "content": "réponse : Question 5 ?",
        },
        {
            "role": "user",
            "content": "Question :\nQuestion 6 ?",
        },
        {
            "role": "assistant",
            "content": "réponse : Question 6 ?",
        },
        {
            "role": "user",
            "content": "Question :\nQuestion actuelle ?",
        },
    ]


def test_peut_reformuler_une_question(une_configuration_de_service_albert):
    client_albert_memoire = ClientAlbertMemoire()
    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert_memoire, prompt_de_reformulation="Mon prompt"
    )
    mon_choix = (
        ConstructeurDeChoix().ayant_pour_contenu("Ma question reformulee").construis()
    )
    client_albert_memoire.avec_les_propositions([mon_choix])

    reponse_question = ServiceAlbert(
        configuration_service_albert=une_configuration_de_service_albert(),
        client=ClientAlbertMemoire(),
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=reformulateur,
    ).pose_question(question="Question actuelle ?", conversation=None)

    assert reponse_question.question_reformulee == "Ma question reformulee"


def test_recherche_paragraphes_utilise_la_question_reformulee(
    une_configuration_de_service_albert,
):
    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert_reformulation,
        prompt_de_reformulation="Mon prompt",
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question reformulee pour recherche")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    ServiceAlbert(
        configuration_service_albert=une_configuration_de_service_albert(),
        client=client_albert_recherche,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=reformulateur,
    ).pose_question(question="Ma question brute ?")

    assert (
        client_albert_recherche.payload_recu.prompt
        == "Question reformulee pour recherche"
    )


def test_reclassement_utilise_la_question_reformulee():
    reponse = un_constructeur_de_reponse_de_reclassement().construis()
    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    client_albert_recherche.avec_le_reclassement(reponse)
    client_albert_recherche.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )
    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert_reformulation,
        prompt_de_reformulation="Mon prompt",
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question reformulee pour reclassement")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE_AVEC_RECLASSEMENT,
        client=client_albert_recherche,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=reformulateur,
    ).pose_question(question="Ma question brute ?")

    assert (
        "Question reformulee pour reclassement"
        in client_albert_recherche.payload_reclassement_recu.prompt
    )


def test_pose_question_passe_la_conversation_au_reformulateur(
    un_constructeur_de_conversation, un_constructeur_d_interaction
):
    interaction = (
        un_constructeur_d_interaction()
        .avec_question("Qu'est-ce que le défacement ?")
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation().avec_interaction(interaction).construis()
    )

    client_albert_recherche = ClientAlbertMemoire()
    client_albert_reformulation = ClientAlbertMemoire()
    reformulateur = ReformulateurDeQuestion(
        client_albert=client_albert_reformulation,
        prompt_de_reformulation="Mon prompt",
    )
    choix_reformulation = (
        ConstructeurDeChoix()
        .ayant_pour_contenu("Question reformulee avec contexte")
        .construis()
    )
    client_albert_reformulation.avec_les_propositions([choix_reformulation])

    ServiceAlbert(
        configuration_service_albert=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_recherche,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=reformulateur,
    ).pose_question(question="Comment s'en protéger ?", conversation=conversation)

    assert len(client_albert_reformulation.messages_recus) == 4
    assert client_albert_reformulation.messages_recus[0]["role"] == "system"
    assert client_albert_reformulation.messages_recus[1]["role"] == "user"
    assert (
        client_albert_reformulation.messages_recus[1]["content"]
        == "Qu'est-ce que le défacement ?"
    )
    assert client_albert_reformulation.messages_recus[2]["role"] == "assistant"
    assert client_albert_reformulation.messages_recus[3]["role"] == "user"
    assert (
        client_albert_reformulation.messages_recus[3]["content"]
        == "Comment s'en protéger ?"
    )
