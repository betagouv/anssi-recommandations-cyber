import os


def recupere_configuration():
    BASE_URL_ALBERT: str = "https://albert.api.etalab.gouv.fr/v1"
    COLLECTION_NOM_ANSSI_LAB: str = "ANSSI_test"
    MODELE_REPONSE_ALBERT: str = "albert-large"

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    COLLECTION_ID_ANSSI_LAB: int = int(os.getenv("COLLECTION_ID_ANSSI_LAB"))
    ALBERT_API_KEY: str = os.getenv("ALBERT_API_KEY")

    HOTE_BDD: str = os.getenv("DB_HOST", "localhost")
    PORT_BDD: int = int(os.getenv("DB_PORT", "5432"))
    NOM_BDD: str = os.getenv("DB_NAME", "anssi_retours")
    UTILISATEUR_BDD: str = os.getenv("DB_USER")
    MOT_DE_PASSE_BDD: str = os.getenv("DB_PASSWORD")

    return {
        "BASE_URL_ALBERT": BASE_URL_ALBERT,
        "COLLECTION_NOM_ANSSI_LAB": COLLECTION_NOM_ANSSI_LAB,
        "MODELE_REPONSE_ALBERT": MODELE_REPONSE_ALBERT,
        "HOST": HOST,
        "PORT": PORT,
        "COLLECTION_ID_ANSSI_LAB": COLLECTION_ID_ANSSI_LAB,
        "ALBERT_API_KEY": ALBERT_API_KEY,
        "HOTE_BDD": HOTE_BDD,
        "PORT_BDD": PORT_BDD,
        "NOM_BDD": NOM_BDD,
        "UTILISATEUR_BDD": UTILISATEUR_BDD,
        "MOT_DE_PASSE_BDD": MOT_DE_PASSE_BDD,
    }
