import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import {
  nettoyeurDOM,
  storeConversation,
} from '../../src/stores/conversation.store';
import { clientAPI, estReponseConversation } from '../../src/client.api';
import { get } from 'svelte/store';
import { storeAffichage } from '../../src/stores/affichage.store';

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

  it('crée une conversation', async () => {
    clientAPI.creeUneConversation = async () => ({
      reponse: 'une réponse',
      paragraphes: [],
      id_interaction: 'id-interaction',
      question: 'une question ?',
      id_conversation: 'id-conversation',
    });
    await storeConversation.ajouteMessageUtilisateur({ question: 'une question ?' });

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

  it('nettoie le dom du contenu reçu en réponse de l’API', async () => {
    clientAPI.creeUneConversation = async () => ({
      reponse: 'une réponse',
      paragraphes: [],
      id_interaction: 'id-interaction',
      question: 'une question ?',
      id_conversation: 'id-conversation',
    });
    nettoyeurDOM.nettoie = (contenu) => Promise.resolve(`<div>${contenu}</div>`);

    await storeConversation.ajouteMessageUtilisateur({ question: 'une question ?' });

    const conversation = get(storeConversation);
    expect(conversation.messages[1].contenu).toStrictEqual('<div>une réponse</div>');
    expect(conversation.messages[1].contenuMarkdown).toStrictEqual('une réponse');
  });

  it('transmet la question de l’utilisateur lors de la création d’une conversation', async () => {
    let messageRecu = undefined;
    clientAPI.creeUneConversation = async (message) => {
      messageRecu = message;
      return {
        erreur: 'une erreur',
      };
    };
    storeConversation.initialise({
      messages: [],
      derniereQuestion: '',
      idConversation: null,
    });

    await storeConversation.ajouteMessageUtilisateur({ question: 'une question ?' });

    expect(messageRecu).toStrictEqual({
      question: 'une question ?',
      id_conversation: null,
    });
  });

  it('transmet la question de l’utilisateur lors de l’ajout d’une interaction à une conversation', async () => {
    let messageRecu = undefined;
    let idConversationRecu = undefined;
    clientAPI.ajouteInteraction = async (idConversation, message) => {
      idConversationRecu = idConversation;
      messageRecu = message;
      return {
        reponse: 'Une réponse',
        question: 'Une question',
        paragraphes: [],
        id_interaction: 'id-interaction',
      };
    };
    storeConversation.initialise({
      messages: [
        {
          contenu: 'Un contenu',
          emetteur: 'utilisateur',
        },
      ],
      derniereQuestion: 'La dernière question',
      idConversation: 'id-conversation',
    });

    await storeConversation.ajouteMessageUtilisateur({ question: 'une question ?' });

    expect(messageRecu).toStrictEqual({
      question: 'une question ?',
    });
    expect(idConversationRecu).toBe('id-conversation');
  });

  it('conserve une sauvegarde de la conversation en cas d’échec lors de l’appel à l’API', async () => {
    clientAPI.ajouteInteraction = async () => ({
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

    await storeConversation.ajouteMessageUtilisateur({
      question: 'une nouvelle question ?',
    });

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

  it('ne mets pas à jour l’id de conversation lors de l’ajout d’une interaction', async () => {
    clientAPI.ajouteInteraction = async () => ({
      reponse: 'Une réponse',
      question: 'Une question',
      paragraphes: [],
      id_interaction: 'id-interaction',
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

    await storeConversation.ajouteMessageUtilisateur({
      question: 'une nouvelle question ?',
    });

    const storeConversationMisAJour = get(storeConversation);
    expect(storeConversationMisAJour.idConversation).toStrictEqual(
      'id-conversation'
    );
  });

  it('mets pas à jour l’id d’interaction lors de l’ajout d’une interaction', async () => {
    clientAPI.ajouteInteraction = async () => ({
      reponse: 'Une réponse',
      question: 'Une question',
      paragraphes: [],
      id_interaction: 'id-interaction-2',
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

    await storeConversation.ajouteMessageUtilisateur({
      question: 'une nouvelle question ?',
    });

    const storeConversationMisAJour = get(storeConversation);
    expect(storeConversationMisAJour.messages[3].idInteraction).toStrictEqual(
      'id-interaction-2'
    );
  });

  describe('met à jour le store affichage', () => {
    it('lorsqu’il y a une erreur', async () => {
      clientAPI.creeUneConversation = async () => ({
        erreur: 'une erreur',
      });

      await storeConversation.ajouteMessageUtilisateur({
        question: 'une question ?',
      });

      expect(get(storeAffichage).aUneErreurAlbert).toBe(true);
    });

    it('lorsque l’erreur est corrigée', async () => {
      storeAffichage.erreurAlbert(true);
      clientAPI.creeUneConversation = async () => ({
        reponse: 'une réponse',
        paragraphes: [],
        id_interaction: 'id-interaction',
        question: 'une question ?',
        id_conversation: 'id-conversation',
      });

      await storeConversation.ajouteMessageUtilisateur({
        question: 'une question ?',
      });

      expect(get(storeAffichage).aUneErreurAlbert).toBe(false);
    });
  });
});

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
