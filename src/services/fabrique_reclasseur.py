from adaptateurs.bus_evenements import BusEvenements
from configuration import TypeReclasseur, taille_lot_reclassement, recupere_configuration
from infra.albert.client_albert import ClientAlbertApi
from question.reclassement.reclassement import Reclasseur
from question.reclassement.reclasseur_bge import ReclasseurBGE
from question.reclassement.reclasseur_llm import ReclasseurLLM
from question.reclassement.reclasseur_llm_par_lots import ReclasseurLLMParLots
from services.fichier_prompt import lis_fichier_prompt


def fabrique_reclasseur(bus_evenements: BusEvenements, client_albert_api: ClientAlbertApi) -> Reclasseur:
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
    elif mode_reclassement is TypeReclasseur.LLM_PAR_LOTS:
        prompt_classification = lis_fichier_prompt(
            "prompt_reclassement_llm_classification.txt"
        )
        return ReclasseurLLMParLots(
            client_albert_api,
            prompt_classification,
            bus_evenements,
            taille_lot=taille_lot_reclassement(),
        )
    else:
        return ReclasseurBGE(
            client_albert_api,
            configuration.albert.service.modele_reclassement,
            prompt_reclassement,
            configuration.albert.service.nombre_paragraphes,
        )
