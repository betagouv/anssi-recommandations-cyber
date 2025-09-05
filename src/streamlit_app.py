import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔐 Mes questions CyberANSSI")
st.caption(
    "Prototype du LAB ANSSI - Assistant IA pour répondre aux questions de sécurité à partir des documents officiels de l'ANSSI"
)

question = st.text_input(
    "Posez votre question :",
    placeholder="Quelle est la bonne longueur pour un mot de passe ?",
)

if st.button("Poser la question"):
    if question:
        with st.spinner("Recherche en cours..."):
            try:
                response = requests.post(
                    f"{API_URL}/pose_question", json={"question": question}, timeout=30
                )
                if response.status_code == 200:
                    st.success("Réponse :")
                    st.write(response.json())
                else:
                    st.error(f"Erreur {response.status_code}")
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
    else:
        st.warning("Veuillez saisir une question")
