import uvicorn
import gradio as gr
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Dict, List, Any
from client_albert import ClientAlbert, fabrique_client_albert
from schemas.requetes import QuestionRequete
from configuration import recupere_configuration
from schemas.reponses import ReponseQuestion
from gradio_app import cree_interface_gradio
from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from schemas.retour_utilisatrice import (
    RetourUtilisatrice,
    DonneesCreationRetourUtilisateur,
)


app: FastAPI = FastAPI()

interface_gradio = cree_interface_gradio(app)
app = gr.mount_gradio_app(app, interface_gradio, path="/ui")


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
    body = reponse_question.model_dump()
    body["interaction_id"] = id_interaction
    return JSONResponse(body)


@app.post("/retour")
def route_retour(
    body: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> Dict[str, Any]:
    retour = RetourUtilisatrice(
        pouce_leve=body.retour.pouce_leve, commentaire=body.retour.commentaire
    )
    succes = adaptateur_base_de_donnes.ajoute_retour_utilisatrice(
        body.id_interaction_rattachee, retour
    )

    if not succes:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return {"succes": True, "commentaire": body.retour.commentaire}


@app.get("/")
def redirige_vers_gradio():
    return RedirectResponse("/ui")


if __name__ == "__main__":
    configuration = recupere_configuration()
    HOST = configuration.host
    PORT = configuration.port
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
    )
