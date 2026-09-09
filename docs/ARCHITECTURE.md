# Architecture — MesQuestionsCyber

Ce document décrit l'architecture réelle du code du dépôt. Il complète
[`AGENTS.md`](../AGENTS.md) (règles pour les assistants) et le [`README.md`](../README.md)
(installation, lancement).

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

### Back — `src/`

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

### Front — `ui/`

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
- Les fabriques (`fabrique_serveur`, `fabrique_service_albert`,
  `fabrique_adaptateur_base_de_donnees`, `fabrique_adaptateur_chiffrement`,
  `fabrique_adaptateur_sentry`…) assemblent l'application à partir de la configuration.
- Les tests substituent des adaptateurs mémoire et des doublures (`tests/mocks/`), ce qui
  permet de tester le métier sans base ni appel réseau.

## Arborescence `src/`

| Dossier / fichier | Responsabilité |
|---|---|
| `api/` | Routeurs FastAPI : `api_conversation` (`POST /api/conversation/`, `POST /api/conversation/{id_conversation}`), `api_recherche` (`/api/recherche/`), `api_retour`, `api_avis`, `route_document_source` (PDF sources). `api_developpement` expose `/api/sante` hors production. |
| `question/` | Couche métier : `cree_conversation()`, `ajoute_interaction()`, `ajoute_retour_utilisatrice()`, `supprime_retour_utilisatrice()` ; `reformulateur_de_question.py`. Renvoie des objets `Resultat*` (succès, erreur, conversation inconnue). |
| `services/` | `ServiceAlbert.pose_question()` orchestre le flux complet ; `reclasseur.py` (BGE / LLM) ; `client_albert.py`, `fabrique_service_albert.py` ; `exceptions.py` (`ErreurAlbert` et dérivées). |
| `infra/` | `albert/client_albert.py` (SDK OpenAI + REST) ; `postgres/` (migrations, encodeurs JSON) ; `chiffrement/` ; `logger.py` ; `mapping_reponses_maitrisees.py` ; `ui_kit/version_ui_kit.py` ; `fast_api/`. |
| `adaptateurs/` | `adaptateur_base_de_donnees_postgres.py` / `_memoire.py`, `chiffrement.py`, `journal.py`, `sentry.py`, `horloge.py`, `migrateur.py`, `connecteur.py`. |
| `schemas/` | Types : `albert.py` (`ReponseQuestion`…), `api.py`, `retour_utilisatrice.py` (`Conversation`, `Interaction`), `type_utilisateur.py`, `violations.py`. |
| `configuration.py` | `recupere_configuration()` : lecture des variables d'environnement, `Mode` (`DEVELOPPEMENT` / `TEST` / `PRODUCTION`), configuration Albert / BDD / chiffrement / Sentry. |
| `serveur.py` | `fabrique_serveur()` : middlewares (rate limiting, proxy headers), en-têtes de sécurité + CSP à nonce, montage des routeurs et des ressources statiques, pages statiques, mode maintenance. |
| `main.py` | Point d'entrée : charge la configuration, construit le serveur, lance `uvicorn`. |

## Flux d'une question vers Albert

Les deux routes de `api_conversation.py` convergent vers `ServiceAlbert.pose_question()`.
Étapes (détail et références de lignes dans [`interactions_albert.md`](./interactions_albert.md)) :

1. **Reformulation** (SDK OpenAI) — reconstruit la question à partir de l'historique. Si
   `QUESTION_NON_COMPRISE`, le flux s'arrête sur une `ViolationQuestionNonComprise`.
2. **Recherche** (REST `/search`) — paragraphes pertinents dans la collection ANSSI
   (recherche `hybrid` ou `semantic` selon la configuration). Étape « jeopardy »
   optionnelle sur une seconde collection.
3. **Reclassement** — `TYPE_RECLASSEUR=bge` (REST `/rerank`) ou `llm` (SDK OpenAI), puis
   filtrage des « réponses maîtrisées » (FAQ) au-delà d'un seuil.
