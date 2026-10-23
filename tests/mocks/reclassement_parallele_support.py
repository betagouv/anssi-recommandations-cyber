import json
import threading

from classification_de_test import (
    classification_element_de_reponse,
    classification_preuve_principale,
    reponse_classification_avec_identifiants_globaux,
)
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition
from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
)
from services.reclasseur_llm_en_parallele import ReclasseurLLMEnParallele


def un_reclasseur_en_parallele(
    client: ClientAlbertMemoire,
    coordinateur: CoordinateurReclassementParallele,
    taille_lot: int = 5,
) -> ReclasseurLLMEnParallele:
    return ReclasseurLLMEnParallele(
        client,
        "{QUESTION}\n{CANDIDATS}",
        BusEvenementsEnMemoire(),
        coordinateur,
        "{QUESTION}\n{DOCUMENTS}",
        taille_lot,
    )


def identifiants_candidats(format_reponse) -> list[int]:
    proprietes = format_reponse["json_schema"]["schema"]["properties"]["candidats"][
        "properties"
    ]
    return [int(identifiant) for identifiant in proprietes]


def reponse_qualification_standard(format_reponse) -> str:
    proprietes = format_reponse["json_schema"]["schema"]["properties"]
    return json.dumps(
        {
            identifiant: (
                "indetermine"
                if specification["enum"] == ["indetermine"]
                else "consacre_au_sujet"
            )
            for identifiant, specification in proprietes.items()
        }
    )


class ClientAlbertAvecQualification(ClientAlbertMemoire):
    def recupere_propositions(
        self, messages, modele=None, temperature=None, format_reponse=None
    ):
        nom_schema = format_reponse["json_schema"]["name"]
        self.noms_schemas_propositions.append(nom_schema)
        self.messages_envoyes_pour_les_propositions.append(messages)
        if nom_schema == "qualification_guides":
            contenu = self.qualifie(format_reponse)
        else:
            contenu = self.classifie(format_reponse)
        return [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]

    def qualifie(self, format_reponse) -> str:
        return reponse_qualification_standard(format_reponse)

    def classifie(self, format_reponse) -> str:
        return reponse_classification_avec_identifiants_globaux(
            {
                identifiant: classification_element_de_reponse()
                for identifiant in identifiants_candidats(format_reponse)
            }
        )


class ClientAlbertQuiEchoueAuDeuxiemeLot(ClientAlbertAvecQualification):
    def __init__(self) -> None:
        super().__init__()
        self.barriere = threading.Barrier(5)
        self.liberation = threading.Event()
        self.tous_les_lots_soumis = threading.Event()
        self._verrou = threading.Lock()
        self._appels: list[int] = []
        self._appels_en_cours = 0

    @property
    def appels(self) -> list[int]:
        with self._verrou:
            return list(self._appels)

    @property
    def appels_en_cours(self) -> int:
        with self._verrou:
            return self._appels_en_cours

    def classifie(self, format_reponse) -> str:
        identifiant = identifiants_candidats(format_reponse)[0]
        with self._verrou:
            self._appels.append(identifiant)
            self._appels_en_cours += 1
            if len(self._appels) == 5:
                self.tous_les_lots_soumis.set()
        self.barriere.wait(timeout=5)
        if identifiant == 2:
            with self._verrou:
                self._appels_en_cours -= 1
            raise RuntimeError("échec du deuxième lot")
        try:
            self.liberation.wait(timeout=5)
            return reponse_classification_avec_identifiants_globaux(
                {identifiant: classification_element_de_reponse()}
            )
        finally:
            with self._verrou:
                self._appels_en_cours -= 1


class ClientAlbertLotsEnOrdreControle(ClientAlbertAvecQualification):
    def __init__(self) -> None:
        super().__init__()
        self.barriere = threading.Barrier(3)
        self.demarre = threading.Event()
        self.liberations = {
            1: threading.Event(),
            4: threading.Event(),
            7: threading.Event(),
        }
        self.termines = {
            1: threading.Event(),
            4: threading.Event(),
            7: threading.Event(),
        }
        self.identifiants_observes: list[int] = []

    def classifie(self, format_reponse) -> str:
        ids = identifiants_candidats(format_reponse)
        premier_id = ids[0]
        self.identifiants_observes.extend(ids)
        self.barriere.wait(timeout=5)
        if premier_id == 7:
            self.demarre.set()
        self.liberations[premier_id].wait(timeout=5)
        evaluations = {
            identifiant: classification_preuve_principale(apport="explication_directe")
            for identifiant in ids
        }
        contenu = reponse_classification_avec_identifiants_globaux(evaluations)
        self.termines[premier_id].set()
        return contenu
