import os

BASE_URL_ALBERT: str = "https://albert.api.etalab.gouv.fr/v1"
ALBERT_API_KEY: str = os.getenv("ALBERT_API_KEY")
assert ALBERT_API_KEY, "ALBERT_API_KEY doit être définie"
