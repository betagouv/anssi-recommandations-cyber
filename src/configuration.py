import logging
import os
from typing_extensions import NamedTuple, Optional
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
        utilise_recherche_hybride: bool
        decalage_index_Albert_et_numero_de_page_lecteur: int

    class Service(NamedTuple):
        collection_nom_anssi_lab: str
        collection_id_anssi_lab: int
        reclassement_active: bool
        modele_reclassement: str

    client: Client
    service: Service


class BaseDeDonnees(NamedTuple):
    hote: str
    port: int
    utilisateur: str
    mot_de_passe: str
    nom: str


class Chiffrement(NamedTuple):
    clef_chiffrement: str | None
    sel_de_hachage: str


class Mode(StrEnum):
    DEVELOPPEMENT = auto()
    TEST = auto()
    PRODUCTION = auto()


class Configuration(NamedTuple):
    albert: Albert
    base_de_donnees: BaseDeDonnees
    base_de_donnees_journal: Optional[BaseDeDonnees]
    chiffrement: Chiffrement
    hote: str
    port: int
    mode: Mode
    max_requetes_par_minute: int


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


def recupere_configuration_journal(mode: Mode) -> Optional[BaseDeDonnees]:
    return (
        BaseDeDonnees(
            hote=os.getenv("DB_JOURNAL_HOST", "localhost"),
            port=int(os.getenv("DB_JOURNAL_PORT", "5432")),
            utilisateur=os.getenv("DB_JOURNAL_USER", "postgres"),
            mot_de_passe=os.getenv("DB_JOURNAL_PASSWORD", "postgres"),
            nom=os.getenv("DB_JOURNAL_NAME", "journal"),
        )
        if os.getenv("DB_JOURNAL_HOST") and mode == Mode.PRODUCTION
        else None
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
            utilise_recherche_hybride=bool(
                os.getenv("ALBERT_UTILISE_RECHERCHE_HYBRIDE", False)
            ),
            decalage_index_Albert_et_numero_de_page_lecteur=int(
                os.getenv("DECALAGE_INDEX_ALBERT_ET_NUMERO_DE_PAGE_LECTEUR", 0)
            ),
        ),
        service=Albert.Service(
            collection_nom_anssi_lab=os.getenv(
                "COLLECTION_NOM_ANSSI_LAB", "ANSSI_test"
            ),
            collection_id_anssi_lab=int(os.getenv("COLLECTION_ID_ANSSI_LAB", "4242")),
            reclassement_active=bool(os.getenv("RECLASSEMENT_ACTIVE", False)),
            modele_reclassement=os.getenv("MODELE_RECLASSEMENT", "openweight-rerank"),
        ),
    )

    configuration_base_de_donnees = recupere_configuration_postgres(
        os.getenv("DB_NAME", "anssi_retours")
    )

    mode = Mode(os.getenv("MODE", "production"))

    configuration_base_de_donnees_journal = recupere_configuration_journal(mode)

    configuration_chiffrement = Chiffrement(
        sel_de_hachage=os.getenv("CHIFFREMENT_SEL_DE_HASHAGE", ""),
        clef_chiffrement=os.getenv("CHIFFREMENT_CLEF_DE_CHIFFREMENT", None),
    )

    return Configuration(
        albert=configuration_albert,
        base_de_donnees=configuration_base_de_donnees,
        base_de_donnees_journal=configuration_base_de_donnees_journal,
        chiffrement=configuration_chiffrement,
        hote=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        mode=mode,
        max_requetes_par_minute=int(
            os.getenv("SERVEUR_MAX_REQUETES_PAR_MINUTE", "600")
        ),
    )
