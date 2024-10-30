import express, {Express, Request, Response} from "express";
import dotenv from "dotenv";
import {ReponseAPIAlbert} from "./types";

dotenv.config();

const app: Express = express();
const port = process.env.PORT;

app.use(express.json());
app.use(express.static('public'));

app.post("/api/demande", async (requete: Request, reponse: Response) => {
    const donnees = await fetch(`${process.env.ALBERT_URL_BASE}/v1/search`, {
        method: 'post',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${process.env.ALBERT_CLE_API}`
        },
        body: JSON.stringify({
            k: 3,
            collections: [process.env.ALBERT_ID_COLLECTION_DOCUMENT],
            prompt: `${requete.body.demande} Merci de citer tes sources`
        })
    });

    const json: ReponseAPIAlbert = await donnees.json();

    const donneesReponse = json.data.map((d) => ({
        score: d.score,
        contenu: d.chunk.content,
        document: d.chunk.metadata.document_name
    }));

    reponse.send(donneesReponse);
});

app.listen(port, () => {
    console.log(`Le serveur est lancé sur le port ${port}`);
});