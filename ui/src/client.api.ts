const urlAPI = import.meta.env.VITE_URL_API;

export const soumetsAvisUtilisateurAPI = async (
  idInteraction: string,
  positif: boolean,
  commentaire?: string,
) =>
  await fetch(`${urlAPI}/api/retour`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      id_interaction_rattachee: idInteraction,
      retour: {
        type: positif ? "positif" : "negatif",
        ...(commentaire ? { commentaire } : {}),
      },
    }),
  });
