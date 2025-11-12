const urlAPI = import.meta.env.VITE_URL_API;

export const soumetsAvisUtilisateurAPI = async (
  idInteraction: string,
  positif: boolean,
  commentaire?: string,
  tags?: string[],
) =>
  await fetch(`${urlAPI}/api/retour`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id_interaction: idInteraction,
      retour: {
        type: positif ? "positif" : "negatif",
        ...(commentaire ? { commentaire } : {}),
        ...(tags ? { tags } : {}),
      },
    }),
  });

export const supprimeAvisUtilisateurAPI = async (idInteraction: string) =>
  await fetch(`${urlAPI}/api/retour/${idInteraction}`, {
    method: "DELETE",
  });

type MessageUtilisateurAPI = {
  question: string;
  prompt?: string;
};

export const publieMessageUtilisateurAPI = async (
  message: MessageUtilisateurAPI,
  avecPromptSysteme: boolean,
) => {
  const endpoint = avecPromptSysteme
    ? `${urlAPI}/api/pose_question_avec_prompt`
    : `${urlAPI}/api/pose_question`;

  const reponse = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(message),
  });
  return await reponse.json();
};
