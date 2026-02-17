import type { Paragraphe } from './stores/conversation.store';

const urlAPI = import.meta.env.VITE_URL_API;

const forgeURLAvecTypeUtilisateur = (chemin: string): string => {
  const urlParams = new URLSearchParams(window.location.search);
  const a_type_utilisateur = urlParams.has('type_utilisateur');

  if (a_type_utilisateur) {
    return new URL(
      `${chemin}?type_utilisateur=${urlParams.get('type_utilisateur')}`,
      urlAPI
    ).toString();
  }
  return new URL(`${chemin}`, urlAPI).toString();
};

export const soumetsAvisUtilisateurAPI = async (
  idInteraction: string,
  positif: boolean,
  commentaire?: string,
  tags?: string[]
) =>
  await fetch(forgeURLAvecTypeUtilisateur('/api/retour'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      id_interaction: idInteraction,
      retour: {
        type: positif ? 'positif' : 'negatif',
        ...(commentaire ? { commentaire } : {}),
        ...(tags ? { tags } : {}),
      },
    }),
  });

export const supprimeAvisUtilisateurAPI = async (idInteraction: string) =>
  await fetch(forgeURLAvecTypeUtilisateur(`/api/retour/${idInteraction}`), {
    method: 'DELETE',
  });

export type MessageUtilisateurAPI = {
  question: string;
  id_conversation?: string | null;
};

export type ReponseCreationConversation = {
  reponse: string;
  paragraphes: Paragraphe[];
  id_interaction: string;
  question: string;
  id_conversation: string;
};

export type ReponseAjoutInteraction = Omit<
  ReponseCreationConversation,
  'id_conversation'
>;

export type ReponseEnErreur = {
  erreur: string;
};

const creeUneConversation = async (
  message: MessageUtilisateurAPI
): Promise<ReponseCreationConversation | ReponseEnErreur> => {
  const endpoint = '/api/conversation';

  const reponse = await fetch(forgeURLAvecTypeUtilisateur(endpoint), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
  });
  const reponseJson = await reponse.json();
  if (!reponse.ok) {
    return {
      erreur: reponseJson.detail.message,
    };
  }
  return reponseJson;
};

const ajouteInteraction = async (
  idConversation: string,
  message: MessageUtilisateurAPI
) => {
  const endpoint = `/api/conversation/${idConversation}`;

  const reponse = await fetch(forgeURLAvecTypeUtilisateur(endpoint), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
  });
  const reponseJson = await reponse.json();
  if (!reponse.ok) {
    return {
      erreur: reponseJson.detail.message,
    };
  }
  return reponseJson;
};

export const estReponseConversation = (
  reponse: ReponseCreationConversation | ReponseAjoutInteraction | ReponseEnErreur
): reponse is ReponseCreationConversation | ReponseAjoutInteraction => {
  return (
    'reponse' in reponse && 'paragraphes' in reponse && 'id_interaction' in reponse
  );
};

export const estReponseCreationConversation = (
  reponse: ReponseCreationConversation | ReponseAjoutInteraction
): reponse is ReponseCreationConversation => {
  return (
    'reponse' in reponse &&
    'paragraphes' in reponse &&
    'id_interaction' in reponse &&
    'id_conversation' in reponse
  );
};

type ClientAPI = {
  creeUneConversation: (
    message: MessageUtilisateurAPI
  ) => Promise<ReponseCreationConversation | ReponseEnErreur>;
  ajouteInteraction: (
    idConversation: string,
    message: MessageUtilisateurAPI
  ) => Promise<ReponseAjoutInteraction | ReponseEnErreur>;
};

export const clientAPI: ClientAPI = {
  creeUneConversation,
  ajouteInteraction,
};
