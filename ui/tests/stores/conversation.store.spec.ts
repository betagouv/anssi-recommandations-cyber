import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import {
  nettoyeurDOM,
  storeConversation,
} from '../../src/stores/conversation.store';
import {
  clientAPI,
  estReponseMessageUtilisateur,
  type ReponseEnErreur,
  type ReponseMessageUtilisateurAPI,
} from '../../src/client.api';
import { get } from 'svelte/store';
import { storeAffichage } from '../../src/stores/affichage.store.ts';

describe('le store de conversation', () => {
  beforeEach(() => {
    nettoyeurDOM.nettoie = async (contenu: string) => contenu;
  });

  afterEach(() => {
    storeConversation.initialise({
      messages: [],
      derniereQuestion: '',
      idConversation: null,
    });
  });

  it('renvoie une conversation en édition vide', () => {
    const conversation = get(storeConversation);

    expect(conversation).toStrictEqual({
      messages: [],
      derniereQuestion: '',
      idConversation: null,
    });
  });

  it('ajoute un message utilisateur', async () => {
    clientAPI.publieMessageUtilisateurAPI = async () => ({
      reponse: 'une réponse',
      paragraphes: [],
      interaction_id: 'id-interaction',
      question: 'une question ?',
      conversation_id: 'id-conversation',
    });
    await storeConversation.ajouteMessageUtilisateur(
      { question: 'une question ?' },
      async () => ({
        reponse: 'une réponse',
        paragraphes: [],
        interaction_id: 'id-interaction',
        question: 'une question ?',
        conversation_id: 'id-conversation',
      })
    );

    const conversation = get(storeConversation);
    expect(conversation).toStrictEqual({
      messages: [
        { contenu: 'une question ?', emetteur: 'utilisateur' },
        {
          contenu: 'une réponse',
          contenuMarkdown: 'une réponse',
          emetteur: 'systeme',
          references: [],
          idInteraction: 'id-interaction',
        },
      ],
      derniereQuestion: 'une question ?',
      idConversation: 'id-conversation',
    });
  });

  it('conserve une sauvegarde de la conversation en cas d’échec lors de l’appel à l’API', async () => {
    clientAPI.publieMessageUtilisateurAPI = async () => ({
      erreur: 'une erreur',
    });
    storeConversation.initialise({
      messages: [
        { contenu: 'une question ?', emetteur: 'utilisateur' },
        {
          contenu: 'une réponse',
          contenuMarkdown: 'une réponse',
          emetteur: 'systeme',
          references: [],
          idInteraction: 'id-interaction',
        },
      ],
      derniereQuestion: 'une question ?',
      idConversation: 'id-conversation',
    });

    await storeConversation.ajouteMessageUtilisateur(
      { question: 'une nouvelle question ?' },
      async () => ({
        erreur: 'une erreur',
      })
    );

    const conversation = get(storeConversation);
    expect(conversation).toStrictEqual({
      messages: [
        { contenu: 'une question ?', emetteur: 'utilisateur' },
        {
          contenu: 'une réponse',
          contenuMarkdown: 'une réponse',
          emetteur: 'systeme',
          references: [],
          idInteraction: 'id-interaction',
        },
        { contenu: 'une nouvelle question ?', emetteur: 'utilisateur' },
      ],
      derniereQuestion: 'une nouvelle question ?',
      idConversation: 'id-conversation',
    });
  });

  it('nettoie le dom du contenu reçu en réponse de l’API', async () => {
    clientAPI.publieMessageUtilisateurAPI = async () => ({
      reponse: 'une réponse',
      paragraphes: [],
      interaction_id: 'id-interaction',
      question: 'une question ?',
      conversation_id: 'id-conversation',
    });
    nettoyeurDOM.nettoie = (contenu) => Promise.resolve(`<div>${contenu}</div>`);

    await storeConversation.ajouteMessageUtilisateur(
      { question: 'une question ?' },
      async () => ({
        reponse: 'une réponse',
        paragraphes: [],
        interaction_id: 'id-interaction',
        question: 'une question ?',
        conversation_id: 'id-conversation',
      })
    );

    const conversation = get(storeConversation);
    expect(conversation.messages[1].contenu).toStrictEqual('<div>une réponse</div>');
    expect(conversation.messages[1].contenuMarkdown).toStrictEqual('une réponse');
  });

  it('transmet la question de l’utilisateur', async () => {
    let messageRecu = undefined;
    let promptDemande = false;
    clientAPI.publieMessageUtilisateurAPI = async (message, avecPromptSysteme) => {
      messageRecu = message;
      promptDemande = avecPromptSysteme;
      return {
        erreur: 'une erreur',
      };
    };
    storeConversation.initialise({
      messages: [],
      derniereQuestion: '',
      idConversation: 'id-conversation',
    });

    await storeConversation.ajouteMessageUtilisateur(
      { question: 'une question ?' },
      async (message, avecPrompt) => {
        messageRecu = message;
        promptDemande = avecPrompt;
        return {
          reponse: 'une réponse',
          paragraphes: [],
          interaction_id: 'id-interaction',
          question: 'une question ?',
          conversation_id: 'id-conversation',
        };
      }
    );

    expect(messageRecu).toStrictEqual({
      question: 'une question ?',
      conversation_id: 'id-conversation',
    });
    expect(promptDemande).toBe(false);
  });

  it('transmet la question de l’utilisateur avec le prompt', async () => {
    let messageRecu = undefined;
    let promptDemande = false;
    clientAPI.publieMessageUtilisateurAPI = async (message, avecPromptSysteme) => {
      messageRecu = message;
      promptDemande = avecPromptSysteme;
      return {
        erreur: 'une erreur',
      };
    };
    storeConversation.initialise({
      messages: [],
      derniereQuestion: '',
      idConversation: 'id-conversation',
    });

    await storeConversation.ajouteMessageUtilisateur(
      { question: 'une question ?', prompt: 'Le prompt' },
      async (message, avecPrompt) => {
        messageRecu = message;
        promptDemande = avecPrompt;
        return {
          reponse: 'une réponse',
          paragraphes: [],
          interaction_id: 'id-interaction',
          question: 'une question ?',
          conversation_id: 'id-conversation',
        };
      }
    );

    expect(messageRecu).toStrictEqual({
      question: 'une question ?',
      conversation_id: 'id-conversation',
      prompt: 'Le prompt',
    });
    expect(promptDemande).toBe(true);
  });

  describe('mets à jour le store affichage', () => {
    it('lorsqu’il y a une erreur', async () => {
      clientAPI.publieMessageUtilisateurAPI = async () => ({
        erreur: 'une erreur',
      });

      await storeConversation.ajouteMessageUtilisateur(
        { question: 'une question ?' },
        async () => ({
          reponse: 'une réponse',
          paragraphes: [],
          interaction_id: 'id-interaction',
          question: 'une question ?',
          conversation_id: 'id-conversation',
        })
      );

      expect(get(storeAffichage).aUneErreurAlbert).toBe(true);
    });

    it('lorsque l’erreur est corrigée', async () => {
      storeAffichage.erreurAlbert(true);
      clientAPI.publieMessageUtilisateurAPI = async () => ({
        reponse: 'une réponse',
        paragraphes: [],
        interaction_id: 'id-interaction',
        question: 'une question ?',
        conversation_id: 'id-conversation',
      });

      await storeConversation.ajouteMessageUtilisateur(
        { question: 'une question ?' },
        async () => ({
          reponse: 'une réponse',
          paragraphes: [],
          interaction_id: 'id-interaction',
          question: 'une question ?',
          conversation_id: 'id-conversation',
        })
      );

      expect(get(storeAffichage).aUneErreurAlbert).toBe(false);
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
