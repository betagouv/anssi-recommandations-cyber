from client_albert_de_test import (
    ClientAlbertMemoire,
)
from configuration import Albert, TypeReclasseur
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from services.reclasseur import ReclasseurBGE, ReclasseurLLM, Reclasseur
from services.service_albert import Prompts, ServiceAlbert


PROMPTS = Prompts(
    prompt_systeme="Documents : {chunks}",
    prompt_reclassement=(
        "Question : {QUESTION}\n\nCandidats :\n{CANDIDATS}\n\nRetourne du JSON."
    ),
)


def une_configuration(
    type_reclasseur: TypeReclasseur, seuil_reponse_maitrisee: float = 0.5
) -> Albert.Service:  # type: ignore[name-defined, attr-defined]
    return Albert.Service(  # type: ignore[attr-defined]
        collection_nom_anssi_lab="",
        id_collection_anssi_lab=42,
        id_collection_anssi_lab_jeopardy=43,
        modele_reclassement="bge-reranker-v2-m3",
        taille_fenetre_historique=2,
        jeopardy_active=False,
        seuil_reponse_maitrisee=seuil_reponse_maitrisee,
        nombre_paragraphes=1,
        type_reclasseur=type_reclasseur,
    )


def construit_service(
    client: ClientAlbertMemoire, type_reclasseur: TypeReclasseur
) -> ServiceAlbert:
    reclasseur: Reclasseur
    if type_reclasseur == TypeReclasseur.BGE:
        prompt_reclassement = "Question BGE : {QUESTION}"
        reclasseur = ReclasseurBGE(
            client,
            "modèle",
            prompt_reclassement,
            5,
        )
    else:
        prompt_reclassement = PROMPTS.prompt_reclassement
        reclasseur = ReclasseurLLM(client, prompt_reclassement)
    return ServiceAlbert(
        configuration_service_albert=une_configuration(type_reclasseur),
        client=client,
        utilise_recherche_hybride=False,
        prompts=Prompts(
            prompt_systeme=PROMPTS.prompt_systeme,
            prompt_reclassement=prompt_reclassement,
        ),
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees({}),
        reclasseur=reclasseur,
    )


def test_selectionne_le_reclasseur_bge_par_configuration():
    service = construit_service(ClientAlbertMemoire(), TypeReclasseur.BGE)

    assert isinstance(service.reclasseur, ReclasseurBGE)
    assert service.reclasseur.prompt == "Question BGE : {QUESTION}"


def test_le_type_de_reclasseur_est_bge_par_defaut():
    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        id_collection_anssi_lab=42,
        id_collection_anssi_lab_jeopardy=43,
        modele_reclassement="bge-reranker-v2-m3",
        taille_fenetre_historique=2,
        jeopardy_active=False,
        seuil_reponse_maitrisee=0.5,
        nombre_paragraphes=1,
    )

    assert configuration.type_reclasseur is TypeReclasseur.BGE


def test_selectionne_le_reclasseur_llm_par_configuration():
    service = construit_service(ClientAlbertMemoire(), TypeReclasseur.LLM)

    assert isinstance(service.reclasseur, ReclasseurLLM)
    assert service.reclasseur.prompt == PROMPTS.prompt_reclassement
