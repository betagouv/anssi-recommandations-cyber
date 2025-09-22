import os
from typing import Dict, Union
from typing_extensions import NamedTuple


class Albert(NamedTuple):
    base_url: str
    modele_reponse: str
    api_key: str
    collection_nom_anssi_lab: str
    collection_id_anssi_lab: int


class BaseDeDonnees(NamedTuple):
    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    nom: str


class Configuration(NamedTuple):
    albert: Albert
    base_de_donnees: BaseDeDonnees
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

    albert_cfg = Albert(
        base_url=base_url_albert,
        modele_reponse=modele_reponse_albert,
        api_key=albert_api_key,
        collection_nom_anssi_lab=collection_nom_anssi_lab,
        collection_id_anssi_lab=collection_id_anssi_lab,
    )

    bdd_cfg = BaseDeDonnees(
        hote=hote_bdd,
        port=port_bdd,
        utilisateur=utilisateur_bdd,
        mot_de_passe=mot_de_passe_bdd,
        nom=nom_bdd,
    )

    return Configuration(
        albert=albert_cfg,
        base_de_donnees=bdd_cfg,
        host=host,
        port=port,
    )
