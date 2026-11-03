# Recommandations cyber ANSSI - Interface Utilisateur

La partie client du service permettant d'interroger [Albert](https://albert.etalab.gouv.fr), le modèle IA, chargé avec des guides de l'ANSSI.

## 📦 Comment installer ?

### Directement sur l'hôte

Il faut installer `node` (la version à installer est spécifiée dans le fichier `.nvmrc`) et `pnpm` (la version est spécifiée dans le champ `packageManager` de `package.json`).
Ensuite, il faut installer les dépendances avec `pnpm install`. Le script `preinstall` refuse `npm install` : le projet n'utilise pas `npm`.

### Dans un conteneur

L'installation dans le projet parent est gérée directement par Docker compose, il faut donc se reporter à la section correspondante [🚀 Comment lancer l'application ?](../README.md#-comment-lancer-lapplication-)

## ⚙️ Comment définir mes variables d'environnement ?

Il faut créer un fichier `ui/.env` à partir de [`ui/.env.template`](./.env.template).
Les variables `VITE_*` sont lues par Vite au démarrage du serveur de développement ou au build : elles ne sont pas lues dans le `.env` de la racine du projet.

## 🧪 Comment valider ?

Depuis le dossier `ui/` :

- utiliser `npm run lint:check` pour lancer les vérifications `eslint`, et `npm run lint:fix` pour réparer automatiquement certaines violations,
- lancer `npm run check` pour vérifier la validité des annotations de types.

## 💬 Comment utiliser l'application ?

Cette application correspond à une interface utilisateur, fournie sous forme de fichiers produits dans le répertoire `dist/`.
Elle doit être distribuée par un serveur HTTP, et a besoin d'une API spécifique pour fonctionner : elle est construite pour être utilisée par [l'application parente](../).

## 🤝 Contribuer

Le formattage automatique s'effectue avec la commande : `npm run format:fix`.
