import os


def recupere_configuration():
    BASE_URL_ALBERT: str = "https://albert.api.etalab.gouv.fr/v1"
    COLLECTION_NOM_ANSSI_LAB: str = "ANSSI_test"
    MODELE_REPONSE_ALBERT: str = "albert-large"

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    COLLECTION_ID_ANSSI_LAB: int = int(os.getenv("COLLECTION_ID_ANSSI_LAB"))
    ALBERT_API_KEY: str = os.getenv("ALBERT_API_KEY")

    HOTE_BD: str = os.getenv("DB_HOST", "localhost")
    PORT_BD: int = int(os.getenv("DB_PORT", "5432"))
    NOM_BD: str = os.getenv("DB_NAME", "anssi_retours")
    UTILISATEUR_BD: str = os.getenv("DB_USER")
    MOT_DE_PASSE_BD: str = os.getenv("DB_PASSWORD")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    JWT_SECURE_COOKIES: bool = bool(os.getenv("JWT_SECURE_COOKIES").lower())
    GRADIO_ADMIN_USER: str = os.getenv("GRADIO_ADMIN_USER")
    GRADIO_ADMIN_PASSWORD: str = os.getenv("GRADIO_ADMIN_PASSWORD")

    return {
        "BASE_URL_ALBERT": BASE_URL_ALBERT,
        "COLLECTION_NOM_ANSSI_LAB": COLLECTION_NOM_ANSSI_LAB,
        "MODELE_REPONSE_ALBERT": MODELE_REPONSE_ALBERT,
        "HOST": HOST,
        "PORT": PORT,
        "COLLECTION_ID_ANSSI_LAB": COLLECTION_ID_ANSSI_LAB,
        "ALBERT_API_KEY": ALBERT_API_KEY,
        "HOTE_BD": HOTE_BD,
        "PORT_BD": PORT_BD,
        "NOM_BD": NOM_BD,
        "UTILISATEUR_BD": UTILISATEUR_BD,
        "MOT_DE_PASSE_BD": MOT_DE_PASSE_BD,
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
        "JWT_EXPIRATION_HOURS": JWT_EXPIRATION_HOURS,
        "JWT_SECURE_COOKIES": JWT_SECURE_COOKIES,
        "GRADIO_ADMIN_USER": GRADIO_ADMIN_USER,
        "GRADIO_ADMIN_PASSWORD": GRADIO_ADMIN_PASSWORD,
    }
