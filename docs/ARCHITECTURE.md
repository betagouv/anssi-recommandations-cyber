# Architecture : MesQuestionsCyber

Ce document décrit l'architecture réelle du code du dépôt. Il complète
[`AGENTS.md`](../AGENTS.md) (règles pour les assistants) et le [`README.md`](../README.md)
(installation, lancement). Vue schématique en [modèle C4](https://c4model.com/) (niveaux
1 à 3) : [`C4.puml`](./C4.puml).

## Vue d'ensemble

MesQuestionsCyber (MQC) est un chatbot de cybersécurité. L'utilisateur pose une question
dans une interface web ; MQC construit une réponse fondée sur les guides de l'ANSSI en
s'appuyant sur [Albert](https://albert.etalab.gouv.fr) (LLM + RAG de la DINUM) et une
collection de documents ANSSI que l'équipe maintient dans Albert.

Parcours d'une requête :

```
Front Svelte  ──►  API FastAPI (src/api/)  ──►  Couche métier (src/question/)
                                                      │
                                                      ▼
                                          ServiceAlbert (src/services/)
                                                      │
                        reformulation · recherche · reclassement · génération
                                                      │
                                                      ▼
                                        Albert (SDK OpenAI + API REST)
```

La conversation est ensuite persistée en base (PostgreSQL) et un événement est écrit dans
le journal.

## Stack & outillage

### Back : `src/`

| Brique | Rôle |
|---|---|
| **Python 3.14** | langage (voir `requires-python` dans `pyproject.toml`) |
| **FastAPI** + **uvicorn** | serveur HTTP et routage (`src/serveur.py`, `src/main.py`) |
| **slowapi** | limitation de débit (rate limiting) par IP |
| **SDK `openai`** | canal vers Albert pour la reformulation, le reclassement LLM et la génération |
| **`httpx` / `requests`** | canal REST « classique » d'Albert (`/search`, `/rerank`, chunks) |
| **`cryptography`** | chiffrement des contenus de conversation, hachage des identifiants |
| **`psycopg2`** | accès PostgreSQL |
| **`sentry-sdk`** | remontée d'erreurs (optionnelle) |
| `uv`, `mypy`, `ruff`, `pytest` | dépendances, types, lint/format, tests |

### Front : `ui/`

| Brique | Rôle |
|---|---|
| **Svelte 5** + **TypeScript** | composants d'interface (`ui/src/`) |
| **Vite** | build vers `ui/dist/` (`pnpm run build`) |
| **pnpm** | gestionnaire de paquets (imposé via `only-allow`) |
| **`@lab-anssi/ui-kit`** | design system de l'État / ANSSI |
| **`pdfjs-dist`** | visionneuse des PDF sources (`ui/src/pdf/`) |
| **`marked`** + **`dompurify`** | rendu Markdown des réponses, assaini |
| **`zod`** | validation des schémas côté client |
| `vitest`, `svelte-check`, `eslint`, `prettier` | tests, types, lint, format |

### Base de données

PostgreSQL 17 (image `docker.io/postgres:17` en dev). Migrations SQL numérotées dans
`migrations/`, appliquées par `src/infra/postgres/execute_migration.py`.

## Style architectural : ports / adaptateurs

Le code suit une architecture hexagonale. La logique métier (`src/question/`,
`src/services/`) ne dépend pas des détails techniques : elle reçoit des **adaptateurs**
construits par des **fabriques**.

- `src/adaptateurs/` et `src/infra/` fournissent les implémentations concrètes :
  base de données (PostgreSQL **ou** mémoire), chiffrement, journal, Sentry, horloge,
  migrateur, client Albert.
- Les fabriques (`fabrique_serveur`, `fabrique_service_albert`, `fabrique_reclasseur`,
  `fabrique_adaptateur_base_de_donnees`, `fabrique_adaptateur_chiffrement`,
  `fabrique_adaptateur_sentry`…) assemblent l'application à partir de la configuration.
- Les tests substituent des adaptateurs mémoire et des doublures (`tests/mocks/`), ce qui
  permet de tester le métier sans base ni appel réseau.

## Arborescence `src/`

