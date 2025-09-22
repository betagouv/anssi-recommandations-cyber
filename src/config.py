import os
from typing import Dict, Union
from typing_extensions import NamedTuple


class Configuration(NamedTuple):
    BASE_URL_ALBERT: str
    COLLECTION_NOM_ANSSI_LAB: str
    MODELE_REPONSE_ALBERT: str
    HOST: str
    PORT: int
    COLLECTION_ID_ANSSI_LAB: int
    ALBERT_API_KEY: str
    HOTE_BDD: str
    PORT_BDD: int
    NOM_BDD: str
    UTILISATEUR_BDD: str
    MOT_DE_PASSE_BDD: str


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

    return Configuration(
        BASE_URL_ALBERT=BASE_URL_ALBERT,
        COLLECTION_NOM_ANSSI_LAB=COLLECTION_NOM_ANSSI_LAB,
        MODELE_REPONSE_ALBERT=MODELE_REPONSE_ALBERT,
        HOST=HOST,
        PORT=PORT,
        COLLECTION_ID_ANSSI_LAB=COLLECTION_ID_ANSSI_LAB,
        ALBERT_API_KEY=ALBERT_API_KEY,
        HOTE_BDD=HOTE_BDD,
        PORT_BDD=PORT_BDD,
        NOM_BDD=NOM_BDD,
        UTILISATEUR_BDD=UTILISATEUR_BDD,
        MOT_DE_PASSE_BDD=MOT_DE_PASSE_BDD,
    )
