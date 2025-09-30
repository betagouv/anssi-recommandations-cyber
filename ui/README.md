# Recommandations cyber ANSSI - Interface Utilisateur

La partie client du service permettant d'interroger [Albert](https://albert.etalab.gouv.fr), le modèle IA, chargé avec des guides de l'ANSSI.

## 📦 Comment installer ?

### Directement sur l'hôte

Il faut installer les dépendances système `node` (la version à installer est spécifiée dans le fichier `.nvmrc`) et `npm`.
Ensuite, il faut installer les dépendances avec `npm install`.

### Dans un conteneur

On fournit une recette pour produire une image de conteneur.\
Pour construire l'image, il faut lancer `docker build --build-arg NODE_VERSION=$(cat .nvmrc) -t localhost/mqc/ui .`.

## 🧪 Comment valider ?

Dans un environnement virtuel :

- utiliser `npm run lint:check` pour lancer les vérifications `eslint`, et `npm run lint:fix` pour réparer automatiquement certaines violations,
- lancer `npm run check` pour vérifier la validité des annotations de types.

## 🚀 Comment lancer l'application ?

### En mode développement

#### Directement sur l'hôte

```shell
npm run dev
```

#### Dans un conteneur

```shell
docker container run --rm -it \
    --volume $(pwd):/app \
    localhost/mqc/ui \
    npm run dev
```

## 💬 Comment utiliser l'application ?

Cette application correspond à une interface utilisateur, fournie sous forme de fichiers produits dans le répertoire `dist/`.
Elle doit être distribuée par un serveur HTTP, et a besoin d'une API spécifique pour fonctionner : elle est construite pour être utilisée par [l'application parente](../).

## 🤝 Contribuer

Le formattage automatique s'effectue avec la commande : `npm run format`.
