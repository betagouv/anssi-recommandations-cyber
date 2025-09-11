import uvicorn
import gradio as gr
import jwt
from datetime import datetime, timedelta, UTC
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
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
    retour: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
) -> Dict[str, List[Dict[str, Any]]]:
    return client_albert.recherche_paragraphes(retour.question)


@app.post("/pose_question")
def route_pose_question(
    retour: QuestionRequete,
    client_albert: ClientAlbert = Depends(fabrique_client_albert),
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
    reponse_http: Response = None,
) -> ReponseQuestion:
    reponse_question = client_albert.pose_question(retour.question)
    id_interaction = adaptateur_base_de_donnes.sauvegarde_interaction(reponse_question)

    if reponse_http is not None:
        configuration = recupere_configuration()
        payload = {
            "interaction_id": id_interaction,
            "exp": datetime.now(UTC)
            + timedelta(hours=configuration["JWT_HEURE_EXPIRATION"]),
        }
        token = jwt.encode(payload, configuration["JWT_CLE_SECRETE"], algorithm="HS256")
        reponse_http.set_cookie(
            key="interaction_token",
            value=token,
            httponly=True,
            secure=configuration["JWT_COOKIES_SECURISE"],
            samesite="strict",
        )
    return reponse_question


@app.post("/retour")
def route_retour(
    retour: RetourUtilisatrice,
    http_retour: Request,
    adaptateur_base_de_donnes: AdaptateurBaseDeDonnees = Depends(
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ),
) -> Dict[str, Any]:
    token = http_retour.cookies.get("interaction_token")
    if not token:
        raise HTTPException(status_code=400, detail="Token d'interaction manquant")

    try:
        configuration = recupere_configuration()
        payload = jwt.decode(
            token, configuration["JWT_CLE_SECRETE"], algorithms=["HS256"]
        )
        id_interaction = payload["interaction_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

    succes = adaptateur_base_de_donnes.ajoute_retour_utilisatrice(
        id_interaction, retour
    )

    if not succes:
        raise HTTPException(status_code=404, detail="Interaction non trouvée")

    return {"succes": True, "commentaire": retour.commentaire}


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
