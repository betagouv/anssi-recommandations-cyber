import logging
import os
from typing_extensions import NamedTuple, Optional, TypedDict
from enum import StrEnum, auto


class VariablesEnvironnementNecessaires(TypedDict):
    ALBERT_API_KEY: str
    ALBERT_MODELE: str
    ALBERT_MODELE_REFORMULATION: str
    COLLECTION_ID_ANSSI_LAB: int
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    CHIFFREMENT_SEL_DE_HACHAGE: str
    CHIFFREMENT_CLEF_DE_CHIFFREMENT: str
    HOST: str
    PORT: int


# `mypy` ne comprend pas les classes imbriquées dans des `NamedTuple` (alors que c'est du `Python` valide...);
# _c.f._ https://github.com/python/mypy/issues/15775 .
# mypy: disable-error-code="misc, attr-defined, name-defined"


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class Albert(NamedTuple):
    class Client(NamedTuple):
        api_key: str
        base_url: str
        modele_reponse: str
        modele_reformulation: str  # TODO: À déplacer dans la configuration service
        temps_reponse_maximum_pose_question: float
        temps_reponse_maximum_recherche_paragraphes: float
        utilise_recherche_hybride: bool
        decalage_index_Albert_et_numero_de_page_lecteur: int

    class Service(NamedTuple):
        collection_nom_anssi_lab: str
        collection_id_anssi_lab: int
        collection_id_anssi_lab_jeopardy: int
        reclassement_active: bool
        modele_reclassement: str
        taille_fenetre_historique: int
        jeopardy_active: bool
        seuil_reponse_maitrisee: float

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


class TypeAdaptateurSentry(StrEnum):
    MEMOIRE = "memoire"
    STANDARD = "standard"


class Sentry(NamedTuple):
    dsn: Optional[str]
    environnement: str
    type_adaptateur_sentry: TypeAdaptateurSentry


class Mode(StrEnum):
    DEVELOPPEMENT = auto()
    TEST = auto()
    PRODUCTION = auto()


class Configuration(NamedTuple):
    albert: Albert
    base_de_donnees: BaseDeDonnees
    base_de_donnees_journal: Optional[BaseDeDonnees]
    chiffrement: Chiffrement
    sentry: Sentry
    hote: str
    port: int
    mode: Mode
    max_requetes_par_minute: int
    est_alpha_test: bool


def _recupere_configuration_postgres(
    variables_environnement: VariablesEnvironnementNecessaires,
) -> BaseDeDonnees:
    return BaseDeDonnees(
        hote=variables_environnement["DB_HOST"],
        port=variables_environnement["DB_PORT"],
        utilisateur=variables_environnement["DB_USER"],
        mot_de_passe=variables_environnement["DB_PASSWORD"],
        nom=variables_environnement["DB_NAME"],
    )


def _recupere_configuration_journal(mode: Mode) -> Optional[BaseDeDonnees]:
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


def _verifie_la_presence_des_variables_d_environnement_necessaires() -> (
    VariablesEnvironnementNecessaires
):
    variables_environnement = _les_variables_d_environnement()
    variables_manquantes = list(
        filter(lambda x: x[1] is None, variables_environnement.items())
    )
    cles_manquantes = list(map(lambda x: x[0], variables_manquantes))
    if len(cles_manquantes) > 0:
        raise Exception(
            f"Les variables d'environnement suivantes sont manquantes :\n - {'\n - '.join(cles_manquantes)}"
        )
    return variables_environnement  # type: ignore


def _les_variables_d_environnement() -> VariablesEnvironnementNecessaires:
    env_db_bort = os.getenv("DB_PORT")
    env_app_port = os.getenv("PORT")
    collection_id_anssi_lab = os.getenv("COLLECTION_ID_ANSSI_LAB")
    variables_environnement: dict[str, str | int | None] = {
        "ALBERT_API_KEY": os.getenv("ALBERT_API_KEY"),
        "ALBERT_MODELE": os.getenv("ALBERT_MODELE"),
        "ALBERT_MODELE_REFORMULATION": os.getenv("ALBERT_MODELE_REFORMULATION"),
        "COLLECTION_ID_ANSSI_LAB": int(collection_id_anssi_lab)
        if collection_id_anssi_lab
        else None,
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": (int(env_db_bort) if env_db_bort else None),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "CHIFFREMENT_SEL_DE_HACHAGE": os.getenv("CHIFFREMENT_SEL_DE_HACHAGE"),
        "CHIFFREMENT_CLEF_DE_CHIFFREMENT": os.getenv("CHIFFREMENT_CLEF_DE_CHIFFREMENT"),
        "HOST": os.getenv("HOST"),
        "PORT": (int(env_app_port) if env_app_port else None),
    }
    return variables_environnement  # type: ignore