| Dossier / fichier | Responsabilité |
|---|---|
| `api/` | Routeurs FastAPI : `api_conversation` (`POST /api/conversation/`, `POST /api/conversation/{id_conversation}`), `recherche.py` (`POST /api/recherche/`), `api_retour`, `api_avis`, `route_document_source` (PDF sources). `api/api.py` définit `api_developpement`, qui expose `/api/sante` uniquement en mode `DEVELOPPEMENT`. |
| `question/` | Couche métier : `cree_conversation()`, `ajoute_interaction()`, `ajoute_retour_utilisatrice()`, `supprime_retour_utilisatrice()` ; `reformulateur_de_question.py` ; `reclassement/` (interface `Reclasseur`, `ReclasseurBGE`, `ReclasseurLLM`, `ReclasseurLLMParLots`, sélection des preuves, unités sources). Renvoie des objets `Resultat*` (succès, erreur, conversation inconnue). |
| `services/` | `ServiceAlbert.pose_question()` orchestre le flux complet ; `fabrique_service_albert.py` et `fabrique_reclasseur.py` (choix du reclasseur selon `TYPE_RECLASSEUR`) ; `reclasseur_llm_en_parallele.py` et `coordinateur_reclassement_parallele.py` (reclassement parallèle) ; `client_albert.py` ; `contexte_documents.py` (contexte des guides MSC) ; `strategie_enrichissement_paragraphes.py` ; `fichier_prompt.py` ; `exceptions.py` (`ErreurAlbert` et dérivées). |
| `infra/` | `albert/client_albert.py` (SDK OpenAI + REST) ; `postgres/` (migrations, encodeurs JSON) ; `chiffrement/` ; `logger.py` ; `mapping_reponses_maitrisees.py` ; `ui_kit/version_ui_kit.py` ; `fast_api/`. |
| `adaptateurs/` | `adaptateur_base_de_donnees_postgres.py` / `_memoire.py`, `chiffrement.py`, `journal.py`, `sentry.py`, `horloge.py`, `migrateur.py`, `connecteur.py`. |
| `schemas/` | Types : `albert.py` (`ReponseQuestion`…), `api.py`, `retour_utilisatrice.py` (`Conversation`, `Interaction`), `type_utilisateur.py`, `violations.py`, `msc.py` (guides MesServicesCyber). |
| `configuration.py` | `recupere_configuration()` : lecture des variables d'environnement, `Mode` (`DEVELOPPEMENT` / `TEST` / `PRODUCTION`), configuration Albert / BDD / chiffrement / Sentry. |
| `serveur.py` | `fabrique_serveur()` : middlewares (rate limiting, proxy headers), en-têtes de sécurité + CSP à nonce, montage des routeurs et des ressources statiques, pages statiques, mode maintenance, cycle de vie du coordinateur de reclassement. |
| `main.py` | Point d'entrée : charge la configuration, construit le serveur, lance `uvicorn`. |

## Flux d'une question vers Albert

Les deux routes de `api_conversation.py` convergent vers `ServiceAlbert.pose_question()`.
Étapes (détail et références de code dans [`interactions_albert.md`](./interactions_albert.md)) :

1. **Reformulation** (SDK OpenAI) : reconstruit la question à partir de l'historique. Si
   `QUESTION_NON_COMPRISE`, le flux s'arrête sur une `ViolationQuestionNonComprise`.
2. **Recherche** (REST `/search`) : paragraphes pertinents dans la collection ANSSI
   (recherche `hybrid` ou `semantic` selon la configuration). Étape « jeopardy »
   optionnelle sur une seconde collection.
   Les paragraphes sont ensuite enrichis (pages précédente et suivante), puis associés au
   contexte des guides MSC (`GET {URL_MSC}/api/guides`).
3. **Reclassement** : `TYPE_RECLASSEUR=bge` (REST `/rerank`), `llm` (SDK OpenAI) ou
   `llm_parallele` (classification structurée, lots exécutés en parallèle), puis filtrage des
   « réponses maîtrisées » (FAQ) au-delà de `SEUIL_REPONSE_MAITRISEE`. Les réponses
   maîtrisées sont chargées depuis `URL_MAPPING_PAR_DEFAUT` (`src/services/fabrique_service_albert.py`),
   une URL du dépôt `anssi-recommandations-cyber-data` : le fichier `donnees/faq_reponses_maitrisees.mapping.json`
   de ce dépôt n'est lu par aucun code.
4. **Génération** (SDK OpenAI) : paragraphes retenus injectés dans le prompt système, avec
   l'historique limité à `ALBERT_TAILLE_FENETRE_HISTORIQUE` échanges.
5. **Analyse locale** : détection de marqueurs texte (`ERREUR_IDENTITÉ`,
   `ERREUR_THÉMATIQUE`, `ERREUR_MALVEILLANCE`, `ERREUR_MECONNAISSANCE`) transformés en
   violations.
6. **Retour** : persistance de la conversation, écriture au journal, réponse `200/201`
   JSON (ou `HTTPException` en cas d'erreur : `500` communication Albert, `404` conversation
   inconnue, `422` erreur imprévue).

Une panne de communication avec le modèle est tracée selon l'étape fautive :
`ErreurCommunicationModeleReformulation` (étape 1),
`ErreurCommunicationModeleReclassement` (étape 3, `TYPE_RECLASSEUR=llm` ou `llm_parallele`),
`ErreurCommunicationModeleGeneration` (étape 4). Toutes sont des sous-classes
de `ErreurCommunicationModele` (`COMMUNICATION_ALBERT`, `500`). Voir
[`interactions_albert.md`](./interactions_albert.md).

Les prompts sont dans `templates/` (`prompt_assistant_cyber.txt`,
`prompt_reformulation.txt`, `prompt_reclassement*.txt`).

## Front (`ui/`)

- `pnpm run build` produit `ui/dist/` ; `src/serveur.py` sert `index.html` sur `/`, les
  pages statiques (`/cgu`, `/faq`, `/politique-confidentialite`, et
  `mode-maintenance.html` en 503 quand `MODE_MAINTENANCE=true`) et monte les ressources
  (`/assets`, `/fonts`, `/icons`, `/images`).
