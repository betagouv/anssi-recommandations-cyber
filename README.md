# Recommandations cyber ANSSI

Une interface permettant d'interroger [Albert](https://albert.etalab.gouv.fr), le modèle IA, chargé avec des guides de l'ANSSI.

## Comment installer ?

Il faut installer deux dépendances systèmes, `python` et `uv`.
Ensuite, la première fois il faut créer un environnement virtuel avec `uv venv`.

Dès lors, l'environnement est activable via `source .venv/bin/activate`.
Les dépendances déclarées sont installables via `uv sync`.

## Comment tester ?

Dans un environnement virtuel, lancer `pytest`.

## Comment lancer l'application ?

En mode développement :

```shell
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

## Contribuer

Le formattage automatique s'effectue avec la commande : `ruff format`.