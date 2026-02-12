import { get, writable } from 'svelte/store';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import {
  clientAPI,
  estReponseMessageUtilisateur,
  type ReponseMessageUtilisateurAPI,
} from '../client.api';
import { storeAffichage } from './affichage.store';

export type Paragraphe = {
  score_similarite: number;
  numero_page: number;
  url: string;
  nom_document: string;
  contenu: string;
};

export type Message = {
  contenu: string;
  contenuMarkdown?: string;
  emetteur: 'utilisateur' | 'systeme';
  references?: Paragraphe[];
  idInteraction?: string;
};

export type MessageUtilisateur = Message & {
  emetteur: 'utilisateur';
};

export type MessageSysteme = Message & {
  emetteur: 'systeme';
  contenuMarkdown: string;
};

export type Conversation = {
  messages: Message[];
  derniereQuestion: string;
  idConversation: string | null;
};

const { subscribe, update, set } = writable<Conversation>({
  messages: [],
  derniereQuestion: '',
  idConversation: null,
});
export const nettoyeurDOM = {
  nettoie: async (contenu: string): Promise<string> =>
    DOMPurify.sanitize(await marked.parse(contenu)),
};

type QuestionUtilisateur = {
  question: string;
  prompt?: string;
};

const ajouteMessageUtilisateur = async (question: QuestionUtilisateur) => {
  const sauvegarde = get(storeConversation);
  const questionUtilisateur: MessageUtilisateur = {
    contenu: question.question,
    emetteur: 'utilisateur',
  };
  storeAffichage.estEnAttenteDeReponse(true);
  const reponseAPI = await clientAPI.publieMessageUtilisateurAPI(
    {
      question: question.question,
      conversation_id: sauvegarde.idConversation,
      ...(question.prompt && { prompt: question.prompt }),
    },
    question.prompt !== undefined
  );
  const { estEnErreur, contenuHTML } = estReponseMessageUtilisateur(reponseAPI)
    ? {
        estEnErreur: false,
        contenuHTML: await nettoyeurDOM.nettoie(reponseAPI.reponse),
      }
    : { estEnErreur: true, contenuHTML: reponseAPI.erreur };
  update((conversation) => {
    storeAffichage.estEnAttenteDeReponse(false);
    if (estEnErreur) {
      storeAffichage.erreurAlbert(true);
      return {
        ...sauvegarde,
        messages: [...conversation.messages, questionUtilisateur],
        derniereQuestion: question.question,
      };
    } else {
      storeAffichage.erreurAlbert(false);
      const reponse = reponseAPI as ReponseMessageUtilisateurAPI;
      return {
        ...conversation,
        messages: [
          ...conversation.messages,
          questionUtilisateur,
          {
            contenu: contenuHTML,
            contenuMarkdown: reponse.reponse,
            emetteur: 'systeme',
            references: reponse.paragraphes,
            idInteraction: reponse.interaction_id,
          },
        ],
        idConversation: reponse.conversation_id,
        derniereQuestion: question.question,
      };
    }
  });
};

export const storeConversation = {
  ajouteMessageUtilisateur,
  subscribe,
  initialise: set,
};
