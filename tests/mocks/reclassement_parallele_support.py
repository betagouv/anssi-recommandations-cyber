import json
import threading
from collections.abc import Mapping
from typing import TypeVar


from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
)
from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
)
from services.reclasseur import ReclasseurLLMEnParallele

Identifiant = TypeVar("Identifiant", int, str)


def reponse_classification_avec_identifiants_globaux(
    classifications: Mapping[Identifiant, Mapping[str, str | int]],
) -> str:
    return json.dumps(
        {
            "candidats": {
                str(identifiant): classification
                for identifiant, classification in classifications.items()
            }
        }
    )


def classification_element_de_reponse(
    *,
    relation: str = "directe",
    portee: str = "generale",
    apport: str = "principe_direct",
) -> dict[str, str | int]:
    return {
        "categorie": "element_de_reponse",
        "relation": relation,
        "portee": portee,
        "apport": apport,
    }


def classification_preuve_principale(
    *,
    portee: str = "generale",
    apport: str = "principe_direct",
    debut_unite: int = 1,
    fin_unite: int = 1,
) -> dict[str, str | int]:
    return {
        "categorie": "preuve_principale",
        "relation": "directe",
        "portee": portee,
        "apport": apport,
        "debut_unite": debut_unite,
        "fin_unite": fin_unite,
    }


def cree_reclasseur_llm_en_parallele(
    client: ClientAlbertMemoire,
    coordinateur: CoordinateurReclassementParallele,
    *,
    prompt_classification: str = "classification",
    prompt_qualification: str = "{QUESTION}\n{DOCUMENTS}",
    taille_lot: int = 5,
    bus: BusEvenementsEnMemoire | None = None,
) -> ReclasseurLLMEnParallele:
    return ReclasseurLLMEnParallele(
        client,
        prompt_classification,
        bus if bus is not None else BusEvenementsEnMemoire(),
        coordinateur,
        taille_lot=taille_lot,
        prompt_qualification=prompt_qualification,
    )


def configure_reponses_par_appel(
    client: ClientAlbertMemoire, contenus: list[str]
) -> None:
    client.avec_les_propositions_par_appel(
        [
            [un_choix_de_proposition().ayant_pour_contenu(contenu).construis()]
            for contenu in contenus
        ]
    )


def reponse_qualification_standard(format_reponse) -> str:
    proprietes = format_reponse["json_schema"]["schema"]["properties"]
    documents = {
        identifiant: (
            "indetermine"
            if specification["enum"] == ["indetermine"]
            else "consacre_au_sujet"
        )
        for identifiant, specification in proprietes.items()
    }
    return json.dumps(documents)


def identifiants_candidats(format_reponse) -> list[int]:
    proprietes = format_reponse["json_schema"]["schema"]["properties"]["candidats"][
        "properties"
    ]
    return [int(identifiant) for identifiant in proprietes]


def nombre_appels_par_schema(client: ClientAlbertMemoire, nom_schema: str) -> int:
    return client.noms_schemas_propositions.count(nom_schema)


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
        self,
        messages,
        modele=None,
        temperature=None,
        format_reponse=None,
    ):
        if (
            format_reponse
            and format_reponse.get("json_schema", {}).get("name")
            == "qualification_guides"
        ):
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(reponse_qualification_standard(format_reponse))
                .construis()
            ]
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
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(
                    reponse_classification_avec_identifiants_globaux(
                        {identifiant: classification_element_de_reponse()}
                    )
                )
                .construis()
            ]
        finally:
            with self._verrou:
                self._appels_en_cours -= 1


