import threading

from classification_de_test import (
    classification_element_de_reponse,
    classification_preuve_principale,
    reponse_classification_avec_identifiants_globaux,
)
from client_albert_de_test import ClientAlbertMemoire, un_choix_de_proposition


def identifiants_candidats(format_reponse) -> list[int]:
    proprietes = format_reponse["json_schema"]["schema"]["properties"]["candidats"][
        "properties"
    ]
    return [int(identifiant) for identifiant in proprietes]


class ClientAlbertQuiEchoueAuDeuxiemeLot(ClientAlbertMemoire):
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

    def recupere_propositions(
        self, messages, modele=None, temperature=None, format_reponse=None
    ):
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
            contenu = reponse_classification_avec_identifiants_globaux(
                {identifiant: classification_element_de_reponse()}
            )
            return [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]
        finally:
            with self._verrou:
                self._appels_en_cours -= 1


class ClientAlbertLotsEnOrdreControle(ClientAlbertMemoire):
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

    def recupere_propositions(
        self, messages, modele=None, temperature=None, format_reponse=None
    ):
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
        return [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]
