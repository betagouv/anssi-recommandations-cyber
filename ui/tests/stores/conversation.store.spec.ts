import { describe, it, expect, beforeEach } from 'vitest';
import {
  nettoyeurDOM,
  storeConversation,
} from '../../src/stores/conversation.store';
import { get } from 'svelte/store';

describe('le store de conversation', () => {
  beforeEach(() => {
    nettoyeurDOM.nettoie = async (contenu: string) => contenu;
  });
  it('renvoie une conversation en édition vide', () => {
    const conversation = get(storeConversation);
    expect(conversation).toStrictEqual({ messages: [], derniereQuestion: '' });
  });

  it('ajoute un message utilisateur', () => {
    storeConversation.ajouteMessageUtilisateur('une question ?');
    const conversation = get(storeConversation);

    expect(conversation).toStrictEqual({
      messages: [{ contenu: 'une question ?', emetteur: 'utilisateur' }],
      derniereQuestion: 'une question ?',
    });
  });

  it('on peut ajouter un message système', async () => {
    await storeConversation.ajouteMessageSysteme('la reponse', [], 'id1');
    const conversation = get(storeConversation);

    expect(conversation).toStrictEqual({
      messages: [
        { contenu: 'une question ?', emetteur: 'utilisateur' },
        {
          contenu: 'la reponse',
          emetteur: 'systeme',
          contenuMarkdown: 'la reponse',
          references: [],
          idInteraction: 'id1',
        },
      ],
      derniereQuestion: 'une question ?',
    });
  });
});