4. **Génération** (SDK OpenAI) — paragraphes retenus injectés dans le prompt système, avec
   l'historique limité à `taille_fenetre_historique` échanges.
5. **Analyse locale** — détection de marqueurs texte (`ERREUR_IDENTITÉ`,
   `ERREUR_THÉMATIQUE`, `ERREUR_MALVEILLANCE`, `ERREUR_MECONNAISSANCE`) → transformés en
   violations.
6. **Retour** — persistance de la conversation, écriture au journal, réponse `200/201`
   JSON (ou `HTTPException` en cas d'erreur : `500` communication Albert, `404` conversation
   inconnue, `422` erreur imprévue).

Les prompts sont dans `templates/` (`prompt_assistant_cyber.txt`,
`prompt_reformulation.txt`, `prompt_reclassement*.txt`).

## Front (`ui/`)

- `pnpm run build` produit `ui/dist/` ; `src/serveur.py` sert `index.html` sur `/`, les
  pages statiques (`/cgu`, `/faq`, `/politique-confidentialite`, et
  `mode-maintenance.html` en 503 quand `MODE_MAINTENANCE=true`) et monte les ressources
  (`/assets`, `/fonts`, `/icons`, `/images`).
- À chaque service de page, `sert_la_page_statique()` remplace les marqueurs
  `%%NONCE_A_INJECTER%%`, `%%VERSION_UI_KIT%%`, `%%FAVICON%%` — le nonce alimente la CSP.
- `ui/src/composants/` contient les composants (conversation, saisie, sources, bandeaux,
  entête, pied de page…) ; `ui/src/client.api.ts` appelle l'API ; `ui/src/pdf/` intègre
  pdf.js pour afficher les documents sources.

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
  dépendances pilotées par Renovate + Dependabot.

## Configuration

Tout passe par des variables d'environnement, centralisées dans `src/configuration.py` :

- `recupere_configuration()` construit un `Configuration` (NamedTuple imbriqué :
  `Albert.Client`, `Albert.Service`, `BaseDeDonnees`, `Chiffrement`, `Sentry`…).
- `VariablesEnvironnementNecessaires` liste les variables obligatoires ; elles sont
  vérifiées au démarrage sauf en mode `TEST` / `DEVELOPPEMENT`.
- Le modèle de fichier est `.env.template` (racine) et `ui/.env.template`.

## Observabilité

- **Sentry** via un adaptateur `memoire` (défaut / tests) ou `standard`
  (`SENTRY_TYPE_ADAPTATEUR`).
- **Journal d'événements** (`src/adaptateurs/journal.py`) : `CONVERSATION_CREEE`,
  `INTERACTION_AJOUTEE`, `VIOLATION_DETECTEE` — avec longueurs et métadonnées, et le texte
  de la question uniquement en `ALPHA_TEST`.

## Tests

- **Back** : `pytest` (`tests/`), organisé par couche (`tests/api/`, `tests/question/`,
  `tests/services/`, `tests/infra/`, `tests/adaptateurs/`, `tests/schemas/`). Adaptateurs
  mémoire + doublures dans `tests/mocks/`. `pythonpath = ["src", "tests/mocks"]`.
- **Front** : `pnpm run test` (`svelte:check` + `vitest`) depuis `ui/`.
- **CI** : `.github/workflows/ci.yml` — job front (test, check, lint, format) et job back
  (`ruff check`, `mypy`, `pytest`) en `MODE: test`.

## Déploiement

- **Développement** : `docker-compose.yml` (services `mqc-frontend`, `mqc-backend`,
  `mqc-db`) ou lancement direct sur l'hôte.
- **Production** : Clever Cloud — `scripts/clever-cloud/post-build-clever.sh` (build +
  migrations), `scripts/clever-cloud/pre-run-clever.sh` ; workflow
  `.github/workflows/deploiement.yml`.