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
env $(cat .env) uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

#### Dans un conteneur

```shell
podman container run --rm -it \
    --network=host \
    --volume $(pwd):/app \
    localhost:mqc \
    bash -c "env \$(cat .env) uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir src"
```

## 💬 Comment utiliser l'application ?

### Rechercher les paragraphes en lien avec une question

Une fois l'application démarrée, il faut ouvrir un autre terminal et exécuter la commande suivante :

```shell
curl -X POST http://0.0.0.0:8000/recherche -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

## 🤝 Contribuer

Le formattage automatique s'effectue avec la commande : `ruff format`.
