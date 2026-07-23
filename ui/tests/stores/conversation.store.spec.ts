import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import {
  nettoyeurDOM,
  storeConversation,
} from '../../src/stores/conversation.store';
import { clientAPI } from '../../src/client.api';
import { get } from 'svelte/store';
import { storeAffichage } from '../../src/stores/affichage.store';
import { unConstructeurParagraphe } from './constructeurDeParagraphe';
import { adaptateurPDF } from '../../src/pdf/adaptateurPDF';
import { InvalidPDFException } from 'pdfjs-dist';

describe('le store de conversation', () => {
  beforeEach(() => {
    nettoyeurDOM.nettoie = async (contenu: string) => contenu;
    adaptateurPDF.pagePDFenPNG = () => Promise.resolve(new Blob());
  });

  afterEach(() => {
    storeConversation.initialise({
      messages: [],
      derniereQuestion: '',
      idConversation: '',
    });
  });

  it('renvoie une conversation en édition vide', () => {
    const conversation = get(storeConversation);

    expect(conversation).toStrictEqual({
      messages: [],
      derniereQuestion: '',
      idConversation: '',
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
      idConversation: '',
    });

    await storeConversation.ajouteMessageUtilisateur({ question: 'une question ?' });

    expect(messageRecu).toStrictEqual({
      question: 'une question ?',
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

  describe('pour la génération des PDF', () => {
    it('continue la génération en cas d’erreur', async () => {
      let nombreAppel = 0;
      adaptateurPDF.pagePDFenPNG = () => {
        nombreAppel++;
        if (nombreAppel === 3) {
          throw new InvalidPDFException('PDF en erreur');
        }
        return Promise.resolve(new Blob());
      };
      clientAPI.ajouteInteraction = async () => ({
        reponse: 'Une réponse',
        question: 'Une question',
        paragraphes: [
          unConstructeurParagraphe().construis(),
          unConstructeurParagraphe().construis(),
          unConstructeurParagraphe().construis(),
          unConstructeurParagraphe().construis(),
        ],
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
        question: 'Une question ?',
      });

      const storeMisAJour = get(storeConversation);
      const paragraphes = storeMisAJour.messages[3].references;
      expect(paragraphes).toBeDefined();
      expect(paragraphes!.every((p) => p.image !== undefined)).toBe(true);
      expect(paragraphes).toHaveLength(4);
    });

    it('remplace correctement l‘url du document source', async () => {
      const urlAppelees: string[] = [];
      adaptateurPDF.pagePDFenPNG = (url: string) => {
        urlAppelees.push(url);
        return Promise.resolve(new Blob());
      };
      clientAPI.ajouteInteraction = async () => ({
        reponse: 'Une réponse',
        question: 'Une question',
        paragraphes: [
          unConstructeurParagraphe()
            .avecURLDocument('http://demo.local/source/?document=mon-doc-1.pdf')
            .construis(),
          unConstructeurParagraphe()
            .avecURLDocument('http://demo.local/source?document=mon-doc-2.pdf')
            .construis(),
        ],
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
        question: 'Une question ?',
      });

      expect(urlAppelees[0]).toEqual(
        'http://demo.local/source/proxy?document=mon-doc-1.pdf'
      );
      expect(urlAppelees[1]).toEqual(
        'http://demo.local/source/proxy?document=mon-doc-2.pdf'
      );
    });
  });
});
