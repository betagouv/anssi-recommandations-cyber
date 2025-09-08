import gradio as gr
from fastapi.testclient import TestClient


def pose_question_gradio(question: str, app) -> tuple[str, str]:
    """Interface Gradio pour poser une question à Albert via TestClient"""
    if not question.strip():
        return "Veuillez saisir une question", ""

    try:
        client = TestClient(app)
        response = client.post("/pose_question", json={"question": question})
        if response.status_code == 200:
            data = response.json()
            return data["reponse"], data["paragraphs"]
        else:
            return f"Erreur {response.status_code}", ""
    except Exception as e:
        return f"Erreur : {str(e)}", ""


def cree_interface_gradio(app):
    """Crée l'interface Gradio"""

    def pose_question_handler(question: str) -> tuple[str, str]:
        return pose_question_gradio(question, app)

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
                sources_output = gr.Textbox(
                    label="Sources (paragraphes utilisés)", lines=10, interactive=False
                )

        submit_btn.click(
            fn=pose_question_handler,
            inputs=[question_input],
            outputs=[reponse_output, sources_output],
        )

    return interface
