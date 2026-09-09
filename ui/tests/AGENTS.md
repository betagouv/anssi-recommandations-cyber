# Instructions agent — Tests front (`ui/tests/`)

Comment on écrit les tests TypeScript de l'interface MesQuestionsCyber. Complète
[`../../AGENTS.md`](../../AGENTS.md) et [`tests/AGENTS.md`](../../tests/AGENTS.md) (mêmes
règles d'or, transposées au front).

Outil : depuis `ui/`, `npm run test` (ou `pnpm run test`) — enchaîne `svelte-check` puis
`vitest run`. Méthode : TDD strict → skill `tdd`.

## Règles d'or

1. **Rédaction en français** — libellés `describe` / `it`, constructeurs, variables.
2. **Jamais de mock ni de librairie de mock** — pas de `vi.mock`, `vi.fn`, `vi.spyOn` pour
   simuler un comportement. On **réassigne les adaptateurs injectés** (voir plus bas), qui
   sont conçus pour ça.
3. **Le libellé du test traduit l'intention** — `it('conserve une sauvegarde de la
conversation en cas d'échec lors de l'appel à l'API', …)`.
4. **Un test ne vérifie qu'une seule chose** — une intention par `it`.
5. **Les intentions sont fonctionnelles / métier**, pas techniques.
6. **On ne teste pas les getters / setters.**
7. **On ne teste pas les librairies tierces** (`pdfjs-dist`, `marked`, `dompurify`, `zod`)
   — elles sont isolées derrière un adaptateur (`adaptateurPDF`, `nettoyeurDOM`) qu'on
   remplace en test.
8. **Outside-in ou inside-out selon le cas** — cf. `tests/AGENTS.md`.

## Nommer un test

`describe` = le sujet, `it` = le comportement attendu, en français.

```ts
describe('le store de conversation', () => {
  it('crée une conversation', async () => { … });
  it('transmet la question de l’utilisateur lors de la création d’une conversation', …);
  it('ne mets pas à jour l’id de conversation lors de l’ajout d’une interaction', …);
});

describe('Le validateur de la question utilisateur', () => {
  it('sont invalides lorsque la question contient plus de 5000 caractère', …);
});
```

À éviter : `it('works')`, `it('test creeUneConversation')`, un libellé qui nomme une
méthode plutôt qu'un comportement.

## Fakes injectés (pas de mocks)

Le code expose des **adaptateurs / clients singletons** (`clientAPI`, `nettoyeurDOM`,
`adaptateurPDF`, …) dont les méthodes sont **réassignables**. En test, on les remplace par
une implémentation locale qui décrit la situation voulue :

```ts
beforeEach(() => {
  nettoyeurDOM.nettoie = async (contenu: string) => contenu;
  adaptateurPDF.pagePDFenPNG = () => Promise.resolve(new Blob());
});

it('transmet la question de l’utilisateur …', async () => {
  let messageRecu;
  clientAPI.creeUneConversation = async (message) => {
    messageRecu = message; // le fake enregistre ce qu'il reçoit
    return { erreur: 'une erreur' }; // …et renvoie la réponse choisie
  };

  await storeConversation.ajouteMessageUtilisateur({ question: 'une question ?' });

  expect(messageRecu).toStrictEqual({ question: 'une question ?' });
});
```

- On **capture les arguments reçus** dans un `let` local plutôt qu'avec un spy.
- On **rétablit l'état** entre les tests (`beforeEach` / `afterEach`) : réassignation des
  adaptateurs, `storeConversation.initialise({...})`, `storeXxx` remis à zéro.
- Un besoin non couvert par un adaptateur existant → on introduit un adaptateur injectable,
  pas un `vi.mock`.

## Constructeurs

Données de test via des **constructeurs fluents**, dans un fichier **sans `.spec`**
(ex. `ui/tests/stores/constructeurDeParagraphe.ts`) :

```ts
export const unConstructeurParagraphe = () => new ConstructeurDeParagraphe();

unConstructeurParagraphe()
  .avecURLDocument('http://demo.local/source?document=mon-doc.pdf')
  .construis();
```

## Quoi tester

- La **logique** : stores (`ui/src/stores/`), validateurs et utilitaires
  (`ui/src/composants/ValidateurQuestionUtilisateur.ts`), client API
  (`estReponseConversation`).
- Le **comportement observable** vu de l'extérieur : état du store après une action, appel
  transmis à `clientAPI`, mise à jour de `storeAffichage` en cas d'erreur.
- **Pas** le rendu interne des composants `.svelte` ni le détail des librairies.

`svelte-check` (inclus dans `pnpm run test`) garde les types et les composants sous
contrôle — inutile d'écrire des tests pour ça.

## Organisation des fichiers

`ui/tests/` reflète `ui/src/` : `ui/tests/stores/`, `ui/tests/composants/`, etc. Fichiers
de test en `*.spec.ts` ; fichiers d'aide (constructeurs, fixtures) sans `.spec`.

## Anti-patterns à refuser

- `vi.mock(...)`, `vi.fn(...)`, `vi.spyOn(...)`, `vi.useFakeTimers()` pour simuler un
  comportement.
- Libellé `describe` / `it` en anglais ou purement technique.
- Plusieurs intentions dans un même `it`.
- Tester `pdfjs-dist`, `marked`, `dompurify` directement plutôt que l'adaptateur qui les
  enveloppe.
- Assertions sur un getter/setter ou sur la forme d'un objet sans enjeu métier.
