import html
import gradio as gr
from fastapi.testclient import TestClient


def pose_question_gradio(question: str, app) -> tuple[str, str, str]:
    """Interface Gradio pour poser une question à Albert via TestClient."""
    if not question.strip():
        return "Veuillez saisir une question", "", ""

    try:
        client = TestClient(app)
        response = client.post("/pose_question", json={"question": question})
        if response.status_code != 200:
            return f"Erreur {response.status_code}", "", ""

        data = response.json()

        cookies = response.cookies
        interaction_token = cookies.get("interaction_token", "")

        sources_html = (
            """
        <div style="margin:0 0 12px 0;">
          <h3 style="margin:0;color:#ddd;">Sources consultées pour générer la réponse</h3>
        </div>
        """.strip()
            + "\n"
        )

        # Construction des sources en HTML échappé pour éviter tout rendu Markdown.
        for i, paragraphe in enumerate(data.get("paragraphes", []), 1):
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

        return data.get("reponse", ""), sources_html, interaction_token

    except Exception as e:
        return f"Erreur : {str(e)}", "", ""


def cree_interface_gradio(app):
    css_cache_footer = "footer { display: none !important; }"
    with gr.Blocks(title="🔐 Assistant Cyber ANSSI", css=css_cache_footer) as interface:
        gr.Markdown("# 🔐 Assistant Cyber ANSSI")
        gr.Markdown(
            "Posez vos questions sur la cybersécurité basées sur les guides de l'ANSSI"
        )

        with gr.Row():
            question_input = gr.Textbox(
                label="Votre question",
                placeholder="Quelle est la bonne longueur pour un mot de passe ?",
                lines=2,
            )

        submit_btn = gr.Button("Poser la question", variant="primary")

        with gr.Row():
            with gr.Column():
                reponse_output = gr.Textbox(
                    label="Réponse", lines=10, interactive=False
                )
            with gr.Column():
                sources_output = gr.HTML(label="Sources consultées")

        with gr.Group(visible=False) as retour_utilisatrice_section:
            gr.Markdown("### Votre avis sur cette réponse")
            with gr.Row():
                pouce_haut_btn = gr.Button("👍 Utile", variant="secondary")
                pouce_bas_btn = gr.Button("👎 Pas utile", variant="secondary")
            commentaire_input = gr.Textbox(
                label="Commentaire (optionnel)",
                placeholder="Dites-nous ce que vous pensez de cette réponse...",
                lines=2,
            )
            envoyer_retour_utilisatrice_btn = gr.Button(
                "Envoyer le retour", variant="primary"
            )
            retour_utilisatrice_status = gr.HTML()

        etat_token_interaction = gr.State()

        def pose_question_avec_retour_utilisatrice(question: str):
            reponse, sources, token_interaction = pose_question_gradio(question, app)
            return reponse, sources, gr.Group(visible=True), token_interaction, ""

        def envoyer_retour_utilisatrice(
            token_interaction: str, pouce_leve: bool, commentaire: str
        ):
            if not token_interaction:
                return "Erreur : Aucune interaction à évaluer"

            try:
                client = TestClient(app)
                payload = {
                    "pouce_leve": pouce_leve,
                    "commentaire": commentaire.strip() if commentaire.strip() else None,
                }
                reponse = client.post(
                    "/retour",
                    json=payload,
                    cookies={"interaction_token": token_interaction},
                )

                if reponse.status_code == 200:
                    return "✅ Merci pour votre retour !"
                else:
                    return f"❌ Erreur lors de l'envoi : {reponse.status_code}"
            except Exception as e:
                return f"❌ Erreur : {str(e)}"

        submit_btn.click(
            fn=pose_question_avec_retour_utilisatrice,
            inputs=[question_input],
            outputs=[
                reponse_output,
                sources_output,
                retour_utilisatrice_section,
                etat_token_interaction,
                retour_utilisatrice_status,
            ],
        )

        pouce_haut_btn.click(
            fn=lambda token, comm: envoyer_retour_utilisatrice(token, True, comm),
            inputs=[etat_token_interaction, commentaire_input],
            outputs=[retour_utilisatrice_status],
        )

        pouce_bas_btn.click(
            fn=lambda token, comm: envoyer_retour_utilisatrice(token, False, comm),
            inputs=[etat_token_interaction, commentaire_input],
            outputs=[retour_utilisatrice_status],
        )

        envoyer_retour_utilisatrice_btn.click(
            fn=lambda token, comm: envoyer_retour_utilisatrice(token, True, comm),
            inputs=[etat_token_interaction, commentaire_input],
            outputs=[retour_utilisatrice_status],
        )

    return interface
