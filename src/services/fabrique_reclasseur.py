from adaptateurs.bus_evenements import BusEvenements
from configuration import TypeReclasseur, taille_lot_reclassement, recupere_configuration
from infra.albert.client_albert import ClientAlbertApi, fabrique_client_albert
from question.reclassement.reclassement import Reclasseur
from question.reclassement.reclasseur_bge import ReclasseurBGE
from question.reclassement.reclasseur_llm import ReclasseurLLM
from services.coordinateur_reclassement_parallele import (
    fabrique_coordinateur_reclassement,
)
from services.fichier_prompt import lis_fichier_prompt
from services.reclasseur_llm_en_parallele import ReclasseurLLMEnParallele


def fabrique_reclasseur(
    bus_evenements: BusEvenements, client_albert_api: ClientAlbertApi
) -> Reclasseur:
    configuration = recupere_configuration()
    mode_reclassement = configuration.albert.service.type_reclasseur
    prompt_reclassement = lis_fichier_prompt(
        "prompt_reclassement_llm.txt"
        if mode_reclassement is TypeReclasseur.LLM
        else "prompt_reclassement.txt"
    )
    if mode_reclassement is TypeReclasseur.LLM:
        return ReclasseurLLM(
            client_albert_api, prompt_reclassement, bus_evenements
        )
    elif mode_reclassement is TypeReclasseur.LLM_PARALLELE:
        client_reclassement = fabrique_client_albert(
            configuration.albert.client, max_retries=0
        )
        return ReclasseurLLMEnParallele(
            client_reclassement,
            lis_fichier_prompt("prompt_reclassement_llm_classification.txt"),
            bus_evenements,
            coordinateur=fabrique_coordinateur_reclassement(),
            taille_lot=taille_lot_reclassement(),
            prompt_qualification=lis_fichier_prompt(
                "prompt_reclassement_llm_parallele_qualification.txt"
            ),
        )
    else:
        return ReclasseurBGE(
            client_albert_api,
            configuration.albert.service.modele_reclassement,
            prompt_reclassement,
            configuration.albert.service.nombre_paragraphes,
        )
