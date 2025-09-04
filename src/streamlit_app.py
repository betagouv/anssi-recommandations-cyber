import streamlit as st
import requests

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔐 Assistant Cyber ANSSI")

question = st.text_input(
    "Posez votre question :",
    placeholder="Quelle est la bonne longueur pour un mot de passe ?",
)

if st.button("Poser la question"):
    if question:
        with st.spinner("Recherche en cours..."):
            try:
                response = requests.post(
                    "http://0.0.0.0:8000/pose_question", json={"question": question}
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
