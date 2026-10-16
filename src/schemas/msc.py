from pydantic import BaseModel


class DocumentGuideMSC(BaseModel):
    libelle: str
    nomFichier: str


class ReponseGuideMSC(BaseModel):
    id: str
    nom: str
    description: str
    listeDocuments: list[DocumentGuideMSC]
    dateMiseAJour: str
