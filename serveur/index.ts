import express, {Express, Request, Response} from "express";
import dotenv from "dotenv";
import {ReponseAPIAlbert} from "./types";

dotenv.config();

const app: Express = express();
const port = process.env.PORT;

app.use(express.json());
app.use(express.static('public'));

app.post("/api/demande", async (requete: Request, reponse: Response) => {
    const demandeUtilisateur = requete.body.demande;
    const donneesRAG = await fetch(`${process.env.ALBERT_URL_BASE}/v1/search`, {
        method: 'post',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${process.env.ALBERT_CLE_API}`
        },
        body: JSON.stringify({
            k: 3,
            collections: [process.env.ALBERT_ID_COLLECTION_DOCUMENT],
            prompt: demandeUtilisateur
        })
    });
    const jsonRAG: ReponseAPIAlbert = await donneesRAG.json();
    const chunksRAG = jsonRAG.data.map(d => d.chunk.content).join("\n\n\n");
    const sources = [...new Set(jsonRAG.data.map(d => d.chunk.metadata.document_name))];

    const prompt = `Réponds à la question suivante en te basant sur les documents ci-dessous : ${demandeUtilisateur}\n\nDocuments :\n\n${chunksRAG}`;
    const donneesLLM = await fetch(`${process.env.ALBERT_URL_BASE}/v1/chat/completions`, {
        method: 'post',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${process.env.ALBERT_CLE_API}`
        },
        body: JSON.stringify({
            messages: [{role: 'user', content: prompt}],
            model: 'AgentPublic/llama3-instruct-8b',
            stream: false,
            n: 1
        })
    });


    const donneesReponse = await donneesLLM.json();

    reponse.send({
        reponse: donneesReponse.choices[0].message.content,
        sources
    });
});

app.listen(port, () => {
    console.log(`Le serveur est lancé sur le port ${port}`);
});