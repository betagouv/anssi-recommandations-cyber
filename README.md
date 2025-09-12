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

### Tests unitaires 

Dans un environnement virtuel, lancer `pytest`.

## 🚀 Comment lancer l'application ?

### Prérequis : PostgreSQL

L'application nécessite une base PostgreSQL. Lancez-la avec Docker en utilisant vos variables d'environnement :

```shell
env $(cat .env) && docker run \
  --detach \
  --name postgres \
  --env POSTGRES_DB="$DB_NAME" \
  --env POSTGRES_PASSWORD="$DB_PASSWORD" \
  --publish "$DB_PORT:5432" \
  postgres:15
```

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

### 1. Déterminer l'adresse de l'application

Il faut récupérer l'adresse où l'application est exposée (en fonction des paramètres d'environnements) :

```shell
host="$(grep HOST .env | cut -d'=' -f2)"
port="$(grep PORT .env | cut -d'=' -f2)"
endpoint="http://${host}:${port}"
```

### 2. Accéder à l'interface graphique

L'interface Gradio est accessible via le chemin `/ui`.\
Ouvrez simplement dans votre navigateur :

    ${endpoint}/ui

Exemple en local (avec `HOST=127.0.0.1`, `PORT=8000`) :

    http://127.0.0.1:8000/ui

### 3. Utiliser directement les routes API

#### Rechercher les paragraphes en lien avec une question

```shell
curl -X POST "${endpoint}/recherche" -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

#### Poser une question

```shell
curl -X POST "${endpoint}/pose_question" -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

## 🤝 Contribuer

Le formattage automatique s'effectue avec la commande : `ruff format`.