- À chaque service de page, `sert_la_page_statique()` remplace les marqueurs
  `%%NONCE_A_INJECTER%%`, `%%VERSION_UI_KIT%%`, `%%FAVICON%%` : le nonce alimente la CSP.
- `ui/src/composants/` contient les composants (conversation, saisie, sources, bandeaux,
  entête, pied de page…) ; `ui/src/client.api.ts` appelle l'API ; `ui/src/pdf/` intègre
  pdf.js pour afficher les documents sources.
- Les variables `VITE_*` se définissent dans `ui/.env` (modèle : `ui/.env.template`).

## Sécurité

- **En-têtes HTTP** : `HEADERS_SECURITE` dans `src/serveur.py` (HSTS, `X-Frame-Options:
  DENY`, `X-Content-Type-Options: nosniff`, COOP/COEP/CORP…) + **CSP à nonce** générée par
  requête.
- **Chiffrement** : les contenus de conversation sont chiffrés
  (`CHIFFREMENT_CLEF_DE_CHIFFREMENT`) ; les identifiants de conversation / interaction sont
  hachés (`CHIFFREMENT_SEL_DE_HACHAGE`) avant d'entrer dans le journal.
- **Rate limiting** : `slowapi`, `SERVEUR_MAX_REQUETES_PAR_MINUTE` requêtes/minute par IP.
- **Mode maintenance** : middleware qui renvoie la page dédiée en 503.
- **Secrets** : uniquement via variables d'environnement (`.env`, jamais versionné, jamais
  lu par un assistant).
- CI de sécurité : `.github/workflows/securite-ci.yml`, `codeql-analysis.yml` ;
  dépendances pilotées par Renovate (`.github/renovate.json`).

## Configuration

Tout passe par des variables d'environnement, centralisées dans `src/configuration.py` :

- `recupere_configuration()` construit un `Configuration` (NamedTuple imbriqué :
  `Albert.Client`, `Albert.Service`, `BaseDeDonnees`, `Chiffrement`, `Sentry`…).
- `VariablesEnvironnementNecessaires` liste les variables obligatoires ; elles sont
  vérifiées au démarrage sauf en mode `TEST` / `DEVELOPPEMENT`.
- Le modèle de fichier est `.env.template` (racine) et `ui/.env.template`. Les variables
  optionnelles figurent en commentaire dans `.env.template`, avec leur valeur par défaut.

## Observabilité

- **Sentry** via un adaptateur `memoire` (défaut / tests) ou `standard`
  (`SENTRY_TYPE_ADAPTATEUR`). Le domaine n'y touche jamais directement : quand une
  `ErreurCommunicationModele*` est levée (reformulation, reclassement LLM, génération),
  le composant fautif publie un `ErreurTechniqueSurvenue` sur le **bus d'événements**
  (`src/adaptateurs/bus_evenements.py`, `publie_erreur_technique`). Le
  `ConsommateurSentry` (`src/adaptateurs/consommateur_sentry.py`), abonné au bus par
  `fabrique_serveur`, relaie l'exception à `AdaptateurSentry.capture_exception`. Le bus
  (`BusEvenementsEnMemoire`, synchrone, en-process) est injecté dans le domaine par
  `fabrique_service_albert`.
- **Journal d'événements** (`src/adaptateurs/journal.py`) : `CONVERSATION_CREEE`,
  `INTERACTION_AJOUTEE`, `VIOLATION_DETECTEE`, `DOCUMENT_SOURCE_VISIONNE` : avec longueurs
  et métadonnées, et le texte de la question uniquement en `ALPHA_TEST`.

## Tests

- **Back** : `pytest` (`tests/`), organisé par couche (`tests/api/`, `tests/question/`,
  `tests/services/`, `tests/infra/`, `tests/adaptateurs/`, `tests/schemas/`). Adaptateurs
  mémoire + doublures dans `tests/mocks/`. `pythonpath = ["src", "tests/mocks"]`.
- **Front** : `pnpm run test` (`svelte:check` + `vitest`) depuis `ui/`.
- **CI** : `.github/workflows/ci.yml` : job front (test, check, lint, format) et job back
  (`ruff check`, `mypy`, `pytest`) en `MODE: test`.

## Déploiement

- **Développement** : `docker-compose.yml` (services `mqc-frontend`, `mqc-backend`,
  `mqc-db`) ou lancement direct sur l'hôte.
- **Déploiement Clever Cloud** : workflow `.github/workflows/deploiement.yml`. À chaque push
  sur `main` (ou déclenchement manuel), l'application est déployée sur l'environnement DEMO,
  puis sur les environnements PROD et PROD-OFF (`needs: deploiement-demo`).
- **Scripts Clever Cloud** : `scripts/clever-cloud/pre-run-clever.sh` construit l'interface
  (`pnpm run build` dans `ui/`) ; `scripts/clever-cloud/post-build-clever.sh` applique les
  migrations (`src/infra/postgres/execute_migration.py`).
