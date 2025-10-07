import { writable } from "svelte/store";

export type AvisUtilisateur = {
  positif: boolean;
};

const { subscribe, update } = writable<Record<string, AvisUtilisateur>>({});

export const storeAvisUtilisateur = {
  ajouteAvis: (idInteraction: string, avis: AvisUtilisateur) => {
    update((avisActuel) => ({ ...avisActuel, [idInteraction]: avis }));
  },
  subscribe,
};
