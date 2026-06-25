import { get, writable } from 'svelte/store';

export type ValeurExactitude = 'Très bonne' | 'Bonne' | 'Correcte' | 'Fausse';
export type ValeurCompletude = Omit<ValeurExactitude, 'Fausse'> | 'Mauvaise';

type AvisUtilisateurBis = {
  exactitude: {
    valeur: ValeurExactitude;
    commentaire?: string;
    precisionsInformationsErronees?: string;
    sourcesAdaptees?: string;
  };
  completude: {
    valeur: ValeurCompletude;
    commentaire?: string;
    informationsManquantes?: string;
    sourcesAdaptees?: string;
  };
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

const preciseLesInformationsErronees = (precisions: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur !== 'Fausse') return avisActuel;
    return {
      ...avisActuel,
      exactitude: {
        ...avisActuel.exactitude,
        precisionsInformationsErronees: precisions,
      },
    };
  });
};

const indiqueLesSourcesAdapteesPourLExactitude = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.exactitude.valeur !== 'Fausse') return avisActuel;
    return {
      ...avisActuel,
      exactitude: {
        ...avisActuel.exactitude,
        sourcesAdaptees: sourcesAdaptees,
      },
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

const preciseLesInformationsManquantes = (informationsManquantes: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur !== 'Mauvaise') return avisActuel;
    return {
      ...avisActuel,
      completude: {
        ...avisActuel.completude,
        informationsManquantes: informationsManquantes,
      },
    };
  });
};

const indiqueLesSourcesAdapteesPourLaCompletude = (sourcesAdaptees: string) => {
  update((avisActuel: AvisUtilisateurBis) => {
    if (avisActuel.completude.valeur !== 'Mauvaise') return avisActuel;
    return {
      ...avisActuel,
      completude: {
        ...avisActuel.completude,
        sourcesAdaptees: sourcesAdaptees,
      },
    };
  });
};

const estValide = (): boolean => {
  const avisUtilisateurBis = get(storeAvisUtilisateurBis);
  return (
    avisUtilisateurBis.exactitude.valeur !== 'Fausse' &&
    avisUtilisateurBis.completude.valeur !== 'Mauvaise'
  );
};

export const storeAvisUtilisateurBis = {
  subscribe,
  initialise: set,
  modifieLaValeurDeLExactitude,
  modifieLaValeurDeLaCompletude,
  commenteLExactitude,
  commenteLaCompletude,
  preciseLesInformationsErronees,
  indiqueLesSourcesAdapteesPourLExactitude,
  preciseLesInformationsManquantes,
  indiqueLesSourcesAdapteesPourLaCompletude,
  estValide,
};
