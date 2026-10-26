from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition
from question.reclassement.reclasseur_llm_par_lots import ReclasseurLLMParLots


def un_reclasseur_qui_repond(
    *reponses: str,
    taille_lot: int = 5,
    prompt_classification: str = "classification",
    bus: BusEvenementsEnMemoire | None = None,
) -> tuple[ReclasseurLLMParLots, ClientAlbertMemoire]:
    client = ClientAlbertMemoire()
    client.avec_les_propositions_par_appel(
        [
            [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]
            for contenu in reponses
        ]
    )
    reclasseur = ReclasseurLLMParLots(
        client,
        prompt_classification,
        bus or BusEvenementsEnMemoire(),
        taille_lot=taille_lot,
    )
    return reclasseur, client
