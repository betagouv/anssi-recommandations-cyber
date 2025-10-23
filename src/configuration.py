import logging
import os
from typing_extensions import NamedTuple
from enum import StrEnum, auto

# `mypy` ne comprend pas les classes imbriquées dans des `NamedTuple` (alors que c'est du `Python` valide...);
# _c.f._ https://github.com/python/mypy/issues/15775 .
# mypy: disable-error-code="misc, attr-defined, name-defined"


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class Albert(NamedTuple):
    class Client(NamedTuple):
        api_key: str
        base_url: str
        modele_reponse: str
        temps_reponse_maximum_pose_question: float
        temps_reponse_maximum_recherche_paragraphes: float

    class Service(NamedTuple):
        collection_nom_anssi_lab: str
        collection_id_anssi_lab: int

    client: Client
    service: Service


class BaseDeDonnees(NamedTuple):
    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    nom: str


class Chiffrement(NamedTuple):
    sel_de_hachage: str


class Mode(StrEnum):
    DEVELOPPEMENT = auto()
    TEST = auto()
    PRODUCTION = auto()


class Configuration(NamedTuple):
    albert: Albert
    base_de_donnees: BaseDeDonnees
    chiffrement: Chiffrement
    hote: str
    port: int
    mode: Mode


def recupere_configuration_postgres(
    database: str = "postgres",
) -> BaseDeDonnees:
    return BaseDeDonnees(
        hote=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        utilisateur=os.getenv("DB_USER", "postgres"),
        mot_de_passe=os.getenv("DB_PASSWORD", "postgres"),
        nom=database,
    )


def recupere_configuration() -> Configuration:
    configuration_albert = Albert(
        client=Albert.Client(
            base_url="https://albert.api.etalab.gouv.fr/v1",
            api_key=os.getenv("ALBERT_API_KEY"),
            modele_reponse=os.getenv("ALBERT_MODELE", "albert-large"),
            temps_reponse_maximum_pose_question=float(
                os.getenv("ALBERT_DELAI_REPONSE_MAXIMUM_REPONSE_QUESTION", 15.0)
            ),
            temps_reponse_maximum_recherche_paragraphes=float(
                os.getenv("ALBERT_DELAI_REPONSE_MAXIMUM_RECHERCHE_PARAGRAPHES", 3.0)
            ),
        ),
        service=Albert.Service(
            collection_nom_anssi_lab=os.getenv(
                "COLLECTION_NOM_ANSSI_LAB", "ANSSI_test"
            ),
            collection_id_anssi_lab=int(os.getenv("COLLECTION_ID_ANSSI_LAB", "4242")),
        ),
    )

    configuration_base_de_donnees = recupere_configuration_postgres(
        os.getenv("DB_NAME", "anssi_retours")
    )

    configuration_chiffrement = Chiffrement(
        sel_de_hachage=os.getenv("CHIFFREMENT_SEL_DE_HASHAGE", "")
    )

    mode = Mode(os.getenv("MODE", "production"))

    return Configuration(
        albert=configuration_albert,
        base_de_donnees=configuration_base_de_donnees,
        chiffrement=configuration_chiffrement,
        hote=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        mode=mode,
    )