def recupere_configuration() -> Configuration:
    mode = Mode(os.getenv("MODE", "production"))
    variables_environnement = (
        _verifie_la_presence_des_variables_d_environnement_necessaires()
        if mode != Mode.TEST and mode != Mode.DEVELOPPEMENT
        else _les_variables_d_environnement()
    )
    configuration_albert = Albert(
        client=Albert.Client(
            base_url="https://albert.api.etalab.gouv.fr/v1",
            api_key=variables_environnement["ALBERT_API_KEY"],
            modele_reponse=variables_environnement["ALBERT_MODELE"],
            modele_reformulation=variables_environnement["ALBERT_MODELE_REFORMULATION"],
            temps_reponse_maximum_pose_question=float(
                os.getenv("ALBERT_DELAI_REPONSE_MAXIMUM_REPONSE_QUESTION", 15.0)
            ),
            temps_reponse_maximum_recherche_paragraphes=float(
                os.getenv("ALBERT_DELAI_REPONSE_MAXIMUM_RECHERCHE_PARAGRAPHES", 3.0)
            ),
            utilise_recherche_hybride=os.getenv(
                "ALBERT_UTILISE_RECHERCHE_HYBRIDE", "false"
            ).lower()
            == "true",
            decalage_index_Albert_et_numero_de_page_lecteur=int(
                os.getenv("DECALAGE_INDEX_ALBERT_ET_NUMERO_DE_PAGE_LECTEUR", 0)
            ),
        ),
        service=Albert.Service(
            collection_nom_anssi_lab=os.getenv(
                "COLLECTION_NOM_ANSSI_LAB", "ANSSI_test"
            ),
            collection_id_anssi_lab=variables_environnement["COLLECTION_ID_ANSSI_LAB"],
            collection_id_anssi_lab_jeopardy=int(
                os.getenv("COLLECTION_ID_ANSSI_LAB_JEOPARDY", "4243")
            ),
            reclassement_active=os.getenv("RECLASSEMENT_ACTIVE", "false").lower()
            == "true",
            modele_reclassement=os.getenv("MODELE_RECLASSEMENT", "openweight-rerank"),
            taille_fenetre_historique=int(
                os.getenv("ALBERT_TAILLE_FENETRE_HISTORIQUE", "10")
            ),
            jeopardy_active=os.getenv("JEOPARDY_ACTIVE", "false").lower() == "true",
            seuil_reponse_maitrisee=float(
                os.getenv("SEUIL_REPONSE_MAITRISEE", "0.8")
            ),
        ),
    )
    configuration_base_de_donnees = _recupere_configuration_postgres(
        variables_environnement
    )

    configuration_base_de_donnees_journal = _recupere_configuration_journal(mode)

    configuration_chiffrement = Chiffrement(
        sel_de_hachage=variables_environnement["CHIFFREMENT_SEL_DE_HACHAGE"],
        clef_chiffrement=variables_environnement["CHIFFREMENT_CLEF_DE_CHIFFREMENT"],
    )

    configuration_sentry = Sentry(
        dsn=os.getenv("SENTRY_DSN"),
        environnement=os.getenv("SENTRY_ENVIRONNEMENT", "developpement"),
        type_adaptateur_sentry=TypeAdaptateurSentry(
            os.getenv("SENTRY_TYPE_ADAPTATEUR", "memoire")
        ),
    )

    return Configuration(
        albert=configuration_albert,
        base_de_donnees=configuration_base_de_donnees,
        base_de_donnees_journal=configuration_base_de_donnees_journal,
        chiffrement=configuration_chiffrement,
        sentry=configuration_sentry,
        hote=variables_environnement["HOST"],
        port=variables_environnement["PORT"],
        mode=mode,
        max_requetes_par_minute=int(
            os.getenv("SERVEUR_MAX_REQUETES_PAR_MINUTE", "600")
        ),
        est_alpha_test=os.getenv("ALPHA_TEST", "false").lower() == "true",
    )
