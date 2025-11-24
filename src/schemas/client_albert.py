from datetime import datetime
import http
from pydantic import BaseModel
from typing import Literal, NamedTuple, Optional

from schemas.violations import Violation


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
    violation: Optional[Violation]


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


class UneConsommation(NamedTuple):
    completion_tokens: float
    cost: float
    datetime: datetime
    duration: int
    endpoint: str
    id: int
    kgco2eq_max: float
    kgco2eq_min: float
    kwh_max: float
    kwh_min: float
    method: http.HTTPMethod
    model: str
    prompt_tokens: int
    request_model: str
    status: http.HTTPStatus
    time_to_first_token: Optional[int]
    token_id: int
    total_tokens: int
    user_id: int


class ConsommationReponse(BaseModel):
    object: Literal["list"]
    data: list[UneConsommation]
    total: int
    total_requests: int
    total_albert_coins: float
    total_tokens: int
    total_co2: float
    page: int
    limit: int
    total_pages: int
    has_more: bool
