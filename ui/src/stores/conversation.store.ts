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

const { subscribe, update } = writable<Message[]>([]);

export const storeConversation = {
  ajouteMessageUtilisateur: (question: string) => {
    update((messages) => {
      return [
        ...messages,
        {
          contenu: question,
          emetteur: "utilisateur",
        },
      ];
    });
  },
  ajouteMessageSysteme: async (
    reponse: string,
    references: Paragraphe[],
    idInteraction: string,
  ) => {
    const contenuHTML = DOMPurify.sanitize(await marked.parse(reponse));
    update((messages) => {
      return [
        ...messages,
        {
          contenu: contenuHTML,
          contenuMarkdown: reponse,
          emetteur: "systeme",
          references,
          idInteraction,
        },
      ];
    });
  },
  subscribe,
};
