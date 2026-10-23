from concurrent.futures import ThreadPoolExecutor

from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition
from configuration import CapaciteReclassementParallele
from question.reclassement.reclasseur_llm_par_lots import ReclasseurLLMParLots
from services.coordinateur_reclassement_parallele import CoordinateurReclassementParallele
from services.reclasseur_llm_en_parallele import ReclasseurLLMEnParallele


def un_reclasseur_qui_repond(
    *reponses: str,
    taille_lot: int = 5,
    prompt_classification: str = "classification",
    bus: BusEvenementsEnMemoire | None = None,
) -> tuple[ReclasseurLLMParLots, ClientAlbertMemoire]:
    coordinateur = CoordinateurReclassementParallele(
        ThreadPoolExecutor(max_workers=1),
        CapaciteReclassementParallele(nombre_maximum_d_appels_par_workflow=3),
    )
    client = ClientAlbertMemoire()
    client.avec_les_propositions_par_appel(
        [
            [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]
            for contenu in reponses
        ]
    )
    reclasseur = ReclasseurLLMEnParallele(
        client,
        prompt_classification,
        bus or BusEvenementsEnMemoire(),
        taille_lot=taille_lot,
        coordinateur=coordinateur
    )
    return reclasseur, client
