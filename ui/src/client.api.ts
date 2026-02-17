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
  conversation_id?: string | null;
};

export type ReponseMessageUtilisateurAPI = {
  reponse: string;
  paragraphes: Paragraphe[];
  interaction_id: string;
  question: string;
  conversation_id: string;
};

export type ReponseEnErreur = {
  erreur: string;
};

const publieMessageUtilisateurAPI = async (
  message: MessageUtilisateurAPI
): Promise<ReponseMessageUtilisateurAPI | ReponseEnErreur> => {
  const endpoint = '/api/pose_question';

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

export const estReponseMessageUtilisateur = (
  reponse: ReponseMessageUtilisateurAPI | ReponseEnErreur
): reponse is ReponseMessageUtilisateurAPI => {
  return (
    'reponse' in reponse &&
    'paragraphes' in reponse &&
    'interaction_id' in reponse &&
    'conversation_id' in reponse
  );
};

type ClientAPI = {
  publieMessageUtilisateurAPI: (
    message: MessageUtilisateurAPI
  ) => Promise<ReponseMessageUtilisateurAPI | ReponseEnErreur>;
};

export const clientAPI: ClientAPI = {
  publieMessageUtilisateurAPI,
};
