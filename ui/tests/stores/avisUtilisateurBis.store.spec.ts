import {
  Completude,
  Exactitude,
  storeAvisUtilisateurBis,
} from '../../src/stores/avisUtilisateurBis.store';
import { get } from 'svelte/store';
import { beforeEach, describe, expect, it } from 'vitest';

describe('le store de conversation', () => {
  beforeEach(() => {
    storeAvisUtilisateurBis.initialise({
      exactitude: { valeur: 'Bonne' },
      completude: { valeur: 'Bonne' },
      idConversation: '123',
      idInteraction: '456',
    });
  });

  describe('dans le cas de l’exactitude', () => {
    it('modifie la valeur', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Très bonne');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Très bonne' },
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    it('peut ajouter un commentaire lorsque la valeur est différente de fausse', () => {
      storeAvisUtilisateurBis.commenteLExactitude('La réponse est exacte');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    it('ne peut pas ajouter de commentaire lorsque la valeur est fausse', () => {
      storeAvisUtilisateurBis.initialise({
        exactitude: { valeur: 'Fausse' },
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
      });
      storeAvisUtilisateurBis.commenteLExactitude('La réponse est fausse');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Fausse' },
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    it('ne peut pas préciser les informations erronées lorsque la valeur n’est pas fausse', () => {
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
      });
    });

    it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas fausse', () => {
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
      });
    });

    describe('dans le cas où la valeur est fausse', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Fausse' },
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
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
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
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
          completude: { valeur: 'Bonne' },
          idConversation: '123',
          idInteraction: '456',
        });
      });
    });
  });

  describe('dans le cas de la complétude', () => {
    it('modifie la valeur', () => {
      storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Très bonne');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Très bonne' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    it('peut ajouter un commentaire lorsque la valeur est différente de mauvaise', () => {
      storeAvisUtilisateurBis.commenteLaCompletude('La réponse est exacte');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    it('ne peut pas ajouter de commentaire lorsque la valeur est mauvaise', () => {
      storeAvisUtilisateurBis.initialise({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Mauvaise' },
        idConversation: '123',
        idInteraction: '456',
      });
      storeAvisUtilisateurBis.commenteLaCompletude('La réponse est fausse');

      const conversation = get(storeAvisUtilisateurBis);
      expect(conversation).toStrictEqual({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Mauvaise' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    it('ne peut pas préciser les informations manquantes lorsque la valeur n’est pas mauvaise', () => {
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
      });
    });

    it('ne peut pas indiquer les sources adaptées lorsque la valeur n’est pas mauvaise', () => {
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
      });
    });

    describe('dans le cas où la valeur est mauvaise', () => {
      beforeEach(() => {
        storeAvisUtilisateurBis.initialise({
          exactitude: { valeur: 'Bonne' },
          completude: { valeur: 'Mauvaise' },
          idConversation: '123',
          idInteraction: '456',
        });
      });

      it('précise les informations manquantes', () => {
        storeAvisUtilisateurBis.preciseLesInformationsManquantes(
          'Informations manquantes'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: {
            valeur: 'Mauvaise',
            informationsManquantes: 'Informations manquantes',
          },
          idConversation: '123',
          idInteraction: '456',
        });
      });

      it('indique les sources adaptées', () => {
        storeAvisUtilisateurBis.indiqueLesSourcesAdapteesPourLaCompletude(
          'Sources adaptées'
        );

        const conversation = get(storeAvisUtilisateurBis);
        expect(conversation).toStrictEqual({
          exactitude: {
            valeur: 'Bonne',
          },
          completude: { valeur: 'Mauvaise', sourcesAdaptees: 'Sources adaptées' },
          idConversation: '123',
          idInteraction: '456',
        });
      });
    });
  });

  describe('dans le cas de la validation', () => {
    beforeEach(() => {
      storeAvisUtilisateurBis.initialise({
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Bonne' },
        idConversation: '123',
        idInteraction: '456',
      });
    });

    type TestAvis = {
      exactitude: Exactitude;
      completude: Completude;
      estValide: boolean;
    };

    it.each<TestAvis>([
      {
        exactitude: { valeur: 'Bonne' },
        completude: { valeur: 'Bonne' },
        estValide: true,
      },
      {
        exactitude: { valeur: 'Bonne', commentaire: 'OK' },
        completude: { valeur: 'Bonne', commentaire: 'OK' },
        estValide: true,
      },
      {
        exactitude: { valeur: 'Très bonne' },
        completude: { valeur: 'Très bonne' },
        estValide: true,
      },
      {
        exactitude: { valeur: 'Très bonne', commentaire: 'OK' },
        completude: { valeur: 'Très bonne', commentaire: 'OK' },
        estValide: true,
      },
      {
        exactitude: { valeur: 'Correcte' },
        completude: { valeur: 'Correcte' },
        estValide: true,
      },
      {
        exactitude: { valeur: 'Correcte', commentaire: 'OK' },
        completude: { valeur: 'Correcte', commentaire: 'OK' },
        estValide: true,
      },
      {
        exactitude: {
          valeur: 'Fausse',
          precisionsInformationsErronees: 'Informations erronées',
          sourcesAdaptees: 'Sources Adaptées',
        },
        completude: { valeur: 'Très bonne' },
        estValide: true,
      },
      {
        exactitude: {
          valeur: 'Bonne',
        },
        completude: {
          valeur: 'Mauvaise',
          sourcesAdaptees: 'Sources Adaptées',
          informationsManquantes: 'Informations manquantes',
        },
        estValide: true,
      },
      {
        exactitude: {
          valeur: 'Fausse',
          precisionsInformationsErronees: '  ',
          sourcesAdaptees: 'Sources Adaptées',
        },
        completude: { valeur: 'Très bonne' },
        estValide: false,
      },
      {
        exactitude: {
          valeur: 'Fausse',
          precisionsInformationsErronees: 'Informations erronées',
          sourcesAdaptees: '  ',
        },
        completude: { valeur: 'Très bonne' },
        estValide: false,
      },
      {
        exactitude: {
          valeur: 'Bonne',
        },
        completude: {
          valeur: 'Mauvaise',
          sourcesAdaptees: '   ',
          informationsManquantes: 'Informations manquantes',
        },
        estValide: false,
      },

      {
        exactitude: {
          valeur: 'Bonne',
        },
        completude: {
          valeur: 'Mauvaise',
          sourcesAdaptees: 'Sources Adaptées',
          informationsManquantes: '  ',
        },
        estValide: false,
      },
      {
        exactitude: { valeur: 'Fausse' },
        completude: { valeur: 'Très bonne' },
        estValide: false,
      },
      {
        exactitude: { valeur: 'Très bonne' },
        completude: { valeur: 'Mauvaise' },
        estValide: false,
      },
      {
        exactitude: { valeur: 'Fausse' },
        completude: { valeur: 'Mauvaise' },
        estValide: false,
      },
    ])(
      'Valide Exactitude : $exactitude.valeur - Complétude : $completude.valeur - Commentaire : $exactitude.commentaire - $completude.commentaire',
      (avis: TestAvis) => {
        storeAvisUtilisateurBis.initialise({
          idConversation: '123',
          idInteraction: '456',
          exactitude: avis.exactitude,
          completude: avis.completude,
        });

        expect(storeAvisUtilisateurBis.estValide()).toBe(avis.estValide);
      }
    );
  });
});
