import { describe, it, expect, beforeEach } from 'vitest';
import {
  nettoyeurDOM,
  storeConversation,
} from '../../src/stores/conversation.store';
import {
  estReponseMessageUtilisateur,
  type ReponseEnErreur,
  type ReponseMessageUtilisateurAPI,
} from '../../src/client.api';
import { get } from 'svelte/store';

describe('le store de conversation', () => {
  beforeEach(() => {
    nettoyeurDOM.nettoie = async (contenu: string) => contenu;
  });
  it('renvoie une conversation en édition vide', () => {
    const conversation = get(storeConversation);
    expect(conversation).toStrictEqual({
      messages: [],
      derniereQuestion: '',
      conversationId: null,
    });
  });

  it('ajoute un message utilisateur', () => {
    storeConversation.ajouteMessageUtilisateur('une question ?');
    const conversation = get(storeConversation);

    expect(conversation).toStrictEqual({
      messages: [{ contenu: 'une question ?', emetteur: 'utilisateur' }],
      derniereQuestion: 'une question ?',
      conversationId: null,
    });
  });

  it('on peut ajouter un message système', async () => {
    await storeConversation.ajouteMessageSysteme('la reponse', [], 'id1', 'id1');
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
      conversationId: 'id1',
    });
  });
});

describe('la validation de réponse API', () => {
  it('valide une réponse avec tous les champs requis incluant conversation_id', () => {
    const reponse = {
      reponse: 'une réponse',
      paragraphes: [],
      interaction_id: 'id1',
      question: 'une question',
      conversation_id: 'conv1',
    };

    expect(estReponseMessageUtilisateur(reponse)).toBe(true);
  });

  it('invalide une réponse sans conversation_id', () => {
    const reponse = {
      reponse: 'une réponse',
      paragraphes: [],
      interaction_id: 'id1',
      question: 'une question',
    } as unknown as ReponseMessageUtilisateurAPI | ReponseEnErreur;

    expect(estReponseMessageUtilisateur(reponse)).toBe(false);
  });
});
