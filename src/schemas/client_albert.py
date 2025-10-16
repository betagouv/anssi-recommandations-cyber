from pydantic import BaseModel
from typing import NamedTuple, Optional


class Paragraphe(BaseModel):
    score_similarite: float
    numero_page: int
    url: str
    nom_document: str
    contenu: str


class ReponseQuestion(BaseModel):
    reponse: str
    paragraphes: list[Paragraphe]
    question: str


class RecherchePayload(NamedTuple):
    collections: list[int]
    k: int
    prompt: str
    method: str


class RechercheMetadonnees(NamedTuple):
    source_url: str
    page: int
    nom_document: str


class RechercheChunk(NamedTuple):
    content: str
    metadata: RechercheMetadonnees


class ResultatRecherche(NamedTuple):
    chunk: RechercheChunk
    score: float


class RechercheReponse(NamedTuple):
    object: str
    data: list[ResultatRecherche]
    usage: Optional[dict]
