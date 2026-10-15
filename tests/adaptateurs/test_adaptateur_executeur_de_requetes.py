from adaptateurs.adaptateur_executeur_de_requetes import AdaptateurExecuteurDeRequetes
from pydantic import BaseModel


class ModeleFictif(BaseModel):
    pass


class ReponseJsonFictive:
    def raise_for_status(self) -> None:
        pass

    def json(self) -> list:
        return []


class SessionRequetesFictive:
    def __init__(self) -> None:
        self.timeout = None
        self.est_fermee = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback) -> None:
        self.est_fermee = True

    def get(self, url: str, timeout=None) -> ReponseJsonFictive:
        self.timeout = timeout
        return ReponseJsonFictive()


def test_borne_et_ferme_la_session_de_recuperation_http() -> None:
    session = SessionRequetesFictive()
    adaptateur = AdaptateurExecuteurDeRequetes(
        timeout=(5, 10), session_factory=lambda: session
    )

    adaptateur.recupere("https://msc.invalid/api/guides", ModeleFictif)

    assert session.timeout == (5, 10)
    assert session.est_fermee is True
