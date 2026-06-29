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
          'Les informations erronées sont les suivantes : informations'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Fausse',
            precisionsInformationsErronees:
              'Les informations erronées sont les suivantes : informations',
          },
          completude: {},
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('indique les sources adaptées', () => {
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Fausse',
            sourcesAdaptees:
              'Les sources adaptées sont les suivantes : les sources adaptées',
          },
          completude: {},
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('ne valide pas l’exactitude si les informations erronées sont trop longues', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        storeAvisUtilisateurBis.preciseLesInformationsErronees('a'.repeat(5001));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.exactitude.erreurs).toEqual({
          'informations-erronees':
            'Le champ `informations erronées` ne peut contenir que 5000 caractères maximum',
        });
      });

      it('ne valide pas l’exactitude si les informations erronées sont trop courtes', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        storeAvisUtilisateurBis.preciseLesInformationsErronees('a'.repeat(49));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.exactitude.erreurs).toEqual({
          'informations-erronees':
            'Le champ `informations erronées` doit contenir au moins 50 caractères minimum',
        });
      });

      it('ne valide pas l’exactitude si les sources adaptées sont trop longues', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Les informations erronées sont les suivantes : informations'
        );

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'a'.repeat(5001)
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.exactitude.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` ne peut contenir que 5000 caractères maximum',
        });
      });

      it('ne valide pas l’exactitude si les sources adaptées sont trop courtes', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Les informations erronées sont les suivantes : informations'
        );

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'a'.repeat(49)
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.exactitude.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum',
        });
      });

      it('conserve l’erreur des informations erronées', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Fausse',
            erreurs: { 'informations-erronees': 'Erreur' },
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'a'.repeat(49)
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.exactitude.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum',
          'informations-erronees': 'Erreur',
        });
      });

      it('conserve l’erreur des sources adaptées', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Fausse',
            erreurs: { 'sources-adaptees': 'Erreur' },
          },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseLesInformationsErronees('a'.repeat(49));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.exactitude.erreurs).toEqual({
          'sources-adaptees': 'Erreur',
          'informations-erronees':
            'Le champ `informations erronées` doit contenir au moins 50 caractères minimum',
        });
      });

      it('supprime l’erreur des informations erronées si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Fausse',
            erreurs: {
              'informations-erronees': 'Erreur infos',
              'sources-adaptees': 'Erreur sources',
            },
          },
          completude: {
            valeur: 'Bonne',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Les infromations erronées sont les suivantes : les informations erronées'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(
          storeMisAJour.exactitude.erreurs?.['informations-erronees']
        ).toBeUndefined();
        expect(storeMisAJour.exactitude.erreurs?.['sources-adaptees']).toBeDefined();
      });

      it('supprime l’erreur des sources adaptées si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Fausse',
            erreurs: {
              'sources-adaptees': 'Erreur sources',
              'informations-erronees': 'Erreur infos',
            },
          },
          completude: {
            valeur: 'Bonne',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLExactitude(
          'Les sources adaptées sont les suivantes : sources adaptées'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(
          storeMisAJour.exactitude.erreurs?.['informations-erronees']
        ).toBeDefined();
        expect(
          storeMisAJour.exactitude.erreurs?.['sources-adaptees']
        ).toBeUndefined();
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
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );
        storeAvisUtilisateurBis.preciseLesInformationsErronees(
          'Les informations erronées sont les suivantes : informations'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Fausse',
            sourcesAdaptees:
              'Les sources adaptées sont les suivantes : les sources adaptées',
            precisionsInformationsErronees:
              'Les informations erronées sont les suivantes : informations',
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
          'Les Informations manquantes sont les suivantes : infos'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {},
          completude: {
            valeur: 'Mauvaise',
            informationsManquantes:
              'Les Informations manquantes sont les suivantes : infos',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
      });

      it('indique les sources adaptées', () => {
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {},
          completude: {
            valeur: 'Mauvaise',
            sourcesAdaptees:
              'Les sources adaptées sont les suivantes : les sources adaptées',
          },
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
          'Les Informations manquantes sont les suivantes : infos'
        );
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            sourcesAdaptees:
              'Les sources adaptées sont les suivantes : les sources adaptées',
            informationsManquantes:
              'Les Informations manquantes sont les suivantes : infos',
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: true,
        });
      });

      it('ne valide pas la complétude si les informations manquantes sont trop longues', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        storeAvisUtilisateurBis.preciseLesInformationsManquantes('a'.repeat(5001));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.completude.erreurs).toEqual({
          'informations-manquantes':
            'Le champ `informations manquantes` ne peut contenir que 5000 caractères maximum',
        });
      });

      it('ne valide pas la complétude si les informations manquantes sont trop courtes', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Les sources adaptées sont les suivantes : les sources adaptées'
        );

        storeAvisUtilisateurBis.preciseLesInformationsManquantes('a'.repeat(49));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.completude.erreurs).toEqual({
          'informations-manquantes':
            'Le champ `informations manquantes` doit contenir au moins 50 caractères minimum',
        });
      });

      it('ne valide pas la complétude si les sources adaptées sont trop longues', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Les informations manquantes sont les suivantes : informations'
        );

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'a'.repeat(5001)
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.completude.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` ne peut contenir que 5000 caractères maximum',
        });
      });

      it('ne valide pas la complétude si les sources adaptées sont trop courtes', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });
        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Les informations manquantes sont les suivantes : informations'
        );

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'a'.repeat(49)
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.completude.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum',
        });
      });

      it('conserve l’erreur des informations manquantes', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            erreurs: { 'informations-manquantes': 'Erreur' },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'a'.repeat(49)
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.completude.erreurs).toEqual({
          'sources-adaptees':
            'Le champ `sources adaptées` doit contenir au moins 50 caractères minimum',
          'informations-manquantes': 'Erreur',
        });
      });

      it('conserve l’erreur des sources adaptées', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            erreurs: { 'sources-adaptees': 'Erreur' },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseLesInformationsManquantes('a'.repeat(49));

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(storeMisAJour.completude.erreurs).toEqual({
          'sources-adaptees': 'Erreur',
          'informations-manquantes':
            'Le champ `informations manquantes` doit contenir au moins 50 caractères minimum',
        });
      });

      it('supprime l’erreur des informations manquantes si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            erreurs: {
              'informations-manquantes': 'Erreur infos',
              'sources-adaptees': 'Erreur sources',
            },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Les informations manquantes sont les suivantes : les informations manquantes'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(
          storeMisAJour.completude.erreurs?.['informations-manquantes']
        ).toBeUndefined();
        expect(storeMisAJour.completude.erreurs?.['sources-adaptees']).toBeDefined();
      });

      it('supprime l’erreur des sources adaptées si elle est corrigée', () => {
        storeAvisUtilisateurBis.initialise({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            erreurs: {
              'sources-adaptees': 'Erreur sources',
              'informations-manquantes': 'Erreur infos',
            },
          },
          idConversation: '123',
          idInteraction: '456',
          estValide: false,
        });

        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Les informations manquantes sont les suivantes : infos'
        );

        const storeMisAJour = get(storeAvisUtilisateurBis);
        expect(storeMisAJour.estValide).toBe(false);
        expect(
          storeMisAJour.completude.erreurs?.['informations-manquantes']
        ).toBeDefined();
        expect(
          storeMisAJour.completude.erreurs?.['sources-adaptees']
        ).toBeUndefined();
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
