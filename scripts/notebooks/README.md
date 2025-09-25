
# Répertoire de prototypage ?

Dans ce dossier, le code a pour objectif de prototyper rapidement un produit / fonctionnalité spécifique. Chaque prototype est développé à l'aide de la libraire python `jupyter notebook`.
Pour cette raison, les dépendances python peuvent être différentes du projet principal, c'est pourquoi un autre environnement python `uv` est disponible.

## 📦 Comment installer ?


Il faut installer deux dépendances systèmes, `python` et `uv`.
Ensuite, la première fois il faut créer un environnement virtuel avec `uv venv` depuis le dossier `./scripts/notebooks`.

Dès lors, l'environnement est activable via `source .venv/bin/activate`.
Les dépendances déclarées sont installables via `uv sync`, toujours depuis le répertoire `./srcipts/notebook`.
L'environnement, une fois activé, apparaît sous le nom de `env-notebook`.

## 🚀 Comment l'utiliser ?

Pour ouvrir les notebooks, il faut exécuter la commande `jupyter notebook`, après avoir vérifié que l'environnement est bien activé.
Dès lors, vous pourrez ouvrir via le lien affiché dans le terminal, les notebooks qui portent l'extension `.ipynb`.