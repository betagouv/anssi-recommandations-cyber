import os
from typing_extensions import NamedTuple
from enum import StrEnum, auto

# `mypy` ne comprend pas les classes imbriquées dans des `NamedTuple` (alors que c'est du `Python` valide...);
# _c.f._ https://github.com/python/mypy/issues/15775 .
# mypy: disable-error-code="misc, attr-defined, name-defined"


class Albert(NamedTuple):
    class Client(NamedTuple):
        api_key: str
        base_url: str

    class Parametres(NamedTuple):
        modele_reponse: str
        collection_nom_anssi_lab: str
        collection_id_anssi_lab: int
        temps_reponse_maximum_pose_question: float

    client: Client
    parametres: Parametres


class BaseDeDonnees(NamedTuple):
    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    nom: str


class Mode(StrEnum):
    DEVELOPPEMENT = auto()
    TEST = auto()
    PRODUCTION = auto()


class Configuration(NamedTuple):
    albert: Albert
    base_de_donnees: BaseDeDonnees
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
        ),
        parametres=Albert.Parametres(
            modele_reponse=os.getenv("ALBERT_MODELE", "albert-large"),
            collection_nom_anssi_lab=os.getenv(
                "COLLECTION_NOM_ANSSI_LAB", "ANSSI_test"
            ),
            collection_id_anssi_lab=int(os.getenv("COLLECTION_ID_ANSSI_LAB", "4242")),
            temps_reponse_maximum_pose_question=float(
                os.getenv("ALBERT_DELAI_REPONSE_MAXIMUM_REPONSE_QUESTION", 15.0)
            ),
        ),
    )

    configuration_base_de_donnees = recupere_configuration_postgres(
        os.getenv("DB_NAME", "anssi_retours")
    )
    mode = Mode(os.getenv("MODE", "production"))

    return Configuration(
        albert=configuration_albert,
        base_de_donnees=configuration_base_de_donnees,
        hote=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        mode=mode,
    )
