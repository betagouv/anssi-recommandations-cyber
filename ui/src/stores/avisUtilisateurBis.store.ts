import { get, writable } from 'svelte/store';

export type ValeurExactitude = 'Très bonne' | 'Bonne' | 'Correcte' | 'Fausse';
export type ValeurCompletude = Omit<ValeurExactitude, 'Fausse'> | 'Mauvaise';

export type Exactitude = {
  valeur: ValeurExactitude;
  commentaire?: string;
  precisionsInformationsErronees?: string;
  sourcesAdaptees?: string;
};
export type Completude = {
  valeur: ValeurCompletude;
  commentaire?: string;
  informationsManquantes?: string;
  sourcesAdaptees?: string;
};
type AvisUtilisateurBis = {
  exactitude: Exactitude;
  completude: Completude;
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
  const exactitudeEtCompletudeAvecOuSansCommentaire =
    avisUtilisateurBis.exactitude.valeur !== 'Fausse' &&
    avisUtilisateurBis.completude.valeur !== 'Mauvaise';
  const exactitudeAvecInformationsErroneesEtSourcesAdaptees =
    avisUtilisateurBis.exactitude.valeur === 'Fausse' &&
    avisUtilisateurBis.exactitude.precisionsInformationsErronees !== undefined &&
    avisUtilisateurBis.exactitude.precisionsInformationsErronees.trim() !== '' &&
    avisUtilisateurBis.exactitude.sourcesAdaptees !== undefined &&
    avisUtilisateurBis.exactitude.sourcesAdaptees.trim() !== '';
  const completudeAvecInformationsManquantesEtSourcesAdaptees =
    avisUtilisateurBis.completude.valeur === 'Mauvaise' &&
    avisUtilisateurBis.completude.informationsManquantes !== undefined &&
    avisUtilisateurBis.completude.informationsManquantes.trim() !== '' &&
    avisUtilisateurBis.completude.sourcesAdaptees !== undefined &&
    avisUtilisateurBis.completude.sourcesAdaptees?.trim() !== '';
  return (
    exactitudeEtCompletudeAvecOuSansCommentaire ||
    exactitudeAvecInformationsErroneesEtSourcesAdaptees ||
    completudeAvecInformationsManquantesEtSourcesAdaptees
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
