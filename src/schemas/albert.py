from pydantic import BaseModel
from typing import NamedTuple, Optional
from schemas.violations import Violation


class Paragraphe(BaseModel):
    score_similarite: float
    score_reclassement: float = 1.0
    numero_page: int
    url: str
    nom_document: str
    contenu: str
    reponse: str = ""
    est_maitrisee: bool = False


class ReponseQuestion(BaseModel):
    reponse: str
    paragraphes: list[Paragraphe]
    question: str
    question_reformulee: str | None
    violation: Optional[Violation]


class RecherchePayload(NamedTuple):
    collection_ids: list[int]
    limit: int
    prompt: str
    method: str


class ReclassePayload(NamedTuple):
    query: str
    documents: list[str]
    model: str


class RechercheMetadonnees(NamedTuple):
    source_url: str
    page: int
    nom_document: str
    reponse: Optional[str] = None


class RechercheMetadonneesJeopardy(NamedTuple):
    source_id_document: str
    source_id_chunk: int
    source_numero_page: int


class RechercheChunk(NamedTuple):
    content: str
    metadata: RechercheMetadonnees


class RechercheChunkJeopardy(NamedTuple):
    content: str
    metadata: RechercheMetadonneesJeopardy


class ResultatRecherche(NamedTuple):
    chunk: RechercheChunk
    score: float


class ResultatRechercheJeopardy(NamedTuple):
    chunk: RechercheChunkJeopardy
    score: float


class RechercheReponse(NamedTuple):
    object: str
    data: list[ResultatRecherche]
    usage: Optional[dict]


class ResultatReclasse(BaseModel):
    object: str = "rerank"
    score: float
    index: int


class ReclasseReponse(BaseModel):
    data: list[ResultatReclasse]

    class Config:
        extra = "allow"
