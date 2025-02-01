import express, {Express, Request, Response} from "express";
import {ReponseAPIAlbert} from "./types";

const app: Express = express();
const port = process.env.PORT;

app.use(express.json());
app.use(express.static('public'));

app.post("/api/demande", async (requete: Request, reponse: Response) => {
    const demandeUtilisateur = requete.body.demande;
    const k = 3;
    const donneesRAG = await fetch(`${process.env.ALBERT_URL_BASE}/v1/search`, {
        method: 'post',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${process.env.ALBERT_CLE_API}`
        },
        body: JSON.stringify({
            k,
            collections: [process.env.ALBERT_ID_COLLECTION_DOCUMENT],
            prompt: demandeUtilisateur
        })
    });
    const jsonRAG: ReponseAPIAlbert = await donneesRAG.json();
    const chunksRAG = jsonRAG.data.map(d => d.chunk.content).join("\n\n\n");
    const sources = [...new Set(jsonRAG.data.map(d => d.chunk.metadata.document_name))];
    const scoreMoyen = jsonRAG.data.reduce((acc, val) => acc + val.score, 0) / jsonRAG.data.length;

    try {
        reponse.setHeader("Content-Type", "text/event-stream");
        reponse.setHeader("Cache-Control", "no-cache");
        reponse.setHeader("Connection", "keep-alive");
        reponse.setHeader("x-sources", JSON.stringify(sources));
        reponse.setHeader("x-score-moyen", JSON.stringify(scoreMoyen));

        const donneesLLM = await fetch(`${process.env.ALBERT_URL_BASE}/v1/chat/completions`, {
            method: 'post',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                Authorization: `Bearer ${process.env.ALBERT_CLE_API}`
            },
            body: JSON.stringify({
                messages: [
                    {
                        role: 'system',
                        content: 'Tu réponds à des questions en te basant sur des documents. Certaines recommandations sont annotées (RXX), si possible, merci de les citer. Merci de résumer ta réponse à la fin.'
                    },
                    {role: 'user', content: `Question: ${demandeUtilisateur}\nDocuments: ${chunksRAG}`}
                ],
                model: 'AgentPublic/llama3-instruct-8b',
                stream: true,
                n: 1
            })
        });

        if (!donneesLLM.ok || !donneesLLM.body) {
            reponse.status(donneesLLM.status).json({error: "Erreur de connexion à l'API Albert"});
            return;
        }

        const lecteur = donneesLLM.body.getReader();
        const decodeur = new TextDecoder();

        let chunkIncomplet = '';
        while (true) {
            const {value, done} = await lecteur.read();
            if (done) break;

            let chunk = decodeur.decode(value, {stream: true});
            if (chunkIncomplet) {
                chunk = chunkIncomplet + chunk;
                chunkIncomplet = '';
            }

            for (const line of chunk.split("\n").filter(l => l)) {
                if (line.startsWith("data:")) {
                    const donneesJSON = line.substring(5).trim();
                    if (donneesJSON && donneesJSON !== "[DONE]") {
                        try {
                            const donnees = JSON.parse(donneesJSON);
                            const contenu = donnees.choices?.[0]?.delta?.content || "";
                            reponse.write(contenu);
                        } catch (error) {
                            chunkIncomplet += line;
                        }
                    }
                } else {
                    chunkIncomplet += line;
                }
            }
        }

        reponse.end();
    } catch (error) {
        reponse.status(500).json({ error: "Erreur interne du serveur" });
    }
});

app.listen(port, () => {
    console.log(`Le serveur est lancé sur le port ${port}`);
});