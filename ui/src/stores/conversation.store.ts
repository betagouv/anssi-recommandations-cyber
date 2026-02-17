import { get, writable } from 'svelte/store';
import DOMPurify from 'dompurify';
import { marked } from 'marked';
import {
  clientAPI,
  estReponseConversation,
  estReponseCreationConversation,
  type ReponseEnErreur,
  type ReponseAjoutInteraction,
  type ReponseCreationConversation,
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
};

const ajouteMessageUtilisateur = async (question: QuestionUtilisateur) => {
  const sauvegarde = get(storeConversation);
  const questionUtilisateur: MessageUtilisateur = {
    contenu: question.question,
    emetteur: 'utilisateur',
  };
  storeAffichage.estEnAttenteDeReponse(true);
  let reponseAPI:
    | ReponseCreationConversation
    | ReponseAjoutInteraction
    | ReponseEnErreur;
  if (sauvegarde.idConversation === null) {
    reponseAPI = await clientAPI.creeUneConversation({
      question: question.question,
      id_conversation: sauvegarde.idConversation,
    });
  } else {
    reponseAPI = await clientAPI.ajouteInteraction(sauvegarde.idConversation, {
      question: question.question,
    });
  }
  const contenuHTML = estReponseConversation(reponseAPI)
    ? await nettoyeurDOM.nettoie(reponseAPI.reponse)
    : reponseAPI.erreur;
  update((conversation) => {
    storeAffichage.estEnAttenteDeReponse(false);
    if (!estReponseConversation(reponseAPI)) {
      storeAffichage.erreurAlbert(true);
      return {
        ...sauvegarde,
        messages: [...conversation.messages, questionUtilisateur],
        derniereQuestion: question.question,
      };
    } else {
      storeAffichage.erreurAlbert(false);
      const reponse = reponseAPI;
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
            idInteraction: reponse.id_interaction,
          },
        ],
        ...(estReponseCreationConversation(reponse) && {
          idConversation: reponse.id_conversation,
        }),
        derniereQuestion: question.question,
      };
    }
  });
};

const questionEnAttenteDeReponse = (question: string) => {
  update((conversation) => ({ ...conversation, derniereQuestion: question }));
};

export const storeConversation = {
  ajouteMessageUtilisateur,
  initialise: set,
  questionEnAttenteDeReponse,
  subscribe,
};
