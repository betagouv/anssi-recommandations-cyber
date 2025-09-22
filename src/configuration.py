import os
from typing import Dict, Union
from typing_extensions import NamedTuple


class ConfigurationAlbert(NamedTuple):
    BASE_URL_ALBERT: str
    MODELE_REPONSE_ALBERT: str
    ALBERT_API_KEY: str
    COLLECTION_NOM_ANSSI_LAB: str
    COLLECTION_ID_ANSSI_LAB: int


class ConfigurationBDD(NamedTuple):
    HOTE_BDD: str
    PORT_BDD: int
    UTILISATEUR_BDD: str
    MOT_DE_PASSE_BDD: str
    NOM_BDD: str


class Configuration(NamedTuple):
    CONFIGURATION_ALBERT: ConfigurationAlbert
    CONFIGURATION_BASE_DE_DONNEES: ConfigurationBDD
    HOST: str
    PORT: int


def recupere_configuration_postgres(
    database: str = "postgres",
) -> Dict[str, Union[str, int]]:
    return dict(
        host=os.getenv("DB_HOST", "localhost"),
        database=database,
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")),
    )


def recupere_configuration() -> Configuration:
    BASE_URL_ALBERT: str = "https://albert.api.etalab.gouv.fr/v1"
    COLLECTION_NOM_ANSSI_LAB: str = "ANSSI_test"
    MODELE_REPONSE_ALBERT: str = "albert-large"

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    COLLECTION_ID_ANSSI_LAB: int = int(os.getenv("COLLECTION_ID_ANSSI_LAB"))
    ALBERT_API_KEY: str = os.getenv("ALBERT_API_KEY")

    config_postgres = recupere_configuration_postgres(
        os.getenv("DB_NAME", "anssi_retours")
    )
    HOTE_BDD: str = config_postgres["host"]
    PORT_BDD: int = config_postgres["port"]
    NOM_BDD: str = config_postgres["database"]
    UTILISATEUR_BDD: str = config_postgres["user"]
    MOT_DE_PASSE_BDD: str = config_postgres["password"]

    albert_cfg = ConfigurationAlbert(
        BASE_URL_ALBERT=BASE_URL_ALBERT,
        MODELE_REPONSE_ALBERT=MODELE_REPONSE_ALBERT,
        ALBERT_API_KEY=ALBERT_API_KEY,
        COLLECTION_NOM_ANSSI_LAB=COLLECTION_NOM_ANSSI_LAB,
        COLLECTION_ID_ANSSI_LAB=COLLECTION_ID_ANSSI_LAB,
    )

    bdd_cfg = ConfigurationBDD(
        HOTE_BDD=HOTE_BDD,
        PORT_BDD=PORT_BDD,
        UTILISATEUR_BDD=UTILISATEUR_BDD,
        MOT_DE_PASSE_BDD=MOT_DE_PASSE_BDD,
        NOM_BDD=NOM_BDD,
    )

    return Configuration(
        CONFIGURATION_ALBERT=albert_cfg,
        CONFIGURATION_BASE_DE_DONNEES=bdd_cfg,
        HOST=HOST,
        PORT=PORT,
    )
