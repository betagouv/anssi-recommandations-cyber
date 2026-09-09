# Instructions agent — MesQuestionsCyber

Ce fichier est la **source de vérité** des instructions destinées aux assistants de
développement (Claude Code, Codex, Junie…). `CLAUDE.md` en est un lien symbolique :
toute modification se fait ici, dans `AGENTS.md`.

Pour l'architecture détaillée du projet, voir [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## RÈGLE D'OR

- Ne **JAMAIS** accéder ou tenter d'accéder aux fichiers `.env` et `.envrc` à la racine du projet.
- Ne jamais tenter d'installer une bibliothèque, librairie, package ou executable sans une explicite approbation.
- Pour chaque bibliothèque, librairie, package ou executable à installer :
    - proposer un lien vers la documentation officielle.
    - détailler les raisons de l'installation.
    - détailler les avantages de l'installation.
    - détailler les éventuels risques de sécurité connus ou potentiels.
    - vérifier que la version utilisée est la dernière stable.
    - ne proposer l'installation de la version âgée d'au moins 7 jours.
- Ne **JAMAIS** commiter au nom de claude ou codex. Mets au nom de l’utilisateur configuré dans git.

À noter : cette dernière contrainte est déjà partiellement outillée — `pyproject.toml`
fixe `[tool.uv] exclude-newer = "1 week"`, et Renovate (`.github/renovate.json`) pilote
les montées de version.

## Contexte projet

MesQuestionsCyber, aussi appelé MQC est une application de type chatbot qui permet d’interroger un LLM,
au travers d’[Albert](https://www.numerique.gouv.fr/offre-accompagnement/expertise-albert-ia-etat/), service
mis en place par la DINUM pour répondre aux attentes en terme d’IA dans les administrations publiques.

MQC repose sur une collection créée au sein d’Albert que nous maintenons.
Cela permet de répondre à des questions ayant pour thème la cyber sécurité.
Pour répondre à ces questions, MQC s’appuie en grande majorité sur les guides publiés par [l’ANSSI](https://cyber.gouv.fr/), Agence Nationale de la sécurité des systèmes d’information.

## Stack technique

- **Python 3.14 / FastAPI** — pour le back (uvicorn, slowapi, SDK OpenAI vers Albert, psycopg2 / PostgreSQL 17).
- **Svelte 5 / TypeScript** — pour le front (Vite, pnpm, `@lab-anssi/ui-kit`, `pdfjs-dist`).
- **Outillage** — `uv` (dépendances Python), `mypy`, `ruff`, `pytest` côté back ; `vitest`, `svelte-check`, `eslint`, `prettier` côté front.

## Commandes

Back (à la racine, dans le venv `uv` — `source .venv/bin/activate` ou préfixer par `uv run`) :

- `uv sync` — installe les dépendances.
- `pytest` (ou `uv run pytest`) — lance les tests Python.
- `uv run mypy` — vérifie les annotations de types.
- `uv run ruff check` — lint Python. `uv run ruff format` — formatage.

Front (depuis le dossier `ui/`) :

- `pnpm install` — installe les dépendances.
- `npm run test` (ou `pnpm run test`) — lance les tests TypeScript (`svelte-check` + `vitest`).
- `pnpm run check` — vérifie les types et les composants Svelte.
- `pnpm run lint:check` / `pnpm run format:check` — lint et formatage.
- `pnpm run build` — construit l'interface dans `ui/dist/`.

Lancer l'application :

- Sur l'hôte : `env $(cat .env) python src/main.py`.
- En conteneur : 
   - Linux / MAC (nouveau docker compose) : `NODE_VERSION="$(cat ./ui/.nvmrc)" docker compose up` 
   - Linux / MAC (ancien docker compose) : `docker-compose up --build --force-recreate -d`.
   - Powershell : `env:NODE_VERSION = (Get-Content ./ui/.nvmrc); docker compose up --build`
- Migrations BDD : `PYTHONPATH=src uv run --env-file .env src/infra/postgres/execute_migration.py`.

## Organisation du code

Architecture en ports / adaptateurs (voir [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)) :

- `src/api/` — routeurs FastAPI (`/api/conversation`, `/api/recherche`, `/api/retour`, `/api/avis`, documents sources).
- `src/question/` — couche métier (`cree_conversation`, `ajoute_interaction`, reformulateur).
- `src/services/` — `ServiceAlbert.pose_question()` et les reclasseurs (BGE / LLM).
- `src/infra/` et `src/adaptateurs/` — adaptateurs : client Albert, PostgreSQL / mémoire, chiffrement, journal, Sentry, horloge, migrateur.
- `src/schemas/` — types (Albert, API, retours utilisateurs, violations).
- `src/configuration.py`, `src/serveur.py` (`fabrique_serveur`), `src/main.py` — configuration et amorçage.
- `ui/` — front Svelte, construit dans `ui/dist/` puis servi en statique par FastAPI.
- `migrations/` — migrations SQL numérotées.

## Conventions

- **Langue** : français partout — code, noms de symboles, commits, documentation (spell-check configuré pour `fr`).
- **Dates** : format ISO.
- **Méthode** : TDD strict, un comportement à la fois → skill `tdd`.
- **Tests** : fakes injectés (jamais de mock), noms en français traduisant l'intention métier → [`tests/AGENTS.md`](tests/AGENTS.md) (back) et [`ui/tests/AGENTS.md`](ui/tests/AGENTS.md) (front).
- **Git** : jamais de push direct sur `main` (toujours une PR) ; branches en `kebab-case` descriptif ; messages `[CATEGORIE] Verbe impératif en français` ; commits atomiques → skill `git`.

## Skills disponibles

Versionnés dans `.agents/skills/` (identique à `.claude/skills/`, qui en est un lien symbolique) :

- `tdd` — cycle Rouge → Vert → Refactor, baby steps stricts.
- `git` — conventions Git / GitHub de l'équipe (branches, messages de commit, commits atomiques, workflow de contribution).

Les déclencher selon leur description.