class ClientAlbertCaptureFormats(ClientAlbertMemoire):
    def __init__(self) -> None:
        super().__init__()
        self.formats_reponse_recus: list[dict | None] = []

    def recupere_propositions(
        self,
        messages,
        modele=None,
        temperature=None,
        format_reponse=None,
    ):
        self.formats_reponse_recus.append(format_reponse)
        return super().recupere_propositions(
            messages, modele, temperature, format_reponse
        )


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
        self,
        messages,
        modele=None,
        temperature=None,
        format_reponse=None,
    ):
        if (
            format_reponse
            and format_reponse.get("json_schema", {}).get("name")
            == "qualification_guides"
        ):
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(reponse_qualification_standard(format_reponse))
                .construis()
            ]
        ids = identifiants_candidats(format_reponse)
        if ids:
            premier_id = ids[0]
            self.identifiants_observes.extend(ids)
            self.barriere.wait(timeout=5)
            if premier_id == 7:
                self.demarre.set()
            self.liberations[premier_id].wait(timeout=5)
            evaluations = {
                identifiant: classification_preuve_principale(
                    apport="explication_directe"
                )
                for identifiant in ids
            }
            contenu_reponse = reponse_classification_avec_identifiants_globaux(
                evaluations
            )
            self.termines[premier_id].set()
        return [
            un_choix_de_proposition().ayant_pour_contenu(contenu_reponse).construis()
        ]


class ClientAlbertQualificationDocumentRetardee(ClientAlbertMemoire):
    def __init__(self) -> None:
        super().__init__()
        self.lot_suivant_termine = threading.Event()
        self.ordre_fin_lots: list[int] = []

    def recupere_propositions(
        self,
        messages,
        modele=None,
        temperature=None,
        format_reponse=None,
    ):
        if (
            format_reponse
            and format_reponse.get("json_schema", {}).get("name")
            == "qualification_guides"
        ):
            assert self.lot_suivant_termine.wait(timeout=5)
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(json.dumps({"D1": "consacre_au_sujet"}))
                .construis()
            ]
        identifiant = identifiants_candidats(format_reponse)[0]
        if identifiant == 1:
            assert self.lot_suivant_termine.wait(timeout=5)
            classification = {
                "candidats": {
                    "1": {
                        "categorie": "preuve_principale",
                        "relation": "directe",
                        "portee": "generale",
                        "apport": "principe_direct",
                        "debut_unite": 1,
                        "fin_unite": 1,
                    }
                },
            }
        else:
            classification = {
                "candidats": {
                    "2": {
                        "categorie": "preuve_principale",
                        "relation": "directe",
                        "portee": "generale",
                        "apport": "reponse_centrale",
                        "debut_unite": 1,
                        "fin_unite": 1,
                    }
                },
            }
        self.ordre_fin_lots.append(identifiant)
        if identifiant == 2:
            self.lot_suivant_termine.set()
        return [
            un_choix_de_proposition()
            .ayant_pour_contenu(json.dumps(classification))
            .construis()
        ]


class ClientAlbertFenetreQuatreLots(ClientAlbertMemoire):
    def __init__(self) -> None:
        super().__init__()
        self.barriere = threading.Barrier(6)
        self._verrou_fenetre = threading.Lock()
        self._appels_actifs = 0
        self.maximum_appels_actifs = 0
        self.ids_observes: list[int] = []
        self.nombre_appels = 0

    def recupere_propositions(
        self,
        messages,
        modele=None,
        temperature=None,
        format_reponse=None,
    ):
        if (
            format_reponse
            and format_reponse.get("json_schema", {}).get("name")
            == "qualification_guides"
        ):
            with self._verrou_fenetre:
                self.nombre_appels += 1
                self._appels_actifs += 1
                self.maximum_appels_actifs = max(
                    self.maximum_appels_actifs, self._appels_actifs
                )
            try:
                self.barriere.wait(timeout=5)
                return [
                    un_choix_de_proposition()
                    .ayant_pour_contenu(reponse_qualification_standard(format_reponse))
                    .construis()
                ]
            finally:
                with self._verrou_fenetre:
                    self._appels_actifs -= 1
        ids = identifiants_candidats(format_reponse)
        with self._verrou_fenetre:
            self.nombre_appels += 1
            self._appels_actifs += 1
            self.maximum_appels_actifs = max(
                self.maximum_appels_actifs, self._appels_actifs
            )
            self.ids_observes.extend(ids)
        try:
            if ids:
                self.barriere.wait(timeout=5)
            evaluations = {
                identifiant: classification_preuve_principale() for identifiant in ids
            }
            contenu_reponse = reponse_classification_avec_identifiants_globaux(
                evaluations
            )
            return [
                un_choix_de_proposition()
                .ayant_pour_contenu(contenu_reponse)
                .construis()
            ]
        finally:
            with self._verrou_fenetre:
                self._appels_actifs -= 1
