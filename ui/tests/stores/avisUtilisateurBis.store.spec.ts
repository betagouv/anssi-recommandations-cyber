import { storeAvisUtilisateurBis } from '../../src/stores/avisUtilisateurBis.store';
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

  it("modifie la valeur de l'exactitude", () => {
    storeAvisUtilisateurBis.modifieLaValeurDeLExactitude('Très bonne');

    const conversation = get(storeAvisUtilisateurBis);
    expect(conversation).toStrictEqual({
      exactitude: { valeur: 'Très bonne' },
      completude: { valeur: 'Bonne' },
      idConversation: '123',
      idInteraction: '456',
    });
  });

  it('peut ajouter un commentaire lorsque l’exactitude est différente de fausse', () => {
    storeAvisUtilisateurBis.commenteLExactitude('La réponse est exacte');

    const conversation = get(storeAvisUtilisateurBis);
    expect(conversation).toStrictEqual({
      exactitude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
      completude: { valeur: 'Bonne' },
      idConversation: '123',
      idInteraction: '456',
    });
  });

  it('ne peut pas ajouter de commentaire lorsque l’exactitude est fausse', () => {
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

  it('modifie la valeur de la complétude', () => {
    storeAvisUtilisateurBis.modifieLaValeurDeLaCompletude('Très bonne');

    const conversation = get(storeAvisUtilisateurBis);
    expect(conversation).toStrictEqual({
      exactitude: { valeur: 'Bonne' },
      completude: { valeur: 'Très bonne' },
      idConversation: '123',
      idInteraction: '456',
    });
  });

  it('peut ajouter un commentaire lorsque la complétude est différente de fausse', () => {
    storeAvisUtilisateurBis.commenteLaCompletude('La réponse est exacte');

    const conversation = get(storeAvisUtilisateurBis);
    expect(conversation).toStrictEqual({
      exactitude: { valeur: 'Bonne' },
      completude: { valeur: 'Bonne', commentaire: 'La réponse est exacte' },
      idConversation: '123',
      idInteraction: '456',
    });
  });

  it('ne peut pas ajouter de commentaire lorsque la complétude est mauvaise', () => {
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
});
