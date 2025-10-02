import html
from pathlib import Path
import gradio as gr
from fastapi.testclient import TestClient
from typing import Optional, Tuple


def _lit_prompt_defaut() -> str:
    try:
        p = Path("./templates/prompt_assistant_cyber.txt")
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def pose_question_gradio(
    question: str, app, prompt_txt: Optional[str]
) -> Tuple[str, str, str]:
    """Interface Gradio pour poser une question à Albert via TestClient."""
    if not question.strip():
        return "Veuillez saisir une question", "", ""

    try:
        client = TestClient(app)
        payload = {"question": question}
        if prompt_txt:
            payload["prompt"] = prompt_txt
        reponse_client = client.post("/api/pose_question_avec_prompt", json=payload)
        if reponse_client.status_code != 200:
            return f"Erreur {reponse_client.status_code}", "", ""

        donnees = reponse_client.json()

        interaction_id = donnees.get("interaction_id", "")

        sources_html = (
            """
        <div style="margin:0 0 12px 0;">
          <h3 style="margin:0;color:#ddd;">Sources consultées pour générer la réponse</h3>
        </div>
        """.strip()
            + "\n"
        )

        # Construction des sources en HTML échappé pour éviter tout rendu Markdown.
        for i, paragraphe in enumerate(donnees.get("paragraphes", []), 1):
            url = paragraphe.get("url", "") or ""
            page = (
                paragraphe.get("numero_page", "") + 1
            )  # +1 car la page de garde ne semble pas être comptée côté Albert (il faut donc ajouter +1)
            url_avec_page = f"{url}#page={page}" if url else ""
            score = paragraphe.get("score_similarite", 0.0)
            nom_doc = paragraphe.get("nom_document", "document")
            contenu = paragraphe.get("contenu", "")

            sources_html += (
                f"""
                <div style="padding:12px;border:1px solid #333;border-radius:8px;margin-bottom:12px;background:#111;">
                  <div><strong>Score de pertinence:</strong> {score:.3f}</div>
                  <div><strong>Document:</strong> <a href="{html.escape(url_avec_page)}" target="_blank" rel="noopener">
                    {html.escape(nom_doc)}
                  </a></div>
                  <div><strong>Page:</strong> {html.escape(str(page))}</div>
                  <div style="margin-top:8px"><strong>Contenu:</strong></div>
                  <div style="white-space:pre-wrap">{html.escape(contenu)}</div>
                </div>
                """.strip()
                + "\n"
            )

        return donnees.get("reponse", ""), sources_html, interaction_id

    except Exception as e:
        return f"Erreur : {str(e)}", "", ""


def cree_interface_gradio(app):
    css_cache_footer = "footer { display: none !important; }"
    with gr.Blocks(title="🔐 Assistant Cyber ANSSI", css=css_cache_footer) as interface:
        gr.Markdown("# 🔐 Assistant Cyber ANSSI")

        # Champ d'instructions plein largeur, prérempli depuis le fichier
        prompt_input = gr.Textbox(
            label="Instructions (optionnel)",
            value=_lit_prompt_defaut(),
            lines=12,
            placeholder="Collez ici vos instructions pour surcharger le prompt système…",
        )

        gr.Markdown(
            "Posez vos questions sur la cybersécurité basées sur les guides de l'ANSSI"
        )

        question_input = gr.Textbox(
            label="Votre question",
            placeholder="Quelle est la bonne longueur pour un mot de passe ?",
            lines=2,
        )

        bouton_envoye = gr.Button("Poser la question", variant="primary")

        with gr.Row():
            with gr.Column():
                reponse_output = gr.Textbox(
                    label="Réponse", lines=10, interactive=False
                )
            with gr.Column():
                sources = gr.HTML(label="Sources consultées")

        with gr.Group(visible=False) as retour_utilisatrice_section:
            gr.Markdown("### Votre avis sur cette réponse")
            with gr.Row():
                pouce_haut_btn = gr.Button("👍 Utile", variant="secondary")
                pouce_bas_btn = gr.Button("👎 Pas utile", variant="secondary")
            commentaire_saisi = gr.Textbox(
                label="Commentaire (optionnel)",
                placeholder="Dites-nous ce que vous pensez de cette réponse...",
                lines=2,
            )
            envoyer_retour_utilisatrice_btn = gr.Button(
                "Envoyer le retour", variant="primary"
            )
            retour_utilisatrice_status = gr.HTML()

        interaction_id_etat = (
            gr.State()
        )  # permet de conserver cette valeur tant que la page n'est pas rafraîchie

        def pose_question_avec_retour_utilisatrice(
            question: str, prompt_txt: Optional[str]
        ):
            reponse, sources, interaction_id = pose_question_gradio(
                question, app, prompt_txt
            )
            return reponse, sources, gr.Group(visible=True), interaction_id, ""

        bouton_envoye.click(
            fn=pose_question_avec_retour_utilisatrice,
            inputs=[question_input, prompt_input],
            outputs=[
                reponse_output,
                sources,
                retour_utilisatrice_section,
                interaction_id_etat,
                retour_utilisatrice_status,
            ],
        )

        def envoyer_retour_utilisatrice(
            interaction_id: str, pouce_leve: bool, commentaire: str
        ):
            if not interaction_id:
                return "Erreur : Aucune interaction à évaluer"
            try:
                client = TestClient(app)
                payload = {
                    "id_interaction_rattachee": interaction_id,
                    "retour": {
                        "type": "positif" if pouce_leve else "negatif",
                        "commentaire": (commentaire.strip() or None)
                        if commentaire is not None
                        else None,
                    },
                }
                response = client.post("/api/retour", json=payload)

                if response.status_code == 200:
                    return "✅ Merci pour votre retour !"
                else:
                    return f"❌ Erreur lors de l'envoi : {response.status_code}"
            except Exception as e:
                return f"❌ Erreur : {str(e)}"

        pouce_haut_btn.click(
            fn=lambda _id, comm: envoyer_retour_utilisatrice(_id, True, comm),
            inputs=[interaction_id_etat, commentaire_saisi],
            outputs=[retour_utilisatrice_status],
        )
        pouce_bas_btn.click(
            fn=lambda _id, comm: envoyer_retour_utilisatrice(_id, False, comm),
            inputs=[interaction_id_etat, commentaire_saisi],
            outputs=[retour_utilisatrice_status],
        )
        envoyer_retour_utilisatrice_btn.click(
            fn=lambda _id, comm: envoyer_retour_utilisatrice(_id, True, comm),
            inputs=[interaction_id_etat, commentaire_saisi],
            outputs=[retour_utilisatrice_status],
        )

    return interface
