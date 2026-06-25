import {
  Completude,
  Exactitude,
  storeAvisUtilisateurBis,
} from '../../src/stores/avisUtilisateurBis.store';
import { get } from 'svelte/store';
import { beforeEach, describe, expect, it } from 'vitest';

describe('le store de conversation', () => {
  describe('dans le cas de l’exactitude', () => {
    beforeEach(() => {
      storeAvisUtilisateurBis.initialise({
        exactitude: {} as Exactitude,
        completude: {} as Completude,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('modifie la valeur', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Très bonne');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Très bonne' },
        completude: {},
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('peut ajouter un commentaire lorsque la valeur est différente de fausse', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Bonne');

      storeAvisUtilisateurBis.commenteLExactitude('La réponse est exacte');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
        completude: {},
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas ajouter de commentaire lorsque la valeur est fausse', () => {
      storeAvisUtilisateurBis.initialise({
        exactitude: { valeur: 'Fausse' },
        completude: {} as Completude,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
      storeAvisUtilisateurBis.commenteLExactitude('La réponse est fausse');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Fausse' },
        completude: {},
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas préciser les informations erronées lorsque la valeur n’est pas fausse', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Bonne');

      storeAvisUtilisateurBis.preciseLesInformationsErronees(
        'Informations erronées'
      );

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: {
          valeur: 'Bonne',
        },
        completude: {},
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas fausse', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Bonne');

      storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
        'Sources adaptées'
      );

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: {
          valeur: 'Bonne',
        },
        completude: {},
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    describe('dans le cas ou la completude n’est pas mauvaise', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {} as Exactitude,
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('modifie la valeur', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Très bonne');

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: { valeur: 'Très bonne' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('peut ajouter un commentaire lorsque la valeur est différente de fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Bonne');

        storeAvisUtilisateurBis.commenteLExactitude('La réponse est exacte');

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne peut pas ajouter de commentaire lorsque la valeur est fausse', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.commenteLExactitude('La réponse est fausse');

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ne peut pas préciser les informations erronées lorsque la valeur n’est pas fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Bonne');

        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Informations erronées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Bonne');

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });
    });

    describe('où la valeur est fausse', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: {} as Completude,
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ajoute des précisions sur les informations erronées', () => {
        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Informations erronées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Fausse',
            precisionsInformationsErronees: 'Informations erronées',
          },
          completude: {},
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('indique les sources adaptées', () => {
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Fausse',
            sourcesAdaptees: 'Sources adaptées',
          },
          completude: {},
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('valide l’exactitude', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Sources adaptées'
        );
        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Informations erronées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Fausse',
            sourcesAdaptees: 'Sources adaptées',
            precisionsInformationsErronees: 'Informations erronées',
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });
    });
  });

  describe('dans le cas de la complétude', () => {
    beforeEach(() => {
      storeAvisUtilisateurBis.initialise({
        exactitude: {} as Exactitude,
        completude: {} as Completude,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('modifie la valeur', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Très bonne');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: {},
        completude: { valeur: 'Très bonne' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('peut ajouter un commentaire lorsque la valeur est différente de mauvaise', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Bonne');
      storeAvisUtilisateurBis.commenteLaCompletude('La réponse est exacte');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: {},
        completude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas ajouter de commentaire lorsque la valeur est mauvaise', () => {
      storeAvisUtilisateurBis.initialise({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Mauvaise' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
      storeAvisUtilisateurBis.commenteLaCompletude('La réponse est fausse');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Mauvaise' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas préciser les informations manquantes lorsque la valeur n’est pas mauvaise', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Bonne');

      storeAvisUtilisateurBis.preciseLesInformationsManquantes(
        'Informations manquantes'
      );

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: {},
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas mauvaise', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Bonne');

      storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
        'Sources adaptées'
      );

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: {},
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    describe('dans le cas ou l’exactitude n’est pas mauvaise', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: {} as Completude,
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('modifie la valeur', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Très bonne');

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Très bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('peut ajouter un commentaire lorsque la valeur est différente de fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Bonne');

        storeAvisUtilisateurBis.commenteLaCompletude('La réponse est exacte');

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne peut pas ajouter de commentaire lorsque la valeur est mauvaise', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.commenteLaCompletude('La réponse est fausse');

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ne peut pas préciser les informations erronées lorsque la valeur n’est pas fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Bonne');

        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Informations manquantes'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas fausse', () => {
        storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Bonne');

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });
    });

    describe('où la valeur est mauvaise', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {} as Exactitude,
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('précise les informations manquantes', () => {
        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Informations manquantes'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {},
          completude: {
            valeur: 'Mauvaise',
            informationsManquantes: 'Informations manquantes',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('indique les sources adaptées', () => {
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {},
          completude: { valeur: 'Mauvaise', sourcesAdaptees: 'Sources adaptées' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('valide la complétude', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Informations manquantes'
        );
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            sourcesAdaptees: 'Sources adaptées',
            informationsManquantes: 'Informations manquantes',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });
    });
  });

  describe('dans le cas où les informations et sources sont à fournir', () => {
    beforeEach(() => {
      storeAvisUtilisateurBis.initialise({
        exactitude: {} as Exactitude,
        completude: {} as Completude,
        idConversation: '123',
        idInteraction: '456',
        estValide: false,
      });
    });

    it('ne valide pas l’avis si seule la complétude est saisie', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Mauvaise');
      storeAvisUtilisateurBis.commenteLaCompletude('La complétude est mauvaise');
      storeAvisUtilisateurBis.preciseLesInformationsManquantes(
        'Informations manquantes'
      );
      storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
        'Sources adaptées'
      );

      const avis = get(storeAvisUtilisateurBis);
      expect(avis.estValide).toBe(false);
    });

    it('ne valide pas l’avis si seule l’exactitude est saisie', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Fausse');
      storeAvisUtilisateurBis.commenteLExactitude('L’exactitude est mauvaise');
      storeAvisUtilisateurBis.preciseLesInformationsErronees(
        'Informations erronées'
      );
      storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
        'Sources adaptées'
      );

      const avis = get(storeAvisUtilisateurBis);
      expect(avis.estValide).toBe(false);
    });
  });
});
