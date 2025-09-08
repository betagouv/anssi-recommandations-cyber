import os

BASE_URL_ALBERT: str = "https://albert.api.etalab.gouv.fr/v1"
COLLECTION_ID_ANSSI_LAB: int = 1954
COLLECTION_NOM_ANSSI_LAB: str = "ANSSI_test"
MODELE_REPONSE_ALBERT: str = "albert-large"

HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "8000"))

ALBERT_API_KEY: str = os.getenv("ALBERT_API_KEY")
assert ALBERT_API_KEY, "ALBERT_API_KEY doit être définie"
