import os
from typing import Dict, Union
from typing_extensions import NamedTuple


class Albert(NamedTuple):
    class Client(NamedTuple):
        api_key: str
        base_url: str

    class Parametres(NamedTuple):
        modele_reponse: str
        collection_nom_anssi_lab: str
        collection_id_anssi_lab: int

    client: Client
    parametres: Parametres


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
            modele_reponse="albert-large",
            collection_nom_anssi_lab="ANSSI_test",
            collection_id_anssi_lab=int(os.getenv("COLLECTION_ID_ANSSI_LAB")),
        ),
    )

    configuration_postgres = recupere_configuration_postgres(
        os.getenv("DB_NAME", "anssi_retours")
    )
    configuration_base_de_donnees = BaseDeDonnees(**configuration_postgres)

    return Configuration(
        albert=configuration_albert,
        base_de_donnees=configuration_base_de_donnees,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )
