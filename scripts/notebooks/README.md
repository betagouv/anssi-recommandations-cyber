
# Répertoire de prototypage ?

Dans ce dossier, le code a pour objectif de prototyper rapidement un produit / fonctionnalité spécifique. Chaque prototype est développé à l'aide de la bibliothèque python `jupyter notebook`.
Pour cette raison, les dépendances python peuvent être différentes du projet principal : ce dossier a donc son propre environnement, et il n'a pas de `pyproject.toml`.

## 📦 Comment installer ?

Il faut installer deux dépendances systèmes, `python` et `uv`.
Ensuite, la première fois il faut créer un environnement virtuel avec `uv venv` depuis le dossier `scripts/notebooks`.

Dès lors, l'environnement est activable via `source .venv/bin/activate` (sous Windows PowerShell : `.venv\Scripts\Activate.ps1`).

Comme il n'y a pas de `pyproject.toml` dans ce dossier, `uv sync` ne s'applique pas. Il faut installer dans cet environnement les bibliothèques importées par les notebooks (`openai`, `requests`, `pandas`, `ipython`) et Jupyter :

```bash
uv pip install openai requests pandas ipython jupyter
```

## 🚀 Comment l'utiliser ?

Pour ouvrir les notebooks, il faut exécuter la commande `jupyter notebook`, après avoir vérifié que l'environnement est bien activé.
Dès lors, vous pourrez ouvrir via le lien affiché dans le terminal, les notebooks qui portent l'extension `.ipynb`.
