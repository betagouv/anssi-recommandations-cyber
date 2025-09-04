# 🔐 Recommandations cyber ANSSI

Une interface permettant d'interroger [Albert](https://albert.etalab.gouv.fr), le modèle IA, chargé avec des guides de l'ANSSI.

## 📦 Comment installer ?

### Directement sur l'hôte

Il faut installer deux dépendances systèmes, `python` et `uv`.
Ensuite, la première fois il faut créer un environnement virtuel avec `uv venv`.

Dès lors, l'environnement est activable via `source .venv/bin/activate`.
Les dépendances déclarées sont installables via `uv sync`.

### Dans un conteneur

On fournit une recette pour produire une image de conteneur.\
Pour construire l'image, il faut lancer `docker build -t localhost:mqc .`.

## ⚙️ Comment Définir mes variables d'environnement ?

Il faut créer à la racine du projet un fichier `.env`.
A minima, ce fichier devra défnir les variables déclarées dans le fichier `.env.template`.

## 🧪 Comment tester ?

Dans un environnement virtuel, lancer `pytest`.

## 🚀 Comment lancer l'application ?

### En mode développement

#### Directement sur l'hôte

```shell
env $(cat .env) python src/main.py
```

#### Dans un conteneur

```shell
podman container run --rm -it \
    --network=host \
    --volume $(pwd):/app \
    localhost:mqc \
    bash -c "env \$(cat .env) python src/main.py"
```

## 💬 Comment utiliser l'application ?

Il faut récupérer l'adresse où l'application est exposée (en fonction des paramètres d'environnements) :

```shell
host="$(grep HOST .env | cut -d'=' -f2)"
port="$(grep PORT .env | cut -d'=' -f2)"
endpoint="http://${host}:${port}"
```
Une fois l'application démarrée, il faut ouvrir un autre terminal et exécuter la commande listée en fonction du besoin.

### Rechercher les paragraphes en lien avec une question

```shell
curl -X POST "${endpoint}/recherche" -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

### Poser une question

```shell
curl -X POST "${endpoint}/pose_question" -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

## 🤝 Contribuer

Le formattage automatique s'effectue avec la commande : `ruff format`.
