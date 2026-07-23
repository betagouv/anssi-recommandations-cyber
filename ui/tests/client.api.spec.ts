import { estReponseConversation } from '../src/client.api';
import { describe, expect, it } from 'vitest';

describe('la validation de réponse API', () => {
  it('valide une réponse avec tous les champs requis incluant id de conversation', () => {
    const reponse = {
      reponse: 'une réponse',
      paragraphes: [],
      id_interaction: 'id1',
      question: 'une question',
      id_conversation: 'conv1',
    };

    expect(estReponseConversation(reponse)).toBe(true);
  });
});
