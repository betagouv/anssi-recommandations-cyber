import type {
  AvisUtilisateurBis,
  ValeurPertinence,
  ValeurSourcesAdaptees,
} from './stores/avisUtilisateurBis.store';

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
  idConversation: string,
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
      id_conversation: idConversation,
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
};

export type ReponseParagraphe = {
  numero_page: number;
  url: string;
  nom_document: string;
  contenu: string;
  image?: Blob;
  titre: string;
  date_mise_a_jour: string;
};

export type ReponseCreationConversation = {
  reponse: string;
  paragraphes: ReponseParagraphe[];
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
  const endpoint = '/api/conversation/';

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

const soumetsAvisUtilisateurBisAPI = async (avis: AvisUtilisateurBis) => {
  const mapValeursPertinence: Map<ValeurPertinence, string> = new Map([
    ['Très pertinente', 'très pertinente'],
    ['Pertinente', 'pertinente'],
    ['Correcte', 'correcte'],
    ['Erronée', 'erronée'],
  ]);

  const mappeValeursSourcesAdaptees: Map<ValeurSourcesAdaptees, string> = new Map([
    ['Oui, tout à fait', 'oui, tout à fait'],
    ['Oui, partiellement', 'oui, partiellement'],
    ['Non', 'non'],
  ]);

  const payload = {
    id_interaction: avis.idInteraction,
    id_conversation: avis.idConversation,
    avis: {
      pertinence: {
        valeur: mapValeursPertinence.get(avis.pertinence.valeur),
        ...(avis.pertinence.commentaire && {
          commentaire: avis.pertinence.commentaire,
        }),
        ...(avis.pertinence.valeur === 'Erronée' && {
          informations_erronees: avis.pertinence.precisionsInformationsErronees,
        }),
      },
      sources_adaptees: {
        valeur: mappeValeursSourcesAdaptees.get(avis.sourcesAdaptees.valeur),
        ...(avis.sourcesAdaptees.commentaire && {
          commentaire: avis.sourcesAdaptees.commentaire,
        }),
        ...(avis.sourcesAdaptees.valeur === 'Non' && {
          liste: avis.sourcesAdaptees.liste,
        }),
        ...(avis.sourcesAdaptees.raisons &&
          avis.sourcesAdaptees.raisons?.length > 0 && {
            raisons: avis.sourcesAdaptees.raisons,
          }),
      },
    },
  };
  const reponse = await fetch('/api/avis', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  const reponseJson = await reponse.json();
  if (!reponse.ok) {
    throw new Error(reponseJson.detail.message);
  }
  return reponseJson;
};

type ClientAPI = {
  creeUneConversation: (
    message: MessageUtilisateurAPI
  ) => Promise<ReponseCreationConversation | ReponseEnErreur>;
  ajouteInteraction: (
    idConversation: string,
    message: MessageUtilisateurAPI
  ) => Promise<ReponseAjoutInteraction | ReponseEnErreur>;
  soumetsAvisUtilisateurBisAPI: (
    avis: AvisUtilisateurBis
  ) => Promise<Response | ReponseEnErreur>;
};

export const clientAPI: ClientAPI = {
  creeUneConversation,
  ajouteInteraction,
  soumetsAvisUtilisateurBisAPI,
};
