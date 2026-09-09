# Instructions agent — Tests back (`tests/`)

Comment on écrit les tests Python de MesQuestionsCyber. Complète [`../AGENTS.md`](../AGENTS.md)
(règles générales) et [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) (architecture en
ports / adaptateurs, qui rend ces tests possibles).

Outil : `pytest` (à la racine, `pytest` ou `uv run pytest`). Méthode de travail : TDD strict
→ skill `tdd`.

## Règles d'or

1. **Rédaction en français** — noms de tests, fixtures, constructeurs, variables, messages.
2. **Jamais de mock ni de librairie de mock** — pas de `unittest.mock`, pas de
   `monkeypatch` pour simuler un comportement. On injecte des **fakes** (doublures qui
   implémentent réellement le contrat) par dépendance.
3. **Le nom du test traduit l'intention** — on doit comprendre le comportement métier
   vérifié sans lire le corps.
4. **Un test ne vérifie qu'une seule chose** — une intention = un test. Plusieurs
   variantes de la même intention → `@pytest.mark.parametrize`.
5. **Les intentions sont fonctionnelles / métier**, pas techniques.
6. **On ne teste pas les getters / setters.**
7. **On ne teste pas les librairies tierces** — on les isole derrière un adaptateur ou une
   dépendance injectée, et on teste l'adaptateur.
8. **Outside-in ou inside-out selon le cas** (voir plus bas) — les deux approches coexistent.

## Nommer un test

`test_<sujet>_<comportement attendu>`, en français, à l'indicatif ou à l'impératif.

Bons exemples tirés du dépôt :

```python
def test_cree_conversation_retourne_un_resultat_de_conversation_en_erreur(...)
def test_ne_conserve_pas_les_paragraphes_en_cas_de_violation(...)
def test_cree_conversation_emet_un_evenement_journal_conversation_creee(...)
def test_route_initie_conversation_rejette_question_trop_longue(...)
def test_retourne_au_maximum_5_paragraphes_meme_si_le_reclassement_echoue(...)
```

À éviter : `test_pose_question`, `test_ok`, `test_cas_2`, `test_setter_reponse`, tout nom
qui décrit une méthode plutôt qu'un comportement observable.

## Fakes injectés (pas de mocks)

Les fakes vivent dans [`tests/mocks/`](./mocks/) (le dossier porte mal son nom : ce sont
des **fakes**, pas des mocks) et sont importables par leur nom nu
(`pyproject.toml` : `pythonpath = ["src", "tests/mocks"]`).

Conventions :

- **Suffixe** `…DeTest`, `…Memoire` ou `…EnMemoire` ; la classe **hérite** du vrai type
  ou en implémente le contrat.
- Méthodes de configuration **expressives et chaînables** qui décrivent une situation
  métier, pas un `return_value` :
  `service_albert.qui_leve_une_erreur_de_communication_vers_albert()`,
  `client_albert_memoire.qui_leve_une_erreur_sur_recherche()`,
  `service_albert.ajoute_reponse(reponse_question)`,
  `adaptateur_chiffrement.qui_dechiffre(type_utilisateur)`.
- Le fake **enregistre ce qu'il a reçu** pour les assertions :
  `service_albert.question_recue`, `client_albert_memoire.payload_reclassement_recu`,
  `adaptateur_journal.les_evenements()`.

Catalogue actuel : `ServiceAlbertMemoire`, `ClientAlbertMemoire`,
`ReformulateurDeQuestionDeTest`, `AdaptateurChiffrementDeTest`,
`AdaptateurBaseDeDonneesEnMemoire`, `AdaptateurJournalMemoire`, `ReclasseurDeTest`,
`AdaptateurExecuteurDeRequetesMemoire`. Besoin d'un nouveau collaborateur en test → on
ajoute un fake du même style, on n'introduit pas de mock.

### Isoler les librairies

