import os
from typing import Dict, Union
from typing_extensions import NamedTuple


class ConfigurationAlbert(NamedTuple):
    base_url_albert: str
    modele_reponse_albert: str
    albert_api_key: str
    collection_nom_anssi_lab: str
    collection_id_anssi_lab: int


class ConfigurationBDD(NamedTuple):
    hote_bdd: str
    port_bdd: int
    utilisateur_bdd: str
    mot_de_passe_bdd: str
    nom_bdd: str


class Configuration(NamedTuple):
    configuration_albert: ConfigurationAlbert
    configuration_base_de_donnees: ConfigurationBDD
    host: str
    port: int


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
    base_url_albert: str = "https://albert.api.etalab.gouv.fr/v1"
    collection_nom_anssi_lab: str = "ANSSI_test"
    modele_reponse_albert: str = "albert-large"

    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))

    collection_id_anssi_lab: int = int(os.getenv("COLLECTION_ID_ANSSI_LAB"))
    albert_api_key: str = os.getenv("ALBERT_API_KEY")

    config_postgres = recupere_configuration_postgres(
        os.getenv("DB_NAME", "anssi_retours")
    )
    hote_bdd: str = config_postgres["host"]
    port_bdd: int = config_postgres["port"]
    nom_bdd: str = config_postgres["database"]
    utilisateur_bdd: str = config_postgres["user"]
    mot_de_passe_bdd: str = config_postgres["password"]

    albert_cfg = ConfigurationAlbert(
        base_url_albert=base_url_albert,
        modele_reponse_albert=modele_reponse_albert,
        albert_api_key=albert_api_key,
        collection_nom_anssi_lab=collection_nom_anssi_lab,
        collection_id_anssi_lab=collection_id_anssi_lab,
    )

    bdd_cfg = ConfigurationBDD(
        hote_bdd=hote_bdd,
        port_bdd=port_bdd,
        utilisateur_bdd=utilisateur_bdd,
        mot_de_passe_bdd=mot_de_passe_bdd,
        nom_bdd=nom_bdd,
    )

    return Configuration(
        configuration_albert=albert_cfg,
        configuration_base_de_donnees=bdd_cfg,
        host=host,
        port=port,
    )
