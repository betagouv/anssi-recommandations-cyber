import { writable } from "svelte/store";
import DOMPurify from "dompurify";
import { marked } from "marked";

export type Paragraphe = {
  score_similarite: number;
  numero_page: number;
  url: string;
  nom_document: string;
  contenu: string;
};

export type Message = {
  contenu: string;
  emetteur: "utilisateur" | "systeme";
  references?: Paragraphe[];
  idInteraction?: string;
};

export type MessageUtilisateur = Message & {
  emetteur: "utilisateur";
};

export type MessageSysteme = Message & {
  emetteur: "systeme";
  contenuMarkdown: string;
};

export type Conversation = {
  messages: Message[];
  derniereQuestion: string;
};

const { subscribe, update } = writable<Conversation>({
  messages: [],
  derniereQuestion: "",
});
export const nettoyeurDOM = {
  nettoie: async (contenu: string): Promise<string> =>
    DOMPurify.sanitize(await marked.parse(contenu)),
};

export const storeConversation = {
  ajouteMessageUtilisateur: (question: string) => {
    update((conversation) => {
      return {
        ...conversation,
        messages: [
          ...conversation.messages,
          {
            contenu: question,
            emetteur: "utilisateur",
          },
        ],
        derniereQuestion: question,
      };
    });
  },
  ajouteMessageSysteme: async (
    reponse: string,
    references: Paragraphe[],
    idInteraction: string,
  ) => {
    const contenuHTML = await nettoyeurDOM.nettoie(reponse);
    update((conversation) => {
      return {
        ...conversation,
        messages: [
          ...conversation.messages,
          {
            contenu: contenuHTML,
            contenuMarkdown: reponse,
            emetteur: "systeme",
            references,
            idInteraction,
          },
        ],
      };
    });
  },
  subscribe,
};