On ne teste jamais `cryptography`, `httpx`, l'SDK `openai`, `psycopg2`… directement :

- chiffrement : on teste `AdaptateurChiffrementStandard` avec
  `ServiceDeChiffrementEnClair()` injecté (voir
  `tests/adaptateurs/test_adaptateur_chiffrement.py`) ;
- HTTP sortant : `AdaptateurExecuteurDeRequetesMemoire` au lieu de `httpx` ;
- Albert : `ClientAlbertMemoire` au lieu du SDK.

## Constructeurs et fixtures

Données de test construites via des **constructeurs fluents** (`Constructeur…` +
`.avec_…(...).construis()`), exposés par des fixtures qui renvoient une **factory**
(un `Callable`) pour garantir une instance fraîche par test :

```python
reponse_question = (
    un_constructeur_de_reponse_question()
    .donnant_en_reponse("La réponse d'MQC")
    .avec_une_question("une question")
    .avec_les_paragraphes([un_constructeur_de_paragraphe().avec_contenu("...").construis()])
    .construis()
)
```

Fixtures d'assemblage : `une_configuration_complete`, `un_serveur_de_test`,
`un_serveur_de_test_complet`, `un_service_albert_avec_un_client_memoire` — elles câblent
les fakes par injection de dépendance (`ConfigurationQuestion(...)`, `ServiceAlbert(client=…,
reformulateur=…, reclasseur=…, executeur_de_requetes=…)`). Le déterminisme temporel passe
par le point d'extension dédié `Horloge.frise(dt.datetime(...))`, jamais par du patching.

## Structure d'un test

Arrange / Act / Assert, séparés par une ligne vide, l'action tenant en une expression :

```python
def test_ne_conserve_pas_les_paragraphes_en_cas_de_violation(
    une_configuration_complete, un_constructeur_de_reponse_question
):
    la_configuration, service_albert, _, _, _ = une_configuration_complete()
    service_albert.ajoute_reponse(
        un_constructeur_de_reponse_question()
        .avec_les_paragraphes([...])
        .avec_une_violation(ViolationMalveillance())
        .construis()
    )

    resultat = cree_conversation(
        la_configuration,
        DemandeConversationUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert resultat.interaction.reponse_question.paragraphes == []
```

## Outside-in vs inside-out

- **Outside-in** — on part de la frontière (route HTTP) et on descend. `tests/api/*`
  montent un serveur entièrement câblé avec des fakes (`un_serveur_de_test`), appellent via
  `fastapi.testclient.TestClient`, et vérifient le comportement HTTP **et** les effets sur
  les fakes injectés (`service_albert.question_recue`, `adaptateur_journal.les_evenements()`).
- **Inside-out** — on part d'un collaborateur isolé et on remonte.
  `tests/services/test_reclasseur_bge.py`, `tests/adaptateurs/*` instancient directement la
  classe sous test avec un client mémoire et assertent sur sa sortie.

On choisit selon ce qui exprime le mieux l'intention métier ; les deux styles cohabitent
dans la suite.

## Organisation des fichiers

`tests/` reflète `src/` : `tests/api/`, `tests/question/`, `tests/services/`,
`tests/infra/`, `tests/adaptateurs/`, `tests/schemas/`. Fixtures partagées dans le
`conftest.py` du niveau concerné (`tests/conftest.py` pour les constructeurs communs).
Un fichier de test par unité de comportement, nommé `test_<sujet>.py`.

## Anti-patterns à refuser

- `from unittest.mock import ...`, `Mock()`, `MagicMock()`, `patch(...)`,
  `monkeypatch.setattr(...)` pour simuler un comportement.
- Nom de test technique ou numéroté.
- Plusieurs intentions dans un même test (plusieurs blocs Act, assertions sans rapport).
- Tester un accès direct à une librairie tierce.
- Tester un simple getter/setter ou la forme d'une structure de données sans enjeu métier.
