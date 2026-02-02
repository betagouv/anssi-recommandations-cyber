from infra.chiffrement.chiffrement import ServiceDeChiffrementAES


class Resultat:
    def __init__(self, identifiant: str, question:str, commentaire: str, avis: str, tags: str):
        self.question = question
        self.tags = tags
        self.avis = avis
        self.commentaire = commentaire
        self.identifiant = identifiant

    def __str__(self):
        return self.avis + " " + self.commentaire


# Requête d’extraction des commentaires
# SELECT id_interaction,
#        interactions.contenu -> 'reponse_question' ->> 'question' as question,
#        interactions.contenu -> 'retour_utilisatrice' ->> 'commentaire' as commentaire,
#        interactions.contenu -> 'retour_utilisatrice' ->> 'type'        as type_reponse,
#        interactions.contenu -> 'retour_utilisatrice' ->> 'tags'        as tags
# FROM interactions
# WHERE interactions.contenu -> 'retour_utilisatrice' ->> 'commentaire' is not NULL;

def test_commentaires():
    resultats = []
    with open("LE_FICHIER.csv") as fichier:
        contenu_fichier = fichier.read()
        lignes = contenu_fichier.split("\n")


        for ligne in lignes:
            contenu_ligne = ligne.split(";")
            service_chiffrement = ServiceDeChiffrementAES(b"LA_CLEF")
            tags = contenu_ligne[4].replace("\"[\"", "").replace("\"]\"", "").split(",")
            les_tags = []
            for tag in tags:
                print(f"LE TAG : {tag}")
                les_tags.append(service_chiffrement.dechiffre(tag.replace("\"", "")))
            resultat = Resultat(contenu_ligne[0], service_chiffrement.dechiffre(contenu_ligne[1]), service_chiffrement.dechiffre(contenu_ligne[2]), contenu_ligne[3], " ".join(les_tags))
            resultats.append(resultat)

    with (open("resultats_alpha_tests.md", "+w") as fichier):
        fichier.write("# Resultats des tests alpha\n")
        for resultat in resultats:
            fichier.write(f"**{resultat.question} :** {resultat.identifiant}\n")
            fichier.write(f"- {resultat.avis}\n- {resultat.commentaire}\n- {resultat.tags}\n\n")

