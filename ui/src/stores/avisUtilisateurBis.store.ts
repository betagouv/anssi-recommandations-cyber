import { writable } from 'svelte/store';

type ValeurExactitude = 'Très bonne' | 'Bonne' | 'Correcte' | 'Fausse';
type ValeurCompletude = Omit<ValeurExactitude, 'Fausse'> | 'Mauvaise';

type AvisUtilisateurBis = {
  exactitude: { valeur: ValeurExactitude; commentaire?: string };
  completude: { valeur: ValeurCompletude; commentaire?: string };
  idConversation: string;
  idInteraction: string;
};

const { subscribe, set, update } = writable<AvisUtilisateurBis>({
  exactitude: { valeur: 'Bonne' },
  completude: { valeur: 'Bonne' },
  idConversation: '',
  idInteraction: '',
});

const modifieLaValeurDeLExactitude = (valeur: ValeurExactitude) => {
  update((avisActuel: AvisUtilisateurBis) => ({
    ...avisActuel,
    exactitude: { valeur },
  }));
};

const commenteLExactitude = (commentaire: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur === 'Fausse') return avisActuel;
    return {
      ...avisActuel,
      exactitude: { ...avisActuel.exactitude, commentaire },
    };
  });
};

const modifieLaValeurDeLaCompletude = (valeur: ValeurCompletude) => {
  update((avisActuel: AvisUtilisateurBis) => ({
    ...avisActuel,
    completude: { valeur },
  }));
};

const commenteLaCompletude = (commentaire: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur === 'Mauvaise') return avisActuel;
    return {
      ...avisActuel,
      completude: { ...avisActuel.completude, commentaire },
    };
  });
};

export const storeAvisUtilisateurBis = {
  subscribe,
  initialise: set,
  modifieLaValeurDeLExactitude,
  commenteLExactitude,
  modifieLaValeurDeLaCompletude,
  commenteLaCompletude,
};
