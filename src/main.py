import uvicorn
import gradio as gr
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict, List, Any
from client_albert import ClientAlbert
from schemas.requetes import QuestionRequete
from config import recupere_configuration
from schemas.reponses import ReponseQuestion
from gradio_app import cree_interface_gradio
from adaptateurs import AdaptateurBaseDeDonnees, AdaptateurBaseDeDonneesPostgres
from schemas.retour_utilisatrice import RetourUtilisatrice


app: FastAPI = FastAPI()

interface_gradio = cree_interface_gradio(app)
app = gr.mount_gradio_app(app, interface_gradio, path="/ui")


def fabrique_client_albert() -> ClientAlbert:
    return ClientAlbert()


def fabrique_adaptateur_base_de_donnees_retour_utilisatrice() -> (
    AdaptateurBaseDeDonnees
):
    return AdaptateurBaseDeDonneesPostgres(recupere_configuration()["NOM_BDD"])


@app.get("/sante")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/recherche")
def route_recherche(
    request: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
) -> Dict[str, List[Dict[str, Any]]]:
    return client_albert.recherche_paragraphes(request.question)


@app.post("/pose_question")
def route_pose_question(
    request: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> ReponseQuestion:
    reponse_question = client_albert.pose_question(request.question)
    id_interaction = adaptateur_base_de_donnes.sauvegarde_interaction(reponse_question)
    reponse_json = JSONResponse(reponse_question.model_dump())
    reponse_json.headers["X-Interaction-Id"] = id_interaction
    return reponse_json


@app.post("/retour/{interaction_id}")
def route_retour(
    interaction_id: str,
    request: RetourUtilisatrice,
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> Dict[str, Any]:
    retour = RetourUtilisatrice(
        pouce_leve=request.pouce_leve, commentaire=request.commentaire
    )
    succes = adaptateur_base_de_donnes.ajoute_retour_utilisatrice(
        interaction_id, retour
    )

    if not succes:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return {"succes": True, "commentaire": request.commentaire}


@app.get("/")
def redirige_vers_gradio():
    return RedirectResponse("/ui")


if __name__ == "__main__":
    configuration = recupere_configuration()
    HOST = configuration["HOST"]
    PORT = configuration["PORT"]
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
