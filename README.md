# 🔐 Recommandations cyber ANSSI

Une interface permettant d'interroger [Albert](https://albert.etalab.gouv.fr), le modèle IA, chargé avec des guides de l'ANSSI.

## 📦 Comment installer ?

### Installer le `hook` de `pre-commit`

```shell
$ chmod +x .githooks/pre-commit
$ git config core.hooksPath .githooks
```

### Directement sur l'hôte

Il faut installer les dépendances systèmes `python`, `uv`, `node` (la version à installer est spécifiée dans le fichier [`ui/.nvmrc`](./ui/.nvmrc)), `npm` et `pnpm`.
Ensuite, la première fois il faut créer un environnement virtuel avec `uv venv`.

Dès lors, l'environnement est activable via `source .venv/bin/activate`.
Les dépendances déclarées sont installables via `uv sync`.
Les dépendances frontend sont installables depuis le dossier `ui/` via `pnpm install`, puis l'interface est construite avec `pnpm run build`.

### Dans un conteneur

L'installation est gérée directement par Docker compose, il faut donc se reporter à la section [🚀 Comment lancer l'application ?](#-comment-lancer-lapplication-)

## ⚙️ Comment Définir mes variables d'environnement ?

Il faut créer à la racine du projet un fichier `.env`.
A minima, ce fichier devra défnir les variables déclarées dans le fichier `.env.template`.

## 🧪 Comment valider ?

Dans un environnement virtuel :

* lancer `mypy` pour vérifier la validité des annotations de types ;
* lancer `pytest` pour valider le comportement à l'exécution ;
* lancer `ruff check` pour vérifier le code Python.

Depuis le dossier `ui/` :

* lancer `pnpm run test` pour exécuter les tests frontend ;
* lancer `pnpm run check` pour vérifier les types et les composants Svelte ;
* lancer `pnpm run lint:check` pour vérifier le linting ;
* lancer `pnpm run format:check` pour vérifier le formatage.

## 🚀 Comment lancer l'application ?

### En mode développement

#### Directement sur l'hôte

```shell
env $(cat .env) python src/main.py
```

#### Dans un conteneur


```shell
NODE_VERSION="$(cat ./ui/.nvmrc)" docker compose up
```

### Migration des données
Exécuter la commande suivante, suivant l’environnement dans lequel on se trouve :
- depuis l’hôte (à la racine du projet) : `PYTHONPATH=src uv run --env-file .env src/infra/postgres/execute_migration.py` 
- depuis un conteneur : `scripts/clever-cloud/post-build-clever.sh`

## 💬 Comment utiliser l'application ?

### 1. Déterminer l'adresse de l'application

Il faut récupérer l'adresse où l'application est exposée (en fonction des paramètres d'environnements) :

```shell
host="$(grep HOST .env | cut -d'=' -f2)"
port="$(grep PORT .env | cut -d'=' -f2)"
endpoint="http://${host}:${port}"
```

### 2. Accéder à l'interface graphique

L'interface produite à partir du code [du dossier `ui/`](./ui) est accessible via le chemin `/`.\
Ouvrez simplement dans votre navigateur :

    ${endpoint}/

Exemple en local (avec `HOST=127.0.0.1`, `PORT=8000`) :

    http://127.0.0.1:8000/

### 3. Utiliser directement les routes API

#### Rechercher les paragraphes en lien avec une question

```shell
curl -X POST "${endpoint}/api/recherche/" -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

#### Poser une question

```shell
curl -X POST "${endpoint}/api/conversation/" -H "Content-Type: application/json" -d '{"question": "Quelles sont les bonnes pratiques de sécurité ?"}'
```

Pour poursuivre une conversation, utiliser l'identifiant `id_conversation` retourné par la requête précédente :

```shell
curl -X POST "${endpoint}/api/conversation/{id_conversation}" -H "Content-Type: application/json" -d '{"question": "Et pour les collectivités ?"}'
```

## 🤝 Contribuer

Le formattage automatique s'effectue avec la commande : `ruff format`.
