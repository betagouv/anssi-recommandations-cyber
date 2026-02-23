import datetime

from infra.chiffrement.chiffrement import ServiceDeChiffrementAES


class Resultat:
    def __init__(self, identifiant: str, date_creation: str, question:str,reponse:str, commentaire: str,  avis: str, tags: list[str]):
        self.question = question
        self.tags = tags
        self.avis = avis
        self.commentaire = commentaire
        self.identifiant = identifiant
        self.reponse = reponse
        self.date_creation = datetime.datetime.fromisoformat(date_creation).strftime("%d/%m/%Y %H:%M")

    def __str__(self):
        return self.avis + " " + self.commentaire


# RÉCUPÉRER LES COMMENTAIRES SUR L’UTILISATION DE MQC
# SELECT id_interaction,
#   interactions.contenu -> 'reponse_question' ->> 'question'       as question,
#   interactions.contenu -> 'reponse_question' ->> 'reponse'       as reponse,
#   interactions.contenu -> 'retour_utilisatrice' ->> 'commentaire' as commentaire,
#   interactions.contenu -> 'retour_utilisatrice' ->> 'type'        as type_reponse,
#   interactions.contenu -> 'retour_utilisatrice' ->> 'tags'        as tags
# FROM interactions
# WHERE interactions.contenu -> 'retour_utilisatrice' ->> 'commentaire' is not NULL
#   AND (interactions.contenu ->> 'date_creation')::date IS NOT NULL
# ORDER BY interactions.contenu ->> 'date_creation' DESC;

def test_commentaires():
    resultats = []
    with open("LE_FICHIER") as fichier:
        contenu_fichier = fichier.read()
        lignes = contenu_fichier.split("\n")


        for ligne in lignes:
            contenu_ligne = ligne.split(";")
            service_chiffrement = ServiceDeChiffrementAES(b"LA_CLEF")
            tags = contenu_ligne[5].replace("\"[\"", "").replace("\"\", \"\"", "\",\"").replace("\"]\"", "").split(",")
            les_tags = []
            for tag in tags:
                print(f"LE TAG : {tag}")
                les_tags.append(service_chiffrement.dechiffre(tag.replace("\"", "")))
            resultat = Resultat(contenu_ligne[0], contenu_ligne[6], service_chiffrement.dechiffre(contenu_ligne[1]), service_chiffrement.dechiffre(contenu_ligne[2]), service_chiffrement.dechiffre(contenu_ligne[3]),contenu_ligne[4], les_tags)
            resultats.append(resultat)

    with (open("resultats_alpha_tests.md", "+w") as fichier):
        fichier.write("# Resultats des tests alpha\n")
        for resultat in resultats:
            retour = "🎉"
            if resultat.avis == "negatif":
                retour = "❌"
            fichier.write(f"## {retour} {resultat.date_creation} - {resultat.question}\n")
            fichier.write(f"**Identifiant :** {resultat.identifiant}\n")
            fichier.write("### Réponse\n")
            fichier.write(f"{resultat.reponse}\n")
            fichier.write("### Retours\n")
            fichier.write(f"- {resultat.avis}\n- {resultat.commentaire}\n- {"- ".join(list(map(lambda t : f"{t}\n", resultat.tags)))}\n\n")


# EXTRAIRE UNE CONVERSATION
# SELECT id_interaction,
#        contenu -> 'reponse_question' ->> 'question'       as question,
#        contenu -> 'reponse_question' ->> 'reponse'       as reponse,
#        contenu -> 'retour_utilisatrice' ->> 'commentaire' as commentaire,
#        contenu -> 'retour_utilisatrice' ->> 'type'        as type_reponse,
#        contenu -> 'retour_utilisatrice' ->> 'tags'        as tags,
#        contenu ->> 'date_creation'        as date_creation FROM interactions WHERE id_conversation = '7c4a3caf-faad-4519-a749-5d1db68fb5b0'
# ORDER BY contenu ->> 'date_creation';

def test_conversation():
    resultats = []
    with open("LE_FICHIER") as fichier:
        contenu_fichier = fichier.read()
        lignes = contenu_fichier.split("\n")


        for ligne in lignes:
            contenu_ligne = ligne.split(";")
            service_chiffrement = ServiceDeChiffrementAES(b"LA_CLEF")
            tags = contenu_ligne[5].replace("\"[\"", "").replace("\"\", \"\"", "\",\"").replace("\"]\"", "").split(",")
            les_tags = []
            for tag in tags:
                print(f"LE TAG : {tag}")
                les_tags.append(service_chiffrement.dechiffre(tag.replace("\"", "")))
            resultat = Resultat(contenu_ligne[0], contenu_ligne[6], service_chiffrement.dechiffre(contenu_ligne[1]), service_chiffrement.dechiffre(contenu_ligne[2]), service_chiffrement.dechiffre(contenu_ligne[3]),contenu_ligne[4], les_tags)
            resultats.append(resultat)

    with (open("suivi_conversation.md", "+w") as fichier):
        fichier.write("# Resultats des tests alpha\n")
        for resultat in resultats:
            retour = "🎉"
            if resultat.avis == "negatif":
                retour = "❌"
            fichier.write(f"## {retour} {resultat.date_creation} - {resultat.question}\n")
            fichier.write(f"**Identifiant :** {resultat.identifiant}\n")
            fichier.write("### Réponse\n")
            fichier.write(f"{resultat.reponse}\n")
            fichier.write("### Retours\n")
            fichier.write(f"- {resultat.avis}\n- {resultat.commentaire}\n- {"- ".join(list(map(lambda t : f"{t}\n", resultat.tags)))}\n\n")

