import {
  AvisUtilisateurBis,
  SourcesAdaptees,
  Pertinence,
  storeAvisUtilisateurBis,
  ErreursPotentiellesSourcesAdaptees,
} from '../../src/stores/avisUtilisateurBis.store';
import { get } from 'svelte/store';
import { beforeEach, describe, expect, it } from 'vitest';

describe('le store des avis', () => {
  describe('dans le cas de la pertinence', () => {
    beforeEach(() => {
      storeAvisUtilisateurBis.initialise({
        pertinence: {} as Pertinence,
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('modifie la valeur', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence('Très pertinente');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: { valeur: 'Très pertinente' },
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('peut ajouter un commentaire lorsque la valeur est différente de fausse', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence('Pertinente');

      storeAvisUtilisateurBis.commenteLaPertinence('La réponse est exacte');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: { valeur: 'Pertinente', commentaire: 'La réponse est exacte' },
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas ajouter de commentaire lorsque la valeur est fausse', () => {
      storeAvisUtilisateurBis.initialise({
        pertinence: { valeur: 'Erronée' },
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
      storeAvisUtilisateurBis.commenteLaPertinence('La réponse est fausse');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: { valeur: 'Erronée' },
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas préciser les informations erronées lorsque la valeur n’est pas erronée', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence('Pertinente');

      storeAvisUtilisateurBis.preciseLesInformationsErronees(
        'Informations erronées'
      );

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: {
          valeur: 'Pertinente',
        },
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    describe('dans le cas ou les sources sont adaptées', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {} as Pertinence,
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('modifie la valeur', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence('Très pertinente');

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: { valeur: 'Très pertinente' },
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('peut ajouter un commentaire lorsque la valeur est différente de erronée', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence('Pertinente');

        storeAvisUtilisateurBis.commenteLaPertinence('La réponse est exacte');

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: { valeur: 'Pertinente', commentaire: 'La réponse est exacte' },
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne peut pas ajouter de commentaire lorsque la valeur est erronée', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Erronée' },
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.commenteLaPertinence('La réponse est fausse');

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: { valeur: 'Erronée' },
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ne peut pas préciser les informations erronées lorsque la valeur n’est pas erronée', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaPertinence('Pertinente');

        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Informations erronées'
        );

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });
    });

    describe('où la valeur est erronée', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Erronée' },
          sourcesAdaptees: {} as SourcesAdaptees,
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ajoute des précisions sur les informations erronées', () => {
        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Les informations erronées sont les suivantes : informations'
        );

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: {
            valeur: 'Erronée',
            precisionsInformationsErronees:
              'Les informations erronées sont les suivantes : informations',
          },
          sourcesAdaptees: {} as SourcesAdaptees,
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('supprime l’erreur des informations erronées si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {
            valeur: 'Erronée',
            erreurs: {
              'informations-erronees': 'Erreur infos',
            },
          },
          sourcesAdaptees: {
            valeur: 'Oui, partiellement',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Les infromations erronées sont les suivantes : les informations erronées'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(true);
        expect(
          storeMisAJour.pertinence.erreurs?.['informations-erronees']
        ).toBeUndefined();
      });
    });
  });

  describe('dans le cas des sources adaptées', () => {
    beforeEach(() => {
      storeAvisUtilisateurBis.initialise({
        pertinence: {} as Pertinence,
        sourcesAdaptees: {} as SourcesAdaptees,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('modifie la valeur', () => {
      storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees('Oui, tout à fait');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: {} as Pertinence,
        sourcesAdaptees: { valeur: 'Oui, tout à fait' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('peut ajouter un commentaire lorsque la valeur est différente de Non', () => {
      storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees(
        'Oui, partiellement'
      );
      storeAvisUtilisateurBis.commenteLesSourcesAdaptees('La réponse est exacte');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: {} as Pertinence,
        sourcesAdaptees: {
          valeur: 'Oui, partiellement',
          commentaire: 'La réponse est exacte',
        },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas ajouter de commentaire lorsque la valeur est non', () => {
      storeAvisUtilisateurBis.initialise({
        pertinence: { valeur: 'Pertinente' },
        sourcesAdaptees: { valeur: 'Non' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
      storeAvisUtilisateurBis.commenteLesSourcesAdaptees('La réponse est fausse');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: { valeur: 'Pertinente' },
        sourcesAdaptees: { valeur: 'Non' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas Non', () => {
      storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees(
        'Oui, partiellement'
      );

      storeAvisUtilisateurBis.indiqueLesSourcesAdaptees('Sources adaptées');

      const avisRetourne = get(storeAvisUtilisateurBis);
      expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
        pertinence: {} as Pertinence,
        sourcesAdaptees: { valeur: 'Oui, partiellement' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    describe('dans le cas où la pertinence n’est pas erronée', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: {} as SourcesAdaptees,
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('modifie la valeur', () => {
        storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees(
          'Oui, tout à fait'
        );

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: { valeur: 'Oui, tout à fait' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('peut ajouter un commentaire lorsque la valeur est différente de fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees(
          'Oui, partiellement'
        );

        storeAvisUtilisateurBis.commenteLesSourcesAdaptees('La réponse est exacte');

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: {
            valeur: 'Oui, partiellement',
            commentaire: 'La réponse est exacte',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne peut pas ajouter de commentaire lorsque la valeur est mauvaise', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: { valeur: 'Non' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.commenteLesSourcesAdaptees('La réponse est fausse');

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: { valeur: 'Non' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDesSourcesAdaptees(
          'Oui, partiellement'
        );

        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees('Sources adaptées');

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: { valeur: 'Oui, partiellement' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });
    });

    describe('où la valeur est Non', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {} as Pertinence,
          sourcesAdaptees: { valeur: 'Non' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('indique les sources adaptées', () => {
        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: {} as Pertinence,
          sourcesAdaptees: {
            valeur: 'Non',
            liste: 'Les sources adaptées sont les suivantes : les sources adaptées',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('valide les sources adaptées', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: { valeur: 'Non', raisons: ['Sources peu pertinentes'] },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        const avisRetourne = get(storeAvisUtilisateurBis);
        expect(avisRetourne).toStrictEqual<AvisUtilisateurBis>({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: {
            valeur: 'Non',
            liste: 'Les sources adaptées sont les suivantes : les sources adaptées',
            raisons: ['Sources peu pertinentes'],
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne valide pas si les sources adaptées sont trop longues', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: { valeur: 'Non' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees('a'.repeat(5001));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.sourcesAdaptees.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` ne peut contenir que 5000 caractères maximum',
        });
      });

      it('ne valide pas si les sources adaptées sont trop courtes', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: { valeur: 'Non' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees('a'.repeat(49));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.sourcesAdaptees.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum',
        });
      });

      it('ne valide pas si il n’y a pas de raison', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: {
            valeur: 'Non',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
      });

      it('peut ajouter une raison pour lesquelles les sources ne sont pas adaptées', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: {
            valeur: 'Non',
            liste: 'Les sources adaptées sont les suivantes : les sources adaptées',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseEnQuoiLesSourcesNeSontPasAdaptees([
          'Sources peu pertinentes',
        ]);

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(true);
      });

      it('ne valide pas si aucune raison donnée pour lesquelles les sources ne sont pas adaptées', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: { valeur: 'Pertinente' },
          sourcesAdaptees: {
            valeur: 'Non',
            liste: 'Les sources adaptées sont les suivantes : les sources adaptées',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseEnQuoiLesSourcesNeSontPasAdaptees([]);

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.sourcesAdaptees.erreurs).toEqual({
          raisons:
            'Veuillez préciser au moins une raison pour lesquelles les sources ne sont pas adaptées.',
        });
      });

      it('conserve l’erreur des sources adaptées', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: {
            valeur: 'Non',
            erreurs: { 'sources-adaptees': 'Erreur' },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseEnQuoiLesSourcesNeSontPasAdaptees([]);

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(
          storeMisAJour.sourcesAdaptees.erreurs
        ).toStrictEqual<ErreursPotentiellesSourcesAdaptees>({
          'sources-adaptees': 'Erreur',
          raisons:
            'Veuillez préciser au moins une raison pour lesquelles les sources ne sont pas adaptées.',
        });
      });

      it('conserve l’erreur des raisons pour lesquelles les sources ne sont pas adaptées.', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: {
            valeur: 'Non',
            erreurs: {
              raisons: 'Une erreur',
            },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees('a'.repeat(49));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(
          storeMisAJour.sourcesAdaptees.erreurs
        ).toStrictEqual<ErreursPotentiellesSourcesAdaptees>({
          raisons: 'Une erreur',
          'sources-adaptees':
            'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum',
        });
      });

      it('supprime l’erreur des sources adaptées si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: {
            valeur: 'Non',
            raisons: ['Sources peu pertinentes'],
            erreurs: {
              'sources-adaptees': 'Erreur sources',
            },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdaptees(
          'Les informations manquantes sont les suivantes : infos'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(true);
        expect(
          storeMisAJour.sourcesAdaptees.erreurs?.['sources-adaptees']
        ).toBeUndefined();
      });

      it('supprime l’erreur de la raison des sources non adaptées si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          pertinence: {
            valeur: 'Pertinente',
          },
          sourcesAdaptees: {
            valeur: 'Non',
            liste: 'Les sources adaptées sont les suivantes : les sources adaptées',
            raisons: [],
            erreurs: {
              raisons: 'Raisons erreur',
            },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseEnQuoiLesSourcesNeSontPasAdaptees([
          'Sources manquantes',
        ]);

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(true);
        expect(storeMisAJour.sourcesAdaptees.erreurs?.['raisons']).toBeUndefined();
      });
    });
  });
});